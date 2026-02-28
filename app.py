import streamlit as st

from src.config import load_settings
from src.logging_setup import setup_logging


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
        ],
        index=3,  # Default to cost-effective
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
        help="Controls how challenging the questions will be (implemented later).",
    )

    persona = st.sidebar.selectbox(
        "Interviewer persona",
        options=["Neutral", "Strict", "Friendly"],
        index=0,
        help="Controls the interviewer tone (implemented later).",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Security note: never paste secrets into the chat.")

    return {
        "model": model,
        "temperature": temperature,
        "track": track,
        "difficulty": difficulty,
        "persona": persona,
        "openai_api_key_present": bool(settings.get("OPENAI_API_KEY")),
    }


def main() -> None:
    """
    Streamlit entry point.

    Phase 1 goal:
    - Build a clean, stable UI skeleton
    - Load env-based settings safely
    - Prepare session state for upcoming multi-turn chat
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

    st.markdown("---")
    st.subheader("Next step")
    st.info(
        "Phase 2: we will connect to the OpenAI API and generate the first interview question."
    )

    # Store inputs in session state for the upcoming multi-turn chat logic.
    st.session_state["role"] = role
    st.session_state["focus_areas"] = focus_areas
    st.session_state["job_description"] = job_description
    st.session_state["ui_settings"] = ui_settings


if __name__ == "__main__":
    main()