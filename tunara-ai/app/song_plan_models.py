from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SongSectionPlan(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    bars: int = Field(ge=2, le=16)
    chords: list[str] = Field(min_length=2, max_length=8)
    energy: Literal["low", "medium", "high"]
    vocal_register: Literal["low", "middle", "high"]
    rhythm_density: Literal["sparse", "balanced", "dense"]


class SongPlan(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    language: str = Field(min_length=1, max_length=50)
    genre: str = Field(min_length=1, max_length=100)
    bpm: int = Field(ge=60, le=180)
    key: str = Field(pattern=r"^[A-G](#|b)? (major|minor)$")
    time_signature: Literal["4/4"] = "4/4"
    melodic_character: str = Field(min_length=1, max_length=300)
    drum_character: str = Field(min_length=1, max_length=300)
    bass_character: str = Field(min_length=1, max_length=300)
    sections: list[SongSectionPlan] = Field(min_length=2, max_length=10)

    @model_validator(mode="after")
    def validate_structure(self) -> "SongPlan":
        names = [section.name.lower() for section in self.sections]
        if not any("verse" in name or "verso" in name for name in names):
            raise ValueError("The plan must contain a verse")
        if not any("chorus" in name or "coro" in name for name in names):
            raise ValueError("The plan must contain a chorus")
        return self


class SongPlanRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    lyrics: str = Field(min_length=1, max_length=20000)
    genre: str = Field(min_length=1, max_length=100)
    language: str = Field(min_length=1, max_length=50)
    target_duration_seconds: int = Field(ge=30, le=600)


class SongPlanResponse(BaseModel):
    status: Literal["COMPLETED"]
    progress: Literal[100]
    plan: SongPlan
