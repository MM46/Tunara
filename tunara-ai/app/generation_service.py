from .schemas import GenerateSongRequest, GenerateSongResponse

class GenerationService:
    async def generate(self, request: GenerateSongRequest) -> GenerateSongResponse:
        return GenerateSongResponse(
            song_id=request.song_id,
            status="PENDING",
            progress=0,
            message="Generation request accepted. Model pipeline is not configured yet.",
        )
