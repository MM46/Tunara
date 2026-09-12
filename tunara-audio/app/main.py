from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .logic_pack_service import LogicPackService
from .musicgen_service import MusicGenService
from .openutau_project_service import OpenUtauProjectService
from .schemas import (
    InstrumentalRequest,
    InstrumentalResponse,
    LogicPackRequest,
    LogicPackResponse,
    OpenUtauProjectRequest,
    OpenUtauProjectResponse,
    VocalMelodyRequest,
    VocalMelodyResponse,
)
from .composer_v2_service import ComposerV2Service

app = FastAPI(title="Tunara Audio", version="0.6.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

musicgen_service = MusicGenService()
composer_service = ComposerV2Service()
openutau_service = OpenUtauProjectService()
logic_pack_service = LogicPackService()

for directory in (
    musicgen_service.output_directory,
    composer_service.output_directory,
    openutau_service.output_directory,
    logic_pack_service.pack_directory,
):
    Path(directory).mkdir(parents=True, exist_ok=True)

app.mount("/audio", StaticFiles(directory=str(musicgen_service.output_directory)), name="audio")
app.mount("/midi", StaticFiles(directory=str(composer_service.output_directory)), name="midi")
app.mount("/openutau", StaticFiles(directory=str(openutau_service.output_directory)), name="openutau")
app.mount("/packs", StaticFiles(directory=str(logic_pack_service.pack_directory)), name="packs")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post("/api/instrumentals", response_model=InstrumentalResponse)
async def instrumental(request: InstrumentalRequest):
    try:
        return await musicgen_service.generate(request)
    except Exception as exception:
        raise HTTPException(status_code=502, detail=str(exception)) from exception


@app.post("/api/vocal-melodies", response_model=VocalMelodyResponse)
async def melody(request: VocalMelodyRequest):
    try:
        return await composer_service.generate(request)
    except Exception as exception:
        raise HTTPException(status_code=502, detail=str(exception)) from exception


@app.post("/api/openutau-projects", response_model=OpenUtauProjectResponse)
async def openutau_project(request: OpenUtauProjectRequest):
    try:
        url = await openutau_service.generate(
            request.song_id,
            request.title,
            request.lyrics,
            request.bpm,
        )
        return OpenUtauProjectResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            ustx_url=url,
        )
    except Exception as exception:
        raise HTTPException(status_code=502, detail=str(exception)) from exception


@app.post("/api/logic-packs", response_model=LogicPackResponse)
async def logic_pack(request: LogicPackRequest):
    try:
        return await logic_pack_service.create(request)
    except Exception as exception:
        raise HTTPException(status_code=502, detail=str(exception)) from exception
