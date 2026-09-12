import os
import re
import subprocess
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/api/permanent-audio", tags=["permanent-audio"])

OUTPUT_DIRECTORY = Path(
    os.getenv("AUDIO_OUTPUT_DIRECTORY", "generated-audio")
).resolve()
PUBLIC_BASE_URL = os.getenv(
    "AUDIO_PUBLIC_BASE_URL", "http://localhost:8001"
).rstrip("/")
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")


def safe_song_id(value: str) -> str:
    safe_value = re.sub(r"[^A-Za-z0-9_-]", "", value)
    if not safe_value:
        raise HTTPException(status_code=400, detail="Invalid song ID")
    return safe_value


@router.post("/{song_id}")
async def store_permanent_audio(
    song_id: str,
    audio: UploadFile = File(...),
) -> dict[str, object]:
    safe_id = safe_song_id(song_id)
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    final_path = OUTPUT_DIRECTORY / f"{safe_id}.wav"

    suffix = Path(audio.filename or "source.audio").suffix or ".audio"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        source_path = Path(handle.name)
        while chunk := await audio.read(1024 * 1024):
            handle.write(chunk)

    try:
        process = subprocess.run(
            [
                FFMPEG_BIN,
                "-y",
                "-i",
                str(source_path),
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s24le",
                str(final_path),
            ],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if process.returncode != 0:
            raise HTTPException(
                status_code=502,
                detail=f"FFmpeg failed: {process.stderr[-1500:]}",
            )

        probe = subprocess.run(
            [
                FFPROBE_BIN,
                "-v",
                "error",
                "-show_entries",
                "stream=codec_name,sample_rate,channels,bits_per_sample",
                "-of",
                "default=noprint_wrappers=1",
                str(final_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        required = {
            "codec_name=pcm_s24le",
            "sample_rate=48000",
            "channels=2",
            "bits_per_sample=24",
        }
        if probe.returncode != 0 or not required.issubset(
            set(probe.stdout.splitlines())
        ):
            final_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=502,
                detail=f"Invalid permanent WAV: {probe.stdout} {probe.stderr}",
            )
    finally:
        source_path.unlink(missing_ok=True)
        await audio.close()

    return {
        "song_id": safe_id,
        "status": "COMPLETED",
        "wav_url": f"{PUBLIC_BASE_URL}/audio/{final_path.name}",
        "sample_rate": 48000,
        "bit_depth": 24,
        "channels": 2,
    }
