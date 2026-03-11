# Interview Practice App 

A single-page Interview Practice App for **Software & AI Engineering** interview preparation, built with Streamlit, OpenAI, and Pydantic.

## Project Structure
```text
.
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Project dependencies
├── src/                        # Application source code
│   ├── config.py               # Settings and .env loading logic
│   ├── guards.py               # Input validation & per-session rate limiting
│   ├── interview_state.py      # Dataclasses for tracking turns and session status
│   ├── json_utils.py           # Robust JSON extraction and parsing from LLM outputs
│   ├── llm_client.py           # OpenAI client wrapper with retry logic and timeouts
│   ├── logging_setup.py        # Centralized loguru configuration
│   ├── pricing.py              # Token counting and cost estimation logic
│   ├── prompts.py              # Jinja2 template rendering and strategy mapping
│   ├── schemas.py              # Pydantic models for structured AI responses
│   └── ux_utils.py             # Helper functions for state management and error mapping
├── templates/                  # Jinja2 prompt templates
│   ├── system/                 # Strategy-specific system prompts
│   └── user/                   # User prompts for extraction, planning, and feedback
└── ...
```

## Technical Architecture
- **Streamlit Frontend:** A modern, interactive web interface with sidebar controls for deep LLM parameter tuning.
- **Jinja2 Templating Engine:** All prompts (system and user) are managed as `.j2` templates, allowing for modular, clean, and dynamic prompt construction.
- **Pydantic Validation:** Strict schema enforcement for JSON outputs (Interview Plans, Focus Areas, Final Feedback) to ensure reliability.
- **Robust Error Mapping:** A custom UX layer that translates backend exceptions (API timeouts, JSON failures, missing keys) into user-friendly guidance.
- **State Management:** Sophisticated session state handling to prevent double-click issues and maintain consistent interview flows.

## Setup

### 1) Install dependencies
Run the following command in your terminal:
```bash
pip install -r requirements.txt
```

### 2) Configure environment variables
Create a local `.env` file from the example:
```bash
cp .env.example .env
```
Edit `.env` and provide your OpenAI API key:
```text
OPENAI_API_KEY=your_openai_api_key_here
```
(Optional) Customize `OPENAI_PRICING_INPUT_PER_1M` and `OPENAI_PRICING_OUTPUT_PER_1M` for more accurate cost estimation.

### 3) Run the app
```bash
streamlit run app.py
```

## Features
- **Guided Mock Interview Flow:** Structured 5-question interview experience (**Start → Next → End**) with full transcript management.
- **Job Description Extraction:** Automatically extract role titles and target focus areas from any pasted job description using AI.
- **Advanced Prompt Engineering:** Access to 10+ prompt strategies (Zero-shot, Few-shot, Self-refinement, Maieutic, etc.) selectable in real-time.
- **UX Safety & Polish:**
  - **Reset Interview:** Dedicated action to cleanly wipe session state and start fresh.
  - **Settings Warning:** Real-time notification if critical interview parameters are changed mid-session.
  - **Single-Click UX:** Optimized interaction flow for seamless question transitions.
- **Tunable Generation Settings:** Granular control over Model, Temperature, Top-p, Penalties, Timeout, and Retries.
- **Approximate Cost Tracking:** Real-time estimation of input/output tokens and USD cost based on configurable pricing models.
- **Security Guardrails:** Built-in input validation, basic prompt-injection heuristics, and session-based rate limiting (10 calls/min).

## How to use

### 1. Preparation
- Fill in the **Role title** and **Focus areas**.
- **Optional:** Paste a **Job description** and click **Extract role title and focus areas** to let the AI populate the fields for you.

### 2. Guided Interview
- Configure your **Model**, **Difficulty**, and **Persona** in the sidebar.
- Click **Start interview**.
- Provide your answer in the text area and click **Next question**.
- After 5 turns (or earlier), click **End interview & get feedback**.
- View your **Final feedback (text)** and **Final feedback (JSON)**.

### 3. Structured Tools
- **Generate interview plan (JSON):** Create a downloadable roadmap for your preparation.
- **Download buttons:** Export any generated JSON (Plans or Feedback) directly to your local machine.

## Prompt strategies included
The app demonstrates various techniques from the "Prompt Engineering" field:
- **Zero-shot:** Direct instructions without examples.
- **Few-shot:** Providing style examples within the prompt.
- **Chain-of-Thought / Maieutic:** Forcing logical steps before reaching a conclusion.
- **Self-refinement:** An internal loop where the model critiques its own first draft.
- **Least-to-most:** Breaking down complex tasks into sequential sub-tasks.
- **Delimiters:** Using distinct markers to separate instructions from data.
- **Condition-checking:** Explicitly verifying requirements before proceeding.
- **Generated knowledge:** Prompting the model to recall relevant concepts first.
- **JSON-only enforcement:** Forcing structured outputs for tool integration.
- **App critic:** A self-assessment strategy where the AI reviews its own performance.

## Security & Reliability
- **Data Safety:** Never paste secrets (API keys, passwords) into the chat. The app uses environment variables for the main API key.
- **Stability:** The app uses a retry mechanism and specific timeouts to handle API instability gracefully.
- **Rate Limiting:** A simple indicator in the UI tracks your usage to help stay within API quotas.

## Disclaimer
- Token and cost estimates are approximate and intended for awareness only.
- Model behavior may vary depending on the chosen prompt strategy and parameters.