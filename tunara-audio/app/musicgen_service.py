import asyncio
import os
from pathlib import Path

from .schemas import InstrumentalRequest, InstrumentalResponse


class MusicGenService:
    def __init__(self) -> None:
        self.model = os.getenv(
            "MUSICGEN_MODEL",
            "facebook/musicgen-small",
        )
        self.public_base_url = os.getenv(
            "AUDIO_PUBLIC_BASE_URL",
            "http://localhost:8001",
        ).rstrip("/")
        self.output_directory = Path(
            os.getenv("AUDIO_OUTPUT_DIRECTORY", "generated-audio")
        ).resolve()
        self.maximum_duration = int(
            os.getenv("MUSICGEN_MAX_DURATION_SECONDS", "30")
        )
        self.timeout_seconds = int(
            os.getenv("MUSICGEN_TIMEOUT_SECONDS", "900")
        )
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self._generation_lock = asyncio.Lock()

    async def generate(
        self,
        request: InstrumentalRequest,
    ) -> InstrumentalResponse:
        generated_duration = min(
            request.duration_seconds,
            self.maximum_duration,
        )
        safe_song_id = self._safe_song_id(request.song_id)
        output_path = self.output_directory / f"{safe_song_id}.wav"
        music_prompt = self._build_music_prompt(request)

        command = [
            "musicgen-mlx",
            music_prompt,
            "-m",
            self.model,
            "-d",
            str(generated_duration),
            "-o",
            str(output_path),
            "--no-open",
        ]

        async with self._generation_lock:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as exception:
                process.kill()
                await process.communicate()
                raise RuntimeError(
                    "MusicGen exceeded the configured timeout"
                ) from exception

        output = stdout.decode("utf-8", errors="replace")
        if process.returncode != 0:
            raise RuntimeError(
                "MusicGen failed: " + output[-2000:]
            )

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("MusicGen did not create a WAV file")

        return InstrumentalResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            wav_url=(
                f"{self.public_base_url}/audio/{output_path.name}"
            ),
            generated_duration_seconds=generated_duration,
        )

    def _build_music_prompt(
        self,
        request: InstrumentalRequest,
    ) -> str:
        return (
            f"{request.genre} instrumental, {request.prompt}, "
            "coherent arrangement, polished production, no vocals"
        )

    def _safe_song_id(self, song_id: str) -> str:
        return "".join(
            character
            for character in song_id
            if character.isalnum() or character in {"-", "_"}
        )
