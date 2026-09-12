from .audio_client import AudioClient
from .lyrics_service import LyricsService
from .lyrics_sanitizer import LyricsSanitizer
from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest, GenerateSongResponse


class GenerationService:
    def __init__(self) -> None:
        self.lyrics_service = LyricsService(OllamaClient())
        self.audio_client = AudioClient()
        self.lyrics_sanitizer = LyricsSanitizer()

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> GenerateSongResponse:
        title, generated_lyrics = await self.lyrics_service.generate(request)
        lyrics = self.lyrics_sanitizer.sanitize(
            generated_lyrics,
            request.duration_seconds,
        )
        minimum_duration = self.lyrics_sanitizer.minimum_duration_seconds(lyrics)
        generation_request = request.model_copy(
            update={
                "duration_seconds": max(
                    request.duration_seconds,
                    minimum_duration,
                )
            }
        )
        audio = await self.audio_client.generate_song(
            request=generation_request,
            lyrics=lyrics,
            batch_size=1,
        )
        wav_urls = audio["wav_urls"]
        return GenerateSongResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            message=(
                "Lyrics and one ACE-Step WAV sample generated. "
                "MIDI and Logic Pro pack remain pending for the export stage."
            ),
            title=title,
            lyrics=lyrics,
            wav_url=wav_urls[0],
            wav_urls=wav_urls,
            midi_url="",
            logic_pack_url="",
            ace_task_id=audio["task_id"],
            bpm=audio.get("bpm"),
            keyscale=audio.get("keyscale", ""),
            timesignature=audio.get("timesignature", ""),
        )
