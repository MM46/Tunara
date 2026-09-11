import json
import re
from typing import Any

from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest


LYRICS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "A short original song title",
        },
        "lyrics": {
            "type": "string",
            "description": "Complete original lyrics with section labels",
        },
    },
    "required": ["title", "lyrics"],
    "additionalProperties": False,
}


class LyricsService:
    def __init__(self, ollama_client: OllamaClient) -> None:
        self.ollama_client = ollama_client

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> tuple[str, str]:
        prompt = self._build_prompt(request)
        raw_response = await self.ollama_client.generate(
            prompt,
            response_schema=LYRICS_SCHEMA,
        )

        try:
            return self._parse_response(raw_response)
        except RuntimeError:
            retry_response = await self.ollama_client.generate(
                self._build_retry_prompt(request, raw_response),
                response_schema=LYRICS_SCHEMA,
            )
            return self._parse_response(retry_response)

    def _build_prompt(self, request: GenerateSongRequest) -> str:
        return f"""
Create a fully original song.

Idea: {request.prompt}
Genre: {request.genre}
Language: {request.language}
Voice style: {request.voice}
Target duration: {request.duration_seconds} seconds

Requirements:
- Return an original, memorable title.
- Return complete original lyrics in the requested language.
- Match the requested genre.
- Use section labels such as [Intro], [Verse 1], [Chorus], [Verse 2], [Bridge], and [Outro].
- Do not imitate or quote an existing artist or song.
- Follow the supplied JSON schema exactly.
""".strip()

    def _build_retry_prompt(
        self,
        request: GenerateSongRequest,
        invalid_response: str,
    ) -> str:
        return f"""
The previous answer did not match the required JSON schema.
Create the song again and return only the required structured object.

Idea: {request.prompt}
Genre: {request.genre}
Language: {request.language}
Voice style: {request.voice}
Target duration: {request.duration_seconds} seconds

Do not add Markdown, explanations, or text outside the structured response.
Previous invalid answer for context:
{invalid_response[:1500]}
""".strip()

    def _parse_response(self, raw_response: str) -> tuple[str, str]:
        cleaned = self._clean_response(raw_response)
        parsed = self._load_json(cleaned)

        if not isinstance(parsed, dict):
            raise RuntimeError("Ollama response must be a JSON object")

        title = str(parsed.get("title", "")).strip()
        lyrics = str(parsed.get("lyrics", "")).strip()

        if not title or not lyrics:
            raise RuntimeError(
                "Ollama response is missing title or lyrics"
            )

        return self._normalize_title(title), self._normalize_lyrics(lyrics)

    def _load_json(self, response: str) -> Any:
        candidates = [response]

        extracted = self._extract_json_object(response)
        if extracted and extracted != response:
            candidates.append(extracted)

        unwrapped = self._unwrap_quoted_json(response)
        if unwrapped and unwrapped not in candidates:
            candidates.append(unwrapped)

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, str):
                    parsed = json.loads(parsed)
                return parsed
            except (json.JSONDecodeError, TypeError):
                continue

        raise RuntimeError(
            "Ollama did not return valid structured JSON"
        )

    def _clean_response(self, response: str) -> str:
        cleaned = response.strip()
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _extract_json_object(self, response: str) -> str | None:
        start = response.find("{")
        end = response.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return response[start:end + 1]

    def _unwrap_quoted_json(self, response: str) -> str | None:
        try:
            value = json.loads(response)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, str) else None

    def _normalize_title(self, title: str) -> str:
        return re.sub(r"\s+", " ", title.replace("\n", " ")).strip()[:255]

    def _normalize_lyrics(self, lyrics: str) -> str:
        normalized = lyrics.replace("\\n", "\n").strip()
        return re.sub(r"\n{3,}", "\n\n", normalized)
