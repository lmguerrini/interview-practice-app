# 👨🏼‍🏫 Interview Practice App

A single-page Interview Practice App designed specifically for **Software & AI Engineering** interview preparation.

---

## 🛠️ Setup & Installation

Follow these steps to get your environment ready:

### 1. Install Dependencies
Run the following command in your terminal:
```bash
pip install -r requirements.txt
```
### 2. Configure Environment Variables

Create a local .env file (ensure this is never committed to your repository):
```
bash streamlit run app.py
```


### Security Notes
- Do not paste secrets in the chat.
- The app reads `OPENAI_API_KEY` only from environment variables / `.env`.