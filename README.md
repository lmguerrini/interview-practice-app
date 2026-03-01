# Interview Practice App 

A single-page Interview Practice App for **Software & AI Engineering** interview preparation.

## Features
- Guided mock interview flow (**Start → Next → End**) with a 5-question interview transcript
- Multiple prompt strategies (prompt engineering techniques) selectable in the UI
- Tunable OpenAI generation settings (temperature, top-p, penalties, max tokens, timeout, retries)
- Security guardrails: input validation, basic prompt-injection heuristics, per-session rate limiting
- Structured outputs (Pydantic-validated):
  - `InterviewPlan` JSON + download buttons for copy-safe export
  - `FinalFeedback` JSON + download buttons for copy-safe export
- Approximate token + cost estimation (pricing configured via `.env`)

## Setup

### 1) Install dependencies
Run the following command in your terminal:
```
pip install -r requirements.txt
```
### 2) Configure environment variables (local only)
Create a local `.env` file (never commit it):
```
cp .env.example .env
```
Edit `.env` and set:
```
OPENAI_API_KEY=your_openai_api_key_here
```

(Optional) Enable cost estimation by setting model pricing variables in `.env` (see `.env.example`).

### 3) Run the app
```
streamlit run app.py
```


## How to use
### Guided interview
1. Fill in **Role**, **Focus areas**, and (optionally) **Job description**
2. Choose **Model**, **Difficulty**, **Persona**, **Prompt strategy**, and **Response style**
3. Click **Start interview**
4. Write an answer and click **Next question**
5. Click **End interview & get feedback** to generate:
   - final feedback (text)
   - final feedback (JSON) + download

### Structured JSON outputs
- Click **Generate interview plan (JSON)** to generate and download an `interview_plan.json`
- Use **Final feedback (JSON)** after the interview to download `final_feedback.json`

### Quick self-review
- Click **Critique this app (quick review)** to generate structured critique sections:
  `USABILITY`, `SECURITY`, `PROMPT_ENGINEERING`, `NEXT_IMPROVEMENTS`

## Prompt strategies included
- Zero-shot (baseline)
- Few-shot (style example)
- Delimiters (structured input sections)
- Condition-checking (requirements verification)
- Generated knowledge (internal checklist)
- Self-refinement (draft → critique → revise)
- Least-to-most (scalable depth)
- Maieutic / Socratic prompting

## Security notes
- Never paste secrets (API keys, passwords) into the app UI.
- `.env` is intentionally git-ignored.
- The app applies input validation + basic prompt-injection heuristics.
- A simple per-session rate limiter helps prevent accidental spam and unexpected costs.

## Disclaimer
- Token and cost estimates are approximate.
- Model pricing can change; verify values on the official OpenAI pricing page when needed.