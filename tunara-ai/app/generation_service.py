from .audio_client import AudioClient
from .lyrics_service import LyricsService
from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest, GenerateSongResponse
class GenerationService:
    def __init__(self):
        self.lyrics_service=LyricsService(OllamaClient()); self.audio_client=AudioClient()
    async def generate(self, request):
        title,lyrics=await self.lyrics_service.generate(request)
        instrumental=await self.audio_client.generate_instrumental(request)
        melody=await self.audio_client.generate_vocal_melody(request,lyrics)
        pack=await self.audio_client.create_logic_pack(request,title,lyrics,int(melody["bpm"]))
        return GenerateSongResponse(song_id=request.song_id,status="COMPLETED",progress=100,message="Lyrics, instrumental, MIDI and Logic pack generated.",title=title,lyrics=lyrics,wav_url=str(instrumental["wav_url"]),midi_url=str(melody["midi_url"]),logic_pack_url=str(pack["pack_url"]))
