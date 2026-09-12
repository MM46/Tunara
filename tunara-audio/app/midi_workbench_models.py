from typing import Literal

from pydantic import BaseModel, Field


class WorkbenchSection(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    bars: int = Field(ge=2, le=16)
    chords: list[str] = Field(min_length=2, max_length=8)
    energy: Literal["low", "medium", "high"]
    vocal_register: Literal["low", "middle", "high"]
    rhythm_density: Literal["sparse", "balanced", "dense"]


class WorkbenchPlan(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    language: str = Field(min_length=1, max_length=50)
    genre: str = Field(min_length=1, max_length=100)
    bpm: int = Field(ge=60, le=180)
    key: str = Field(pattern=r"^[A-G](#|b)? (major|minor)$")
    time_signature: Literal["4/4"] = "4/4"
    melodic_character: str = Field(min_length=1, max_length=300)
    drum_character: str = Field(min_length=1, max_length=300)
    bass_character: str = Field(min_length=1, max_length=300)
    sections: list[WorkbenchSection] = Field(min_length=2, max_length=10)


class MidiWorkbenchRequest(BaseModel):
    song_id: str = Field(min_length=1, max_length=100)
    lyrics: str = Field(min_length=1, max_length=20000)
    plan: WorkbenchPlan


class MidiWorkbenchResponse(BaseModel):
    song_id: str
    status: Literal["COMPLETED"]
    progress: Literal[100]
    package_url: str
    multitrack_midi_url: str
    vocal_melody_midi_url: str
    chords_midi_url: str
    bass_midi_url: str
    drums_midi_url: str
    duration_seconds: float
