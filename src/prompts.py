from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined,
)


def _render(template_name: str, **context: object) -> str:
    """
    Render a Jinja template and return the stripped text.
    """
    template = _env.get_template(template_name)
    return template.render(**context).strip()


def _tone_instruction(persona: str) -> str:
    """
    Return a short tone instruction based on the selected interviewer persona.
    """
    tone_map = {
        "Neutral": "Be professional, clear, and constructive.",
        "Strict": "Be demanding and direct. Push for specifics and correctness.",
        "Friendly": "Be encouraging and supportive, but still honest.",
    }
    return tone_map.get(persona, tone_map["Neutral"])


def system_prompt_zero_shot(persona: str) -> str:
    return _render("system/zero_shot.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_few_shot(persona: str) -> str:
    return _render("system/few_shot.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_delimiters(persona: str) -> str:
    return _render("system/delimiters.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_condition_checking(persona: str) -> str:
    return _render("system/condition_checking.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_generated_knowledge(persona: str) -> str:
    return _render("system/generated_knowledge.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_self_refinement(persona: str) -> str:
    return _render("system/self_refinement.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_least_to_most(persona: str) -> str:
    return _render("system/least_to_most.j2", tone_instruction=_tone_instruction(persona))


def system_prompt_maieutic(persona: str) -> str:
    return _render("system/maieutic.j2", tone_instruction=_tone_instruction(persona))


PROMPT_STRATEGIES = {
    "Zero-shot (baseline)": system_prompt_zero_shot,
    "Few-shot (style example)": system_prompt_few_shot,
    "Delimiters (structured input)": system_prompt_delimiters,
    "Condition-checking (requirements)": system_prompt_condition_checking,
    "Generated knowledge (internal checklist)": system_prompt_generated_knowledge,
    "Self-refinement (draft → revise)": system_prompt_self_refinement,
    "Least-to-most (scalable depth)": system_prompt_least_to_most,
    "Maieutic (Socratic reasoning)": system_prompt_maieutic,
}


def user_prompt_first_question(
        role: str,
        focus_areas: str,
        difficulty: str,
        job_description: str,
        response_style: str,
) -> str:
    return _render(
        "user/first_question.j2",
        role=(role or "").strip(),
        focus_areas=(focus_areas or "").strip(),
        difficulty=(difficulty or "").strip(),
        job_description=(job_description or "").strip(),
        response_style=(response_style or "").strip(),
    )


def system_prompt_json_only() -> str:
    return _render("system/json_only.j2")


def user_prompt_interview_plan_json(
        *,
        role: str,
        focus_areas: str,
        difficulty: str,
        strategy_name: str,
        persona: str,
) -> str:
    return _render(
        "user/interview_plan_json.j2",
        role=role,
        focus_areas=focus_areas,
        difficulty=difficulty,
        strategy_name=strategy_name,
        persona=persona,
    )


def user_prompt_final_feedback_json(
        *,
        role: str,
        difficulty: str,
        focus_areas: str,
        job_description: str,
        question: str,
        answer: str,
) -> str:
    return _render(
        "user/final_feedback_json.j2",
        role=role,
        difficulty=difficulty,
        focus_areas=focus_areas,
        job_description=job_description,
        question=question,
        answer=answer,
    )


def user_prompt_final_feedback_json_from_history(
        *,
        role: str,
        difficulty: str,
        focus_areas: str,
        job_description: str,
        history: list[dict[str, str]],
) -> str:
    history_lines = []
    for i, item in enumerate(history, start=1):
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()
        history_lines.append(f"Q{i}: {q}\nA{i}: {a}\n")

    history_block = "\n".join(history_lines).strip()

    return _render(
        "user/final_feedback_json_from_history.j2",
        role=role,
        difficulty=difficulty,
        focus_areas=focus_areas,
        job_description=job_description,
        history_block=history_block,
    )


def user_prompt_next_question(
        *,
        role: str,
        focus_areas: str,
        difficulty: str,
        job_description: str,
        response_style: str,
        history: list[dict[str, str]],
) -> str:
    history_lines = []
    for i, item in enumerate(history, start=1):
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()
        history_lines.append(f"Q{i}: {q}\nA{i}: {a}\n")
    history_block = "\n".join(history_lines).strip()

    return _render(
        "user/next_question.j2",
        role=role,
        focus_areas=focus_areas,
        difficulty=difficulty,
        job_description=job_description,
        response_style=response_style,
        history_block=history_block,
    )


def system_prompt_final_feedback_text() -> str:
    return _render("system/final_feedback_text.j2")


def user_prompt_final_feedback_text(
        *,
        role: str,
        difficulty: str,
        focus_areas: str,
        job_description: str,
        history: list[dict[str, str]],
) -> str:
    history_lines = []
    for i, item in enumerate(history, start=1):
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()
        history_lines.append(f"Q{i}: {q}\nA{i}: {a}\n")

    history_block = "\n".join(history_lines).strip()

    return _render(
        "user/final_feedback_text.j2",
        role=role,
        difficulty=difficulty,
        focus_areas=focus_areas,
        job_description=job_description,
        history_block=history_block,
    )


def system_prompt_app_critic() -> str:
    return _render("system/app_critic.j2")


def user_prompt_app_critic(
        *,
        model: str,
        temperature: float,
        strategy_name: str,
        difficulty: str,
        response_style: str,
        persona: str,
) -> str:
    return _render(
        "user/app_critic.j2",
        model=model,
        temperature=temperature,
        strategy_name=strategy_name,
        difficulty=difficulty,
        response_style=response_style,
        persona=persona,
    )


def _history_to_block(history: list[dict[str, str]]) -> str:
    """
    Convert interview history into a readable Q/A transcript block for prompts.
    """
    history_lines = []
    for i, item in enumerate(history, start=1):
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()
        history_lines.append(f"Q{i}: {q}\nA{i}: {a}\n")
    return "\n".join(history_lines).strip()


def user_prompt_extract_focus_areas_json(*, role: str, job_description: str) -> str:
    return _render(
        "user/extract_focus_areas_json.j2",
        role=role,
        job_description=job_description,
    )
