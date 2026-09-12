from fastapi import FastAPI, HTTPException

from .generation_service import GenerationService
from .schemas import GenerateSongRequest, GenerateSongResponse
from .song_plan_router import router as song_plan_router

app = FastAPI(title="Tunara AI", version="0.3.0")
app.include_router(song_plan_router)
service = GenerationService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


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
