from pydantic import BaseModel, Field


class VocalQaScore(BaseModel):
    accepted: bool
    score: float = Field(ge=0, le=1)
    coverage: float = Field(ge=0, le=1)
    order_score: float = Field(ge=0, le=1)
    hallucination_rate: float = Field(ge=0, le=1)
    sung_section_labels: list[str] = Field(default_factory=list)
    transcript: str
    missing_words: list[str] = Field(default_factory=list)
    extra_words: list[str] = Field(default_factory=list)
