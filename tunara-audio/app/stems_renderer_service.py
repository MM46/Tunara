import asyncio
import json
import os
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .stems_renderer_models import StemsRenderRequest, StemsRenderResponse


class StemsRendererService:
    STEM_FILES = {
        "vocal": ("02-Vocal-Melody-Piano.mid", "01-Vocal-Melody-48k-24bit.wav"),
        "chords": ("03-Chords.mid", "02-Chords-48k-24bit.wav"),
        "bass": ("04-Bass.mid", "03-Bass-48k-24bit.wav"),
        "drums": ("05-Drums.mid", "04-Drums-48k-24bit.wav"),
        "pads": ("06-Pads.mid", "05-Pads-48k-24bit.wav"),
        "arpeggio": ("07-Arpeggio.mid", "06-Arpeggio-48k-24bit.wav"),
        "transitions": ("08-Transitions.mid", "07-Transitions-48k-24bit.wav"),
        "counter": ("09-Chorus-Counter-Melody.mid", "08-Counter-Melody-48k-24bit.wav"),
    }

    def __init__(self) -> None:
        self.public_base_url = os.getenv(
            "AUDIO_PUBLIC_BASE_URL",
            "http://localhost:8001",
        ).rstrip("/")
        self.workbench_directory = Path(
            os.getenv("MIDI_WORKBENCH_OUTPUT_DIRECTORY", "generated-workbench")
        ).resolve()
        self.output_directory = Path(
            os.getenv("STEMS_OUTPUT_DIRECTORY", "generated-stems")
        ).resolve()
        self.fluidsynth = os.getenv(
            "FLUIDSYNTH_BIN",
            "/opt/homebrew/bin/fluidsynth",
        )
        self.ffmpeg = os.getenv("FFMPEG_BIN", "ffmpeg")
        self.ffprobe = os.getenv("FFPROBE_BIN", "ffprobe")
        self.soundfont = Path(
            os.getenv(
                "FLUIDSYNTH_SOUNDFONT",
                "/opt/homebrew/share/fluid-synth/sf2/VintageDreamsWaves-v2.sf3",
            )
        )
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self._render_lock = asyncio.Lock()

    async def render(
        self,
        request: StemsRenderRequest,
    ) -> StemsRenderResponse:
        safe_composition_id = self._safe_id(request.composition_id)
        safe_workbench_id = self._safe_id(request.workbench_id)
        source_directory = self.workbench_directory / safe_workbench_id
        render_directory = self.output_directory / safe_composition_id

        self._validate_runtime(source_directory)

        async with self._render_lock:
            if render_directory.exists():
                shutil.rmtree(render_directory)
            render_directory.mkdir(parents=True)

            rendered: dict[str, Path] = {}
            for stem_name, (midi_name, wav_name) in self.STEM_FILES.items():
                midi_path = source_directory / midi_name
                if not midi_path.exists():
                    if stem_name == "counter":
                        continue
                    raise RuntimeError(f"Required stem MIDI is missing: {midi_path}")

                output_path = render_directory / wav_name
                await self._render_stem(
                    midi_path,
                    output_path,
                    request.target_duration_seconds,
                )
                rendered[stem_name] = output_path

            preview_path = render_directory / "00-Full-Preview-48k-24bit.wav"
            await self._mix_stems(
                list(rendered.values()),
                preview_path,
                request.target_duration_seconds,
            )

            manifest_path = render_directory / "09-Render-Manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "compositionId": safe_composition_id,
                        "workbenchId": safe_workbench_id,
                        "preview": preview_path.name,
                        "stems": {
                            name: path.name for name, path in rendered.items()
                        },
                        "audio": {
                            "sampleRate": 48000,
                            "bitDepth": 24,
                            "channels": 2,
                            "format": "WAV PCM",
                        },
                        "durationSeconds": request.target_duration_seconds,
                    },
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )

            archive_path = self.output_directory / (
                f"{safe_composition_id}-audio-stems.zip"
            )
            with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
                for path in sorted(render_directory.iterdir()):
                    archive.write(
                        path,
                        f"{safe_composition_id}-Audio-Stems/{path.name}",
                    )

        base_url = f"{self.public_base_url}/stems/{safe_composition_id}"
        return StemsRenderResponse(
            composition_id=request.composition_id,
            status="COMPLETED",
            progress=100,
            preview_wav_url=f"{base_url}/{preview_path.name}",
            stems_package_url=(
                f"{self.public_base_url}/stems/{archive_path.name}"
            ),
            vocal_melody_wav_url=self._url(base_url, rendered, "vocal"),
            chords_wav_url=self._url(base_url, rendered, "chords"),
            bass_wav_url=self._url(base_url, rendered, "bass"),
            drums_wav_url=self._url(base_url, rendered, "drums"),
            pads_wav_url=self._url(base_url, rendered, "pads"),
            arpeggio_wav_url=self._url(base_url, rendered, "arpeggio"),
            transitions_wav_url=self._url(base_url, rendered, "transitions"),
            counter_melody_wav_url=(
                self._url(base_url, rendered, "counter")
                if "counter" in rendered
                else None
            ),
            sample_rate=48000,
            bit_depth=24,
            duration_seconds=request.target_duration_seconds,
        )

    def _validate_runtime(self, source_directory: Path) -> None:
        if not source_directory.is_dir():
            raise RuntimeError(
                f"Workbench directory does not exist: {source_directory}"
            )
        if not Path(self.fluidsynth).is_file():
            raise RuntimeError(
                f"FluidSynth executable was not found: {self.fluidsynth}"
            )
        if not self.soundfont.is_file():
            raise RuntimeError(
                f"SoundFont was not found: {self.soundfont}"
            )

    async def _render_stem(
        self,
        midi_path: Path,
        output_path: Path,
        duration_seconds: float,
    ) -> None:
        raw_path = output_path.with_suffix(".raw.wav")
        command = [
            self.fluidsynth,
            "-ni",
            "-r",
            "48000",
            "-R",
            "0",
            "-C",
            "0",
            "-F",
            str(raw_path),
            str(self.soundfont),
            str(midi_path),
        ]
        await self._run(command, f"FluidSynth failed for {midi_path.name}")

        conversion = [
            self.ffmpeg,
            "-y",
            "-i",
            str(raw_path),
            "-af",
            f"apad=whole_dur={duration_seconds}",
            "-t",
            str(duration_seconds),
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(output_path),
        ]
        await self._run(conversion, f"FFmpeg failed for {midi_path.name}")
        raw_path.unlink(missing_ok=True)
        await self._validate_wave(output_path)

    async def _mix_stems(
        self,
        stems: list[Path],
        preview_path: Path,
        duration_seconds: float,
    ) -> None:
        if not stems:
            raise RuntimeError("No rendered stems are available to mix")

        command = [self.ffmpeg, "-y"]
        for stem in stems:
            command.extend(["-i", str(stem)])

        command.extend(
            [
                "-filter_complex",
                f"amix=inputs={len(stems)}:duration=longest:normalize=0,"
                "alimiter=limit=0.95",
                "-t",
                str(duration_seconds),
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s24le",
                str(preview_path),
            ]
        )
        await self._run(command, "Unable to mix the audio stems")
        await self._validate_wave(preview_path)

    async def _validate_wave(self, path: Path) -> None:
        command = [
            self.ffprobe,
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bits_per_sample",
            "-of",
            "default=noprint_wrappers=1",
            str(path),
        ]
        output = await self._run(command, f"Unable to validate {path.name}")
        required = {
            "codec_name=pcm_s24le",
            "sample_rate=48000",
            "channels=2",
            "bits_per_sample=24",
        }
        actual = set(output.splitlines())
        if not required.issubset(actual):
            raise RuntimeError(
                f"Invalid rendered WAV format for {path.name}: {output}"
            )

    async def _run(self, command: list[str], error_message: str) -> str:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await process.communicate()
        output = stdout.decode("utf-8", errors="replace")
        if process.returncode != 0:
            raise RuntimeError(f"{error_message}: {output[-2000:]}")
        return output.strip()

    def _url(
        self,
        base_url: str,
        rendered: dict[str, Path],
        stem_name: str,
    ) -> str:
        return f"{base_url}/{rendered[stem_name].name}"

    def _safe_id(self, value: str) -> str:
        safe_value = re.sub(r"[^A-Za-z0-9_-]", "", value)
        if not safe_value:
            raise RuntimeError("Invalid composition or workbench ID")
        return safe_value
