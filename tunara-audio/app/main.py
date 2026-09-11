from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .musicgen_service import MusicGenService
from .schemas import (
    InstrumentalRequest,
    InstrumentalResponse,
    VocalMelodyRequest,
    VocalMelodyResponse,
)
from .vocal_melody_service import VocalMelodyService

app = FastAPI(title="Tunara Audio", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

musicgen_service = MusicGenService()
vocal_melody_service = VocalMelodyService()

Path(musicgen_service.output_directory).mkdir(
    parents=True,
    exist_ok=True,
)
Path(vocal_melody_service.output_directory).mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/audio",
    StaticFiles(directory=str(musicgen_service.output_directory)),
    name="audio",
)
app.mount(
    "/midi",
    StaticFiles(directory=str(vocal_melody_service.output_directory)),
    name="midi",
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
        return await musicgen_service.generate(request)
    except Exception as exception:
        raise HTTPException(
            status_code=502,
            detail=str(exception),
        ) from exception


@app.post(
    "/api/vocal-melodies",
    response_model=VocalMelodyResponse,
)
async def generate_vocal_melody(
    request: VocalMelodyRequest,
) -> VocalMelodyResponse:
    try:
        return await vocal_melody_service.generate(request)
    except Exception as exception:
        raise HTTPException(
            status_code=502,
            detail=str(exception),
        ) from exception
