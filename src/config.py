import os
from dotenv import load_dotenv


def load_settings() -> dict:
    """
    Load environment settings safely.

    We use python-dotenv so beginners can store environment variables
    in a local .env file while keeping secrets out of Git.
    """
    load_dotenv(override=False)

    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "").strip(),
    }