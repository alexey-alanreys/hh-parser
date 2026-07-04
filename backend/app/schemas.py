"""Pydantic schemas for the HTTP API."""

from enum import Enum

from pydantic import BaseModel, Field

from app.config import EXPERIENCE_CHOICES, MAX_VACANCIES_LIMIT


class ScanRequest(BaseModel):
    query: str = Field(min_length=2, max_length=200)
    experience: str | None = Field(default=None)
    max_vacancies: int = Field(default=50, ge=1, le=MAX_VACANCIES_LIMIT)

    def validate_experience(self) -> None:
        if self.experience is not None and self.experience not in EXPERIENCE_CHOICES:
            raise ValueError(f"Недопустимое значение experience: {self.experience}")


class CountItem(BaseModel):
    label: str
    count: int


class AnalysisResultOut(BaseModel):
    query: str
    total_vacancies: int
    hot_skills: list[CountItem]
    hot_keywords: list[CountItem]


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class JobStage(str, Enum):
    COLLECTING = "collecting"  # fetching search result pages
    ENRICHING = "enriching"  # fetching each vacancy's description and skills
    ANALYZING = "analyzing"  # frequency analysis


class JobProgress(BaseModel):
    stage: JobStage
    current: int
    total: int


class ScanCreatedOut(BaseModel):
    job_id: str


class JobStatusOut(BaseModel):
    job_id: str
    status: JobStatus
    progress: JobProgress | None = None
    result: AnalysisResultOut | None = None
    error: str | None = None