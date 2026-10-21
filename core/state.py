from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""
    published_date: str | None = None


class ScrapedSource(BaseModel):
    url: str
    title: str = ""
    text: str = ""
    status: Literal["success", "failed"]
    error: str | None = None


class Finding(BaseModel):
    claim: str
    source_url: str
    evidence: str = ""
    source_title: str = ""


class CriterionScores(BaseModel):
    relevance: float = Field(ge=0, le=10)
    factual_support: float = Field(ge=0, le=10)
    research_depth: float = Field(ge=0, le=10)
    perspectives: float = Field(ge=0, le=10)
    logic: float = Field(ge=0, le=10)
    clarity: float = Field(ge=0, le=10)
    uncertainty: float = Field(ge=0, le=10)


class CriticEvaluation(BaseModel):
    overall_score: float = Field(ge=0, le=10)
    criterion_scores: CriterionScores
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    verdict: str


class ResearchState(BaseModel):
    topic: str
    status: str = "pending"
    progress_message: str = ""
    search_results: list[SearchResult] = Field(default_factory=list)
    scraped_sources: list[ScrapedSource] = Field(default_factory=list)
    failed_sources: dict[str, str] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)
    report: str = ""
    critic: CriticEvaluation | None = None
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def update(self, status: str, message: str) -> None:
        self.status, self.progress_message = status, message
