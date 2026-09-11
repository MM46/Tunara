import os
import httpx
from .schemas import GenerateSongRequest

class AudioClient:
    def __init__(self):
        self.base_url=os.getenv("TUNARA_AUDIO_BASE_URL","http://host.docker.internal:8001").rstrip("/")
        self.timeout=float(os.getenv("TUNARA_AUDIO_TIMEOUT_SECONDS","900"))

    async def generate_instrumental(self, request):
        return await self._post("/api/instrumentals", {"song_id":request.song_id,"prompt":request.prompt,"genre":request.genre,"duration_seconds":request.duration_seconds})

    async def generate_vocal_melody(self, request, lyrics):
        return await self._post("/api/vocal-melodies", {"song_id":request.song_id,"lyrics":lyrics,"genre":request.genre,"duration_seconds":request.duration_seconds})

    async def create_logic_pack(self, request, title, lyrics, bpm):
        return await self._post("/api/logic-packs", {"song_id":request.song_id,"title":title,"lyrics":lyrics,"prompt":request.prompt,"genre":request.genre,"voice":request.voice,"language":request.language,"duration_seconds":request.duration_seconds,"bpm":bpm})

    async def _post(self, path, payload):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response=await client.post(f"{self.base_url}{path}", json=payload)
            response.raise_for_status()
            return response.json()
