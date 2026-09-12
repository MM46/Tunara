from fastapi import FastAPI, HTTPException

from .generation_service import GenerationService
from .prompt_director_router import router as prompt_director_router
from .schemas import GenerateSongRequest, GenerateSongResponse
from .song_plan_router import router as song_plan_router

app = FastAPI(title="Tunara AI", version="0.5.0")
app.include_router(prompt_director_router)
app.include_router(song_plan_router)
service = GenerationService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/health/audio")
async def audio_health() -> dict:
    try:
        return await service.audio_client.health()
    except Exception as exception:
        raise HTTPException(
            status_code=503,
            detail=f"ACE-Step unavailable: {exception}",
        ) from exception


@app.post("/api/generate", response_model=GenerateSongResponse)
async def generate(
    request: GenerateSongRequest,
) -> GenerateSongResponse:
    try:
        return await service.generate(request)
    except Exception as exception:
        raise HTTPException(
            status_code=502,
            detail=str(exception),
        ) from exception
