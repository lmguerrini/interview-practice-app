from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Turn:
    """
    One interview turn: a question and the candidate's answer.
    """
    question: str
    answer: str = ""


@dataclass
class InterviewSession:
    """
    Holds the state of a guided mock interview.

    We keep it minimal and session-state friendly:
    - active: interview started
    - max_questions: fixed length (5 for this project)
    - turns: list of Q/A pairs
    """
    active: bool = False
    max_questions: int = 5
    turns: list[Turn] = field(default_factory=list)

    def is_complete(self) -> bool:
        return len(self.turns) >= self.max_questions

    def current_turn_index(self) -> int:
        return max(0, len(self.turns) - 1)