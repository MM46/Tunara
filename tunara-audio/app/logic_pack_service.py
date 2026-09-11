import asyncio
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from .schemas import LogicPackRequest, LogicPackResponse

class LogicPackService:
    def __init__(self):
        self.public_base_url=os.getenv("AUDIO_PUBLIC_BASE_URL","http://localhost:8001").rstrip("/")
        self.audio_directory=Path(os.getenv("AUDIO_OUTPUT_DIRECTORY","generated-audio")).resolve()
        self.midi_directory=Path(os.getenv("MIDI_OUTPUT_DIRECTORY","generated-midi")).resolve()
        self.pack_directory=Path(os.getenv("LOGIC_PACK_OUTPUT_DIRECTORY","generated-packs")).resolve(); self.pack_directory.mkdir(parents=True,exist_ok=True)

    async def create(self, request):
        sid=self._safe(request.song_id); source_wav=self.audio_directory/f"{sid}.wav"
        mappings={"02-Vocal-Melody.mid":self.midi_directory/f"{sid}-vocal.mid","03-Chords.mid":self.midi_directory/f"{sid}-chords.mid","04-Bass.mid":self.midi_directory/f"{sid}-bass.mid","05-Drums.mid":self.midi_directory/f"{sid}-drums.mid","06-Composer-Multitrack.mid":self.midi_directory/f"{sid}-composer-v2.mid"}
        if not source_wav.exists(): raise RuntimeError("Instrumental WAV does not exist")
        missing=[str(p) for p in mappings.values() if not p.exists()]
        if missing: raise RuntimeError("Composer MIDI files missing: "+", ".join(missing))
        folder=f"{self._slug(request.title)}-Logic-Pack"; work=self.pack_directory/f".{sid}-work"; final=work/folder
        if work.exists(): shutil.rmtree(work)
        final.mkdir(parents=True)
        await self._convert(source_wav,final/"01-Instrumental-48k-24bit.wav")
        for name,source in mappings.items(): shutil.copy2(source,final/name)
        (final/"07-Lyrics.txt").write_text(request.lyrics.strip()+"\n",encoding="utf-8")
        (final/"08-Metadata.json").write_text(json.dumps({"songId":request.song_id,"title":request.title,"prompt":request.prompt,"genre":request.genre,"voice":request.voice,"language":request.language,"targetDurationSeconds":request.duration_seconds,"bpm":request.bpm,"logicPro":{"audio":"48 kHz 24-bit PCM WAV","midi":"Standard MIDI multitrack and separated tracks"}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        archive=self.pack_directory/f"{sid}-logic-pack.zip"
        with ZipFile(archive,"w",ZIP_DEFLATED) as z:
            for item in final.iterdir(): z.write(item,f"{folder}/{item.name}")
        shutil.rmtree(work)
        return LogicPackResponse(song_id=request.song_id,status="COMPLETED",progress=100,instrumental_wav_url=f"{self.public_base_url}/audio/{source_wav.name}",midi_url=f"{self.public_base_url}/midi/{sid}-composer-v2.mid",lyrics_url="",metadata_url="",pack_url=f"{self.public_base_url}/packs/{archive.name}")

    async def _convert(self,source,target):
        p=await asyncio.create_subprocess_exec("ffmpeg","-y","-i",str(source),"-ar","48000","-acodec","pcm_s24le",str(target),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT); out,_=await p.communicate()
        if p.returncode!=0: raise RuntimeError("FFmpeg conversion failed: "+out.decode(errors="replace")[-1500:])
    def _safe(self,value): return "".join(ch for ch in value if ch.isalnum() or ch in {"-","_"})
    def _slug(self,value):
        ascii_value=unicodedata.normalize("NFKD",value).encode("ascii","ignore").decode("ascii")
        return (re.sub(r"[^A-Za-z0-9]+","-",ascii_value).strip("-")[:80] or "Tunara-Song")
