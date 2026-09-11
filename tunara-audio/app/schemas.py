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
