from .audio_client import AudioClient
from .lyrics_service import LyricsService
from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest, GenerateSongResponse


class GenerationService:
    def __init__(self) -> None:
        self.lyrics_service = LyricsService(OllamaClient())
        self.audio_client = AudioClient()

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> GenerateSongResponse:
        title, lyrics = await self.lyrics_service.generate(request)
        audio = await self.audio_client.generate_song(
            request=request,
            lyrics=lyrics,
            batch_size=2,
        )
        wav_urls = audio["wav_urls"]
        return GenerateSongResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            message=(
                "Lyrics and two ACE-Step WAV samples generated. "
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
