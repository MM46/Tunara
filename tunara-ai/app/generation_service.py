from .audio_client import AudioClient
from .lyrics_service import LyricsService
from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest, GenerateSongResponse


class GenerationService:
    def __init__(self) -> None:
        self.lyrics_service = LyricsService(OllamaClient())
        self.audio_client = AudioClient()

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> GenerateSongResponse:
        title, lyrics = await self.lyrics_service.generate(request)
        wav_url = await self.audio_client.generate_instrumental(request)

        return GenerateSongResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            message=(
                "Lyrics and instrumental generated successfully."
            ),
            title=title,
            lyrics=lyrics,
            wav_url=wav_url,
        )
