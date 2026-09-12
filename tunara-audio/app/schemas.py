from pydantic import BaseModel, Field


class InstrumentalRequest(BaseModel):
    song_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1, max_length=2000)
    genre: str = Field(min_length=1, max_length=100)
    duration_seconds: int = Field(ge=5, le=600)


class InstrumentalResponse(BaseModel):
    song_id: str
    status: str
    progress: int
    wav_url: str
    generated_duration_seconds: int


class VocalMelodyRequest(BaseModel):
    song_id: str = Field(min_length=1)
    lyrics: str = Field(min_length=1, max_length=20000)
    genre: str = Field(min_length=1, max_length=100)
    duration_seconds: int = Field(ge=10, le=600)


class VocalMelodyResponse(BaseModel):
    song_id: str
    status: str
    progress: int
    midi_url: str
    bpm: int
    note_count: int
    generated_duration_seconds: float


class OpenUtauProjectRequest(BaseModel):
    song_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    lyrics: str = Field(min_length=1, max_length=20000)
    bpm: int = Field(ge=40, le=240)


class OpenUtauProjectResponse(BaseModel):
    song_id: str
    status: str
    progress: int
    ustx_url: str


class LogicPackRequest(BaseModel):
    song_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    lyrics: str = Field(min_length=1, max_length=20000)
    prompt: str = Field(min_length=1, max_length=2000)
    genre: str = Field(min_length=1, max_length=100)
    voice: str = Field(min_length=1, max_length=100)
    language: str = Field(min_length=1, max_length=50)
    duration_seconds: int = Field(ge=10, le=600)
    bpm: int = Field(ge=40, le=240)


class LogicPackResponse(BaseModel):
    song_id: str
    status: str
    progress: int
    instrumental_wav_url: str
    midi_url: str
    lyrics_url: str
    metadata_url: str
    pack_url: str
