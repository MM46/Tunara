from .lyrics_service import LyricsService
from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest, GenerateSongResponse


class GenerationService:
    def __init__(self) -> None:
        self.lyrics_service = LyricsService(OllamaClient())

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> GenerateSongResponse:
        title, lyrics = await self.lyrics_service.generate(request)

        return GenerateSongResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            message="Lyrics generated successfully with Ollama.",
            title=title,
            lyrics=lyrics,
        )
