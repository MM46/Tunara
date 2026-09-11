from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .composer_v2_service import ComposerV2Service
from .logic_pack_service import LogicPackService
from .musicgen_service import MusicGenService
from .schemas import InstrumentalRequest, InstrumentalResponse, LogicPackRequest, LogicPackResponse, VocalMelodyRequest, VocalMelodyResponse

app = FastAPI(title="Tunara Audio", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
musicgen_service = MusicGenService()
composer_service = ComposerV2Service()
logic_pack_service = LogicPackService()
for directory in (musicgen_service.output_directory, composer_service.output_directory, logic_pack_service.pack_directory):
    Path(directory).mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(musicgen_service.output_directory)), name="audio")
app.mount("/midi", StaticFiles(directory=str(composer_service.output_directory)), name="midi")
app.mount("/packs", StaticFiles(directory=str(logic_pack_service.pack_directory)), name="packs")

@app.get("/health")
async def health(): return {"status": "UP"}

@app.post("/api/instrumentals", response_model=InstrumentalResponse)
async def instrumental(request: InstrumentalRequest):
    try: return await musicgen_service.generate(request)
    except Exception as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.post("/api/vocal-melodies", response_model=VocalMelodyResponse)
async def melody(request: VocalMelodyRequest):
    try: return await composer_service.generate(request)
    except Exception as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.post("/api/logic-packs", response_model=LogicPackResponse)
async def logic_pack(request: LogicPackRequest):
    try: return await logic_pack_service.create(request)
    except Exception as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
