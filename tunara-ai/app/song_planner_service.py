import json
import os
from typing import Any

import httpx

from .song_plan_models import SongPlan, SongPlanRequest


class SongPlannerService:
    def __init__(self) -> None:
        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434",
        ).rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.timeout = float(os.getenv("SONG_PLANNER_TIMEOUT_SECONDS", "30"))
        self.maximum_output_tokens = int(
            os.getenv("SONG_PLANNER_MAX_TOKENS", "500")
        )

    async def create_plan(self, request: SongPlanRequest) -> SongPlan:
        for attempt in range(1):
            try:
                generated = await self._request_ollama(request, attempt)
                return SongPlan.model_validate(json.loads(generated))
            except (json.JSONDecodeError, ValueError):
                continue
            except httpx.TimeoutException:
                break
            except httpx.HTTPError:
                break

        return self._fallback_plan(request)

    async def _request_ollama(
        self,
        request: SongPlanRequest,
        attempt: int,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": self._prompt(request, attempt),
            "stream": False,
            "format": SongPlan.model_json_schema(),
            "options": {
                "temperature": 0.1 if attempt else 0.2,
                "top_p": 0.75,
                "num_predict": self.maximum_output_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        generated = str(body.get("response", "")).strip()
        if not generated:
            raise ValueError("Ollama returned an empty plan")
        return generated

    def _prompt(self, request: SongPlanRequest, attempt: int) -> str:
        retry_instruction = (
            "The previous response was invalid. Keep the object minimal and "
            "follow every schema field exactly. "
            if attempt
            else ""
        )
        return f"""
{retry_instruction}Create a compact arrangement plan for one original song.
Do not generate MIDI notes. Do not repeat the lyrics.

Idea: {request.prompt}
Genre: {request.genre}
Language: {request.language}
Target duration: {request.target_duration_seconds} seconds

Requirements:
- Use 4/4 time.
- Select one practical BPM and one major or minor key.
- Include Verse 1 and Chorus.
- Use 4 to 6 short sections.
- Use 2 to 4 conventional chord symbols per section.
- Make the chorus higher and more energetic than the verse.
- Keep melodic, drum, and bass descriptions under 12 words each.
- Return only the JSON object required by the schema.
""".strip()

    def _fallback_plan(self, request: SongPlanRequest) -> SongPlan:
        genre = request.genre.strip().lower()
        profiles = {
            "pop": (112, "C major", ["Am", "F", "C", "G"]),
            "rock": (124, "A minor", ["Am", "F", "C", "G"]),
            "edm": (128, "A minor", ["Am", "F", "C", "G"]),
            "hip hop": (92, "D minor", ["Dm", "Bb", "F", "C"]),
            "country": (104, "G major", ["G", "C", "Em", "D"]),
            "cinematic": (84, "D minor", ["Dm", "Bb", "F", "C"]),
        }
        bpm, key, chords = profiles.get(
            genre,
            profiles["pop"],
        )
        title = self._title_from_prompt(request.prompt)
        sections = [
            {
                "name": "Verse 1",
                "bars": 8,
                "chords": chords,
                "energy": "medium",
                "vocal_register": "middle",
                "rhythm_density": "sparse",
            },
            {
                "name": "Chorus",
                "bars": 8,
                "chords": [chords[1], chords[3], chords[0], chords[2]],
                "energy": "high",
                "vocal_register": "high",
                "rhythm_density": "balanced",
            },
            {
                "name": "Verse 2",
                "bars": 8,
                "chords": chords,
                "energy": "medium",
                "vocal_register": "middle",
                "rhythm_density": "sparse",
            },
            {
                "name": "Final Chorus",
                "bars": 8,
                "chords": [chords[1], chords[3], chords[0], chords[2]],
                "energy": "high",
                "vocal_register": "high",
                "rhythm_density": "balanced",
            },
        ]
        return SongPlan.model_validate(
            {
                "title": title,
                "language": request.language,
                "genre": request.genre,
                "bpm": bpm,
                "key": key,
                "time_signature": "4/4",
                "melodic_character": "Memorable stepwise phrases with a lifted chorus",
                "drum_character": "Steady groove with stronger chorus accents",
                "bass_character": "Root-driven bass with simple rhythmic movement",
                "sections": sections,
            }
        )

    def _title_from_prompt(self, prompt: str) -> str:
        words = [word.strip(".,;:!?¡¿") for word in prompt.split()]
        usable = [word for word in words if word]
        return " ".join(usable[:5])[:255] or "Tunara Song"
