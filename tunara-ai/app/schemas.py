from pydantic import BaseModel, Field


class GenerateSongRequest(BaseModel):
    song_id: str
    prompt: str = Field(min_length=1, max_length=2000)
    genre: str
    voice: str
    language: str
    duration_seconds: int = Field(ge=30, le=600)


class GenerateSongResponse(BaseModel):
    song_id: str
    status: str
    progress: int
    message: str
    title: str
    lyrics: str
    wav_url: str
    wav_urls: list[str] = Field(default_factory=list)
    midi_url: str = ""
    logic_pack_url: str = ""
    ace_task_id: str = ""
    bpm: int | None = None
    keyscale: str = ""
    timesignature: str = ""
