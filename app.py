import json
import time
import streamlit as st

from src.config import load_settings
from src.logging_setup import setup_logging
from src.llm_client import LLMClient
from src.prompts import (
    PROMPT_STRATEGIES,
    system_prompt_final_feedback_text,
    system_prompt_json_only,
    user_prompt_final_feedback_json_from_history,
    user_prompt_final_feedback_text,
    user_prompt_first_question,
    user_prompt_interview_plan_json,
    user_prompt_next_question,
)
from src.guards import rate_limit_ok, validate_inputs
from src.pricing import estimate_call_cost_usd
from src.interview_state import InterviewSession, Turn
from src.schemas import InterviewPlan
from src.json_utils import parse_json_loose
from src.schemas import FinalFeedback


def render_sidebar(settings: dict) -> dict:
    """
    Render the sidebar controls and return the UI-selected settings.

    Keeping this logic in a dedicated function makes the UI easier to evolve
    when we add more model settings (temperature, top_p, penalties, etc.).
    """
    st.sidebar.title("Interview Practice App")

    st.sidebar.markdown("### Model & Generation Settings")
    model = st.sidebar.selectbox(
        "Model",
        options=[
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ],
        index=4,  # Default to cost-effective
        help="Pick one of the allowed models for this project.",
    )

    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more deterministic.",
    )

    top_p = st.sidebar.slider(
        "Top-p",
        min_value=0.1,
        max_value=1.0,
        value=1.0,
        step=0.1,
        help="Nucleus sampling. Lower values make output more focused.",
    )

    presence_penalty = st.sidebar.slider(
        "Presence penalty",
        min_value=-2.0,
        max_value=2.0,
        value=0.0,
        step=0.5,
        help="Encourages introducing new topics (higher) vs staying on existing ones (lower).",
    )

    frequency_penalty = st.sidebar.slider(
        "Frequency penalty",
        min_value=-2.0,
        max_value=2.0,
        value=0.0,
        step=0.5,
        help="Reduces repetition when higher.",
    )

    max_output_tokens = st.sidebar.slider(
        "Max output tokens",
        min_value=80,
        max_value=900,
        value=250,
        step=10,
        help="Upper bound for the model output length.",
    )

    timeout_seconds = st.sidebar.slider(
        "Timeout (seconds)",
        min_value=5,
        max_value=90,
        value=30,
        step=5,
        help="Request timeout for the API call.",
    )

    retries = st.sidebar.slider(
        "Retries",
        min_value=0,
        max_value=4,
        value=2,
        step=1,
        help="How many times to retry after a failed request.",
    )

    st.sidebar.markdown("### Prompt strategy")
    strategy_names = list(PROMPT_STRATEGIES.keys())
    prompt_strategy = st.sidebar.selectbox(
        "Strategy",
        options=strategy_names,
        index=0,
        help="Different prompt-engineering techniques for the system prompt.",
    )

    st.sidebar.markdown("### Interview Settings")
    track = st.sidebar.selectbox(
        "Track",
        options=["Software Engineering", "AI Engineering"],
        index=1,
        help="Choose the domain you want to practice for.",
    )

    difficulty = st.sidebar.selectbox(
        "Difficulty",
        options=["Easy", "Medium", "Hard"],
        index=1,
        help="Controls how challenging the questions will be.",
    )

    response_style = st.sidebar.selectbox(
        "Response style",
        options=["Brief", "Detailed"],
        index=0,
        help="Brief = short question. Detailed = realistic context & constraints (still one question).",
    )

    persona = st.sidebar.selectbox(
        "Interviewer persona",
        options=["Neutral", "Strict", "Friendly"],
        index=0,
        help="Controls the interviewer tone.",
    )


    return {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "max_output_tokens": int(max_output_tokens),
        "timeout_seconds": float(timeout_seconds),
        "retries": int(retries),
        "prompt_strategy": prompt_strategy,
        "track": track,
        "difficulty": difficulty,
        "response_style": response_style,
        "persona": persona,
        "openai_api_key_present": bool(settings.get("OPENAI_API_KEY")),
    }


def main() -> None:
    """
    Streamlit entry point.

    The app builds an interview practice UI and calls the OpenAI API to generate questions.
    """
    setup_logging()
    settings = load_settings()

    st.set_page_config(
        page_title="Interview Practice App",
        page_icon="",
        layout="wide",
    )

    ui_settings = render_sidebar(settings)

    st.title("Interview Practice App")
    st.write(
        "Practice for Software & AI Engineering interviews using prompt strategies, safety guardrails, and tunable LLM settings."
    )

    # Show API key status without revealing it.
    if ui_settings["openai_api_key_present"]:
        st.success("OpenAI API key detected (from environment).")
    else:
        st.warning(
            "No OpenAI API key found. Create a local .env file with OPENAI_API_KEY to enable AI features."
        )
        st.code("OPENAI_API_KEY=your_api_key_here", language="bash")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Your target role")
        role = st.text_input(
            "Role title",
            value="AI Engineer",
            help="Examples: Backend Engineer, AI Engineer, ML Engineer, Software Engineer.",
            max_chars=80,
        )

        st.subheader("Focus areas")
        focus_areas = st.text_area(
            "Skills / topics to practice",
            value="Python, APIs, LLM prompting, debugging, system design basics",
            help="Comma-separated topics are fine. Keep it concise.",
            height=120,
            max_chars=500,
        )

    with col2:
        st.subheader("Job description (optional)")
        job_description = st.text_area(
            "Paste the job description (optional)",
            value="",
            help="Optional. We'll use it to tailor questions and feedback later.",
            height=220,
            max_chars=3000,
        )

    # --- Cost estimate (sidebar, always visible) ---
    try:
        strategy_fn = PROMPT_STRATEGIES[ui_settings["prompt_strategy"]]
        system_prompt_preview = strategy_fn(ui_settings["persona"])
        user_prompt_preview = user_prompt_first_question(
            role=role,
            focus_areas=focus_areas,
            difficulty=ui_settings["difficulty"],
            job_description=job_description,
            response_style=ui_settings["response_style"],
        )

        estimate = estimate_call_cost_usd(
            model=ui_settings["model"],
            system_prompt=system_prompt_preview,
            user_prompt=user_prompt_preview,
            output_tokens=ui_settings["max_output_tokens"],
            pricing_input_per_1m=settings.get("OPENAI_PRICING_INPUT_PER_1M", {}),
            pricing_output_per_1m=settings.get("OPENAI_PRICING_OUTPUT_PER_1M", {}),
        )

        st.sidebar.markdown("---")
        st.sidebar.markdown("### Cost estimate (approx.)")
        st.sidebar.write(f"Input tokens: **~{estimate.input_tokens}**")
        st.sidebar.write(f"Output tokens: **~{estimate.output_tokens}**")
        st.sidebar.write(f"Total tokens: **~{estimate.total_tokens}**")
        st.sidebar.write(f"Estimated cost: **${estimate.estimated_cost_usd:.6f}**")
        st.sidebar.caption(estimate.note)
    except Exception:
        pass

    st.sidebar.caption("Security note: never paste secrets into the chat.")

    st.markdown("---")
    st.header("Interview plan (JSON)")

    plan_disabled = not ui_settings["openai_api_key_present"]
    if st.button("Generate interview plan (JSON)", disabled=plan_disabled):
        guard = validate_inputs(role, focus_areas, job_description)
        if not guard.allowed:
            st.warning(guard.user_message)
        else:
            ok, msg = rate_limit_ok(timestamps=st.session_state["call_timestamps"])
            if not ok:
                st.warning(msg)
            else:
                try:
                    client = LLMClient(api_key=settings["OPENAI_API_KEY"])
                    system_prompt = system_prompt_json_only()
                    user_prompt = user_prompt_interview_plan_json(
                        role=role,
                        focus_areas=focus_areas,
                        difficulty=ui_settings["difficulty"],
                        strategy_name=ui_settings["prompt_strategy"],
                        persona=ui_settings["persona"],
                    )

                    with st.spinner("Generating interview plan (JSON)..."):  # type: ignore[call-arg]
                        raw = client.generate_text(
                            model=ui_settings["model"],
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            temperature=0.2,
                            top_p=1.0,
                            presence_penalty=0.0,
                            frequency_penalty=0.0,
                            max_output_tokens=650,
                            timeout_seconds=ui_settings.get("timeout_seconds", 30.0),
                            retries=ui_settings.get("retries", 2),
                        )

                    data = parse_json_loose(raw)
                    plan = InterviewPlan.model_validate(data).model_dump()

                    # Keep the plan aligned with the guided interview length (5 questions).
                    plan["total_questions"] = 5

                    st.session_state["interview_plan_json"] = plan

                except Exception as exc:
                    st.error(f"Could not generate interview plan JSON. Error: {exc}")

    if "interview_plan_json" in st.session_state:
        plan_obj = st.session_state["interview_plan_json"]
        plan_text = json.dumps(plan_obj, ensure_ascii=False, indent=2)

        st.download_button(
            label="Download interview_plan.json",
            data=plan_text,
            file_name="interview_plan.json",
            mime="application/json",
        )

        st.markdown("Copy-ready JSON:")
        st.code(plan_text, language="json")

        st.markdown("Preview:")
        st.json(plan_obj)

    st.markdown("---")

    # Initialize rate limiting state for this browser session.
    if "call_timestamps" not in st.session_state:
        st.session_state["call_timestamps"] = []

    # Initialize guided interview session state.
    if "interview_session" not in st.session_state:
        st.session_state["interview_session"] = InterviewSession(active=False, max_questions=5)

    session: InterviewSession = st.session_state["interview_session"]

    # Rate-limit indicator
    now_ts = time.time()
    recent_calls = [t for t in st.session_state["call_timestamps"] if now_ts - t <= 60]
    st.caption(f"Rate limit: {len(recent_calls)}/10 calls in the last 60 seconds.")

    st.header("Mock interview (guided)")

    start_disabled = not ui_settings["openai_api_key_present"]
    start_col, next_col, end_col = st.columns(3)

    with start_col:
        if st.button("Start interview", type="primary", disabled=start_disabled):
            guard = validate_inputs(role, focus_areas, job_description)
            if not guard.allowed:
                st.warning(guard.user_message)
            else:
                ok, msg = rate_limit_ok(timestamps=st.session_state["call_timestamps"])
                if not ok:
                    st.warning(msg)
                else:
                    try:
                        session.active = True
                        session.max_questions = 5
                        session.turns = []
                        st.session_state.pop("final_feedback_text", None)

                        client = LLMClient(api_key=settings["OPENAI_API_KEY"])
                        strategy_fn = PROMPT_STRATEGIES[ui_settings["prompt_strategy"]]
                        system_prompt = strategy_fn(ui_settings["persona"])

                        user_prompt = user_prompt_first_question(
                            role=role,
                            focus_areas=focus_areas,
                            difficulty=ui_settings["difficulty"],
                            job_description=job_description,
                            response_style=ui_settings["response_style"],
                        )

                        with st.spinner("Starting interview..."):  # type: ignore[call-arg]
                            first_q = client.generate_text(
                                model=ui_settings["model"],
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                temperature=ui_settings["temperature"],
                                top_p=ui_settings.get("top_p", 1.0),
                                presence_penalty=ui_settings.get("presence_penalty", 0.0),
                                frequency_penalty=ui_settings.get("frequency_penalty", 0.0),
                                max_output_tokens=ui_settings.get("max_output_tokens", 250),
                                timeout_seconds=ui_settings.get("timeout_seconds", 30.0),
                                retries=ui_settings.get("retries", 2),
                            )

                        session.turns.append(Turn(question=first_q, answer=""))
                    except Exception as exc:
                        st.error(f"Could not start interview. Error: {exc}")

    # --- Guided interview: current question + answer + actions (FORM) ---
    if session.active and session.turns:
        current_q = session.turns[-1].question
        st.subheader("Current question")
        st.write(current_q)

        turn_number = len(session.turns)  # 1-based
        answer_key = f"answer_turn_{turn_number}"

        if answer_key not in st.session_state:
            st.session_state[answer_key] = session.turns[-1].answer

        with st.form(key=f"answer_form_turn_{turn_number}", clear_on_submit=False):
            st.text_area(
                "Your answer",
                key=answer_key,
                height=180,
                max_chars=3000,
                help="Write your answer, then click Next question or End interview.",
            )

            col_left, col_spacer, col_right = st.columns([2, 5, 2])
            with col_left:
                submit_next = st.form_submit_button("Next question")
            with col_right:
                submit_end = st.form_submit_button("End interview & get feedback")

        # Handle submit actions (exactly one will be True per submit)
        if submit_next or submit_end:
            current_answer = (st.session_state.get(answer_key, "") or "").strip()
            session.turns[-1].answer = current_answer

            if not current_answer:
                st.warning("Please write an answer before continuing.")
            else:
                ok, msg = rate_limit_ok(timestamps=st.session_state["call_timestamps"])
                if not ok:
                    st.warning(msg)
                else:
                    try:
                        client = LLMClient(api_key=settings["OPENAI_API_KEY"])
                        history = [{"question": t.question, "answer": t.answer} for t in session.turns]

                        if submit_next:
                            if session.is_complete():
                                st.warning("You have reached the maximum number of questions. Please end the interview.")
                            else:
                                strategy_fn = PROMPT_STRATEGIES[ui_settings["prompt_strategy"]]
                                system_prompt = strategy_fn(ui_settings["persona"])

                                user_prompt = user_prompt_next_question(
                                    role=role,
                                    focus_areas=focus_areas,
                                    difficulty=ui_settings["difficulty"],
                                    job_description=job_description,
                                    response_style=ui_settings["response_style"],
                                    history=history,
                                )

                                with st.spinner("Generating next question..."):  # type: ignore[call-arg]
                                    next_q = client.generate_text(
                                        model=ui_settings["model"],
                                        system_prompt=system_prompt,
                                        user_prompt=user_prompt,
                                        temperature=ui_settings["temperature"],
                                        top_p=ui_settings.get("top_p", 1.0),
                                        presence_penalty=ui_settings.get("presence_penalty", 0.0),
                                        frequency_penalty=ui_settings.get("frequency_penalty", 0.0),
                                        max_output_tokens=ui_settings.get("max_output_tokens", 250),
                                        timeout_seconds=ui_settings.get("timeout_seconds", 30.0),
                                        retries=ui_settings.get("retries", 2),
                                    )

                                session.turns.append(Turn(question=next_q, answer=""))

                        if submit_end:
                            system_prompt = system_prompt_final_feedback_text()
                            user_prompt = user_prompt_final_feedback_text(
                                role=role,
                                difficulty=ui_settings["difficulty"],
                                focus_areas=focus_areas,
                                job_description=job_description,
                                history=history,
                            )

                            with st.spinner("Generating final feedback..."):  # type: ignore[call-arg]
                                feedback_text = client.generate_text(
                                    model=ui_settings["model"],
                                    system_prompt=system_prompt,
                                    user_prompt=user_prompt,
                                    temperature=0.2,
                                    top_p=1.0,
                                    presence_penalty=0.0,
                                    frequency_penalty=0.0,
                                    max_output_tokens=900,
                                    timeout_seconds=ui_settings.get("timeout_seconds", 30.0),
                                    retries=ui_settings.get("retries", 2),
                                )

                            json_system = system_prompt_json_only()
                            json_user = user_prompt_final_feedback_json_from_history(
                                role=role,
                                difficulty=ui_settings["difficulty"],
                                focus_areas=focus_areas,
                                job_description=job_description,
                                history=history,
                            )

                            with st.spinner("Generating final feedback (JSON)..."):  # type: ignore[call-arg]
                                raw_json = client.generate_text(
                                    model=ui_settings["model"],
                                    system_prompt=json_system,
                                    user_prompt=json_user,
                                    temperature=0.2,
                                    top_p=1.0,
                                    presence_penalty=0.0,
                                    frequency_penalty=0.0,
                                    max_output_tokens=900,
                                    timeout_seconds=ui_settings.get("timeout_seconds", 30.0),
                                    retries=ui_settings.get("retries", 2),
                                )

                            data = parse_json_loose(raw_json)
                            feedback_json = FinalFeedback.model_validate(data).model_dump()

                            st.session_state["final_feedback_text"] = feedback_text
                            st.session_state["final_feedback_json"] = feedback_json
                            session.active = False

                    except Exception as exc:
                        st.error(f"Interview action failed. Error: {exc}")

    # Transcript + outputs (must be inside main())
    if session.turns:
        st.markdown("---")
        st.subheader("Transcript")
        for i, t in enumerate(session.turns, start=1):
            st.markdown(f"**Q{i}:** {t.question}")
            if t.answer.strip():
                st.markdown(f"**A{i}:** {t.answer}")
            else:
                st.markdown("**A:** _(no answer yet)_")

    if "final_feedback_text" in st.session_state:
        st.markdown("---")
        st.subheader("Final feedback")
        st.write(st.session_state["final_feedback_text"])

    if "final_feedback_json" in st.session_state:
        st.subheader("Final feedback (JSON)")

        final_json_obj = st.session_state["final_feedback_json"]
        final_json_text = json.dumps(final_json_obj, ensure_ascii=False, indent=2)

        st.download_button(
            label="Download final_feedback.json",
            data=final_json_text,
            file_name="final_feedback.json",
            mime="application/json",
        )

        st.markdown("Copy-ready JSON:")
        st.code(final_json_text, language="json")

        st.markdown("Preview:")
        st.json(final_json_obj)

    # Store inputs in session state for the upcoming multi-turn chat logic.
    st.session_state["role"] = role
    st.session_state["focus_areas"] = focus_areas
    st.session_state["job_description"] = job_description
    st.session_state["ui_settings"] = ui_settings

if __name__ == "__main__":
    main()