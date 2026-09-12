from typing import Literal

from pydantic import BaseModel, Field


class StemsRenderRequest(BaseModel):
    composition_id: str = Field(min_length=1, max_length=100)
    workbench_id: str = Field(min_length=1, max_length=100)
    target_duration_seconds: float = Field(gt=1, le=600)


class StemsRenderResponse(BaseModel):
    composition_id: str
    status: Literal["COMPLETED"]
    progress: Literal[100]
    preview_wav_url: str
    stems_package_url: str
    vocal_melody_wav_url: str
    chords_wav_url: str
    bass_wav_url: str
    drums_wav_url: str
    pads_wav_url: str
    arpeggio_wav_url: str
    transitions_wav_url: str
    counter_melody_wav_url: str | None
    sample_rate: Literal[48000]
    bit_depth: Literal[24]
    duration_seconds: float
