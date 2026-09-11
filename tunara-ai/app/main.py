from fastapi import FastAPI, HTTPException

from .generation_service import GenerationService
from .schemas import GenerateSongRequest, GenerateSongResponse

app = FastAPI(title="Tunara AI", version="0.2.0")
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
