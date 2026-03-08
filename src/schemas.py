from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["Easy", "Medium", "Hard"]


class ExtractedFocusAreas(BaseModel):
    """
    Structured output for extracting role and focus areas from a job description.
    """
    role: str = Field(..., description="Short inferred role title from the job description.")
    focus_areas: list[str] = Field(..., description="Clean list of extracted focus areas.")
    summary: str = Field(..., description="Short summary of what the job description emphasizes.")


class InterviewPlan(BaseModel):
    role: str = Field(..., description="Target role being interviewed for.")
    difficulty: Difficulty
    focus_areas: list[str] = Field(..., description="List of focus areas/topics.")
    total_questions: int = Field(..., ge=1, le=20)
    strategy: str = Field(..., description="Prompt strategy name selected in the UI.")
    persona: str = Field(..., description="Interviewer persona selected in the UI.")
    rubric_criteria: list[str] = Field(..., description="Criteria used to evaluate answers.")
    tips: list[str] = Field(..., description="Actionable preparation tips.")


class RubricScores(BaseModel):
    clarity: int = Field(..., ge=1, le=10)
    correctness: int = Field(..., ge=1, le=10)
    depth: int = Field(..., ge=1, le=10)
    structure: int = Field(..., ge=1, le=10)
    communication: int = Field(..., ge=1, le=10)


class FinalFeedback(BaseModel):
    role: str
    difficulty: Difficulty
    question: str
    answer_summary: str = Field(..., description="Short summary of the candidate answer.")
    scores: RubricScores
    strengths: list[str]
    weaknesses: list[str]
    improved_answer_outline: list[str] = Field(..., description="Bullet outline of a stronger answer.")
    next_steps: list[str]