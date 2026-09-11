import os

import httpx

from .schemas import GenerateSongRequest


class AudioClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "TUNARA_AUDIO_BASE_URL",
            "http://host.docker.internal:8001",
        ).rstrip("/")
        self.timeout = float(
            os.getenv("TUNARA_AUDIO_TIMEOUT_SECONDS", "900")
        )

    async def generate_instrumental(
        self,
        request: GenerateSongRequest,
    ) -> str:
        payload = {
            "song_id": request.song_id,
            "prompt": request.prompt,
            "genre": request.genre,
            "duration_seconds": request.duration_seconds,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/instrumentals",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        wav_url = str(data.get("wav_url", "")).strip()
        if not wav_url:
            raise RuntimeError("Tunara Audio returned no WAV URL")

        return wav_url
