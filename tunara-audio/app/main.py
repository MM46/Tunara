from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .musicgen_service import MusicGenService
from .schemas import InstrumentalRequest, InstrumentalResponse

app = FastAPI(title="Tunara Audio", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

service = MusicGenService()
Path(service.output_directory).mkdir(parents=True, exist_ok=True)
app.mount(
    "/audio",
    StaticFiles(directory=str(service.output_directory)),
    name="audio",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post(
    "/api/instrumentals",
    response_model=InstrumentalResponse,
)
async def generate_instrumental(
    request: InstrumentalRequest,
) -> InstrumentalResponse:
    try:
        return await service.generate(request)
    except Exception as exception:
        raise HTTPException(
            status_code=502,
            detail=str(exception),
        ) from exception
