from pydantic import BaseModel, Field


class PromptDirectorRequest(BaseModel):
    idea: str = Field(min_length=1, max_length=2000)
    genre: str | None = Field(default=None, max_length=100)
    language: str = Field(default="Spanish", min_length=1, max_length=50)
    duration_seconds: int = Field(default=180, ge=30, le=600)


class CreativeBrief(BaseModel):
    original_idea: str
    safe_reference_translation: str
    genre: str
    subgenre: str
    language: str
    duration_seconds: int
    bpm_range: str
    tonal_direction: str
    mood: str
    lyrical_theme: str
    song_structure: list[str]
    instrumentation: list[str]
    vocal_direction: str
    arrangement_direction: str
    transition_direction: str
    mix_direction: str
    negative_constraints: list[str]
    lyrics_prompt: str
    song_planner_prompt: str
    production_prompt: str


class PromptDirectorResponse(BaseModel):
    status: str
    progress: int
    brief: CreativeBrief
