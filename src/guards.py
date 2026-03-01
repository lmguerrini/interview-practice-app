from __future__ import annotations

import re
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    user_message: str


_INJECTION_PATTERNS = [
    r"\bignore (all|any|previous) instructions\b",
    r"\bdisregard (the )?system\b",
    r"\breveal (the )?system prompt\b",
    r"\bshow (me )?your hidden instructions\b",
    r"\bdeveloper message\b",
    r"\byou are now\b",
]


def validate_inputs(role: str, focus_areas: str, job_description: str) -> GuardResult:
    """
    Validate user inputs to reduce misuse, injection attempts, and overly large prompts.
    """
    role = (role or "").strip()
    focus_areas = (focus_areas or "").strip()
    job_description = (job_description or "").strip()

    if not role:
        return GuardResult(False, "Please provide a role title (e.g., 'AI Engineer').")

    if len(role) > 80:
        return GuardResult(False, "Role title is too long. Please keep it under 80 characters.")

    if len(focus_areas) > 500:
        return GuardResult(False, "Focus areas are too long. Please keep them under 500 characters.")

    if len(job_description) > 3000:
        return GuardResult(False, "Job description is too long. Please keep it under 3000 characters.")

    combined = f"{role}\n{focus_areas}\n{job_description}".lower()

    for pat in _INJECTION_PATTERNS:
        if re.search(pat, combined):
            return GuardResult(
                False,
                "Your input looks like it may contain prompt-injection instructions. "
                "Please remove them and try again.",
            )

    return GuardResult(True, "")


def rate_limit_ok(
    *,
    timestamps: list[float],
    max_calls: int = 10,
    window_seconds: int = 60,
) -> tuple[bool, str]:
    """
    Simple sliding-window rate limiter for the current Streamlit session.
    """
    now = time.time()
    recent = [t for t in timestamps if now - t <= window_seconds]
    timestamps[:] = recent

    if len(recent) >= max_calls:
        return False, "Rate limit reached. Please wait a moment and try again."

    timestamps.append(now)
    return True, ""