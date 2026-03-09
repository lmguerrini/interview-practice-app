from __future__ import annotations

import hashlib
import json
from typing import Any

import streamlit as st


def reset_interview() -> None:
    """
    Stop the active interview and clear all related state.
    """
    if "interview_session" in st.session_state:
        session = st.session_state["interview_session"]
        session.active = False
        session.turns = []

    # Clear feedback
    st.session_state.pop("final_feedback_text", None)
    st.session_state.pop("final_feedback_json", None)

    # Clear interview configuration signature
    st.session_state.pop("interview_config_signature", None)

    # Clear any per-turn answer fields stored in session_state
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("answer_turn_")]
    for key in keys_to_delete:
        del st.session_state[key]


def get_interview_config_signature(
    role: str,
    focus_areas: str,
    difficulty: str,
    prompt_strategy: str,
    response_style: str,
    persona: str,
    job_description: str,
) -> str:
    """
    Create a stable hash of the interview configuration.
    """
    config = {
        "role": role.strip(),
        "focus_areas": focus_areas.strip(),
        "difficulty": difficulty,
        "prompt_strategy": prompt_strategy,
        "response_style": response_style,
        "persona": persona,
        "job_description": job_description.strip(),
    }
    config_json = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_json.encode("utf-8")).hexdigest()


def format_error_message(exc: Exception) -> str:
    """
    Map common exceptions to user-friendly messages.
    """
    msg = str(exc).lower()

    if "missing openai api key" in msg or "api_key" in msg:
        return "OpenAI API key is missing. Please check your .env file or environment variables."

    if "timeout" in msg:
        return "The request timed out. Please try again or increase the timeout in the sidebar."

    if "empty response" in msg:
        return "The AI model returned an empty response. Please try again."

    if "json" in msg or "structured output" in msg or "parse_json_loose" in msg:
        return "Failed to parse a structured response from the AI. This can happen occasionally; please try again."

    if "rate limit" in msg:
        return "You've reached the AI provider's rate limit. Please wait a moment before trying again."

    # Fallback
    return f"An unexpected error occurred: {exc}"
