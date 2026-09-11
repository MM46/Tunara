from fastapi import FastAPI
from .generation_service import GenerationService
from .schemas import GenerateSongRequest, GenerateSongResponse

app = FastAPI(title="Tunara AI", version="0.1.0")
service = GenerationService()

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}

@app.post("/api/generate", response_model=GenerateSongResponse)
async def generate(request: GenerateSongRequest) -> GenerateSongResponse:
    return await service.generate(request)
