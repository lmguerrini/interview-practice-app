# Interview Practice App 

A single-page Interview Practice App designed for **Software & AI Engineering** interview preparation.

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
Open `.env` and set your key:
```
OPENAI_API_KEY=your_openai_api_key_here
```
### 3) Run the app
```
streamlit run app.py
```

## Security Notes
- Never paste secrets (API keys, passwords) into the app UI.
- `.env` is intentionally git-ignored.