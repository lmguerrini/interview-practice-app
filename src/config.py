import os
from dotenv import load_dotenv


def _get_env_float(name: str, default: float = 0.0) -> float:
    """
    Read a float from environment variables safely.
    """
    raw = os.getenv(name, "").strip()
    if raw == "":
        return float(default)
    try:
        return float(raw)
    except ValueError:
        return float(default)


def load_settings() -> dict:
    """
    Load environment settings safely.

    We use python-dotenv so beginners can store environment variables
    in a local .env file while keeping secrets out of Git.
    """
    load_dotenv(override=False)

    pricing_input_per_1m = {
        "gpt-4o-mini": _get_env_float("OPENAI_PRICE_GPT_4O_MINI_INPUT_PER_1M", 0.0),
        "gpt-4o": _get_env_float("OPENAI_PRICE_GPT_4O_INPUT_PER_1M", 0.0),
        "gpt-4.1": _get_env_float("OPENAI_PRICE_GPT_4_1_INPUT_PER_1M", 0.0),
        "gpt-4.1-mini": _get_env_float("OPENAI_PRICE_GPT_4_1_MINI_INPUT_PER_1M", 0.0),
        "gpt-4.1-nano": _get_env_float("OPENAI_PRICE_GPT_4_1_NANO_INPUT_PER_1M", 0.0),
    }

    pricing_output_per_1m = {
        "gpt-4o-mini": _get_env_float("OPENAI_PRICE_GPT_4O_MINI_OUTPUT_PER_1M", 0.0),
        "gpt-4o": _get_env_float("OPENAI_PRICE_GPT_4O_OUTPUT_PER_1M", 0.0),
        "gpt-4.1": _get_env_float("OPENAI_PRICE_GPT_4_1_OUTPUT_PER_1M", 0.0),
        "gpt-4.1-mini": _get_env_float("OPENAI_PRICE_GPT_4_1_MINI_OUTPUT_PER_1M", 0.0),
        "gpt-4.1-nano": _get_env_float("OPENAI_PRICE_GPT_4_1_NANO_OUTPUT_PER_1M", 0.0),
    }

    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "").strip(),
        "OPENAI_PRICING_INPUT_PER_1M": pricing_input_per_1m,
        "OPENAI_PRICING_OUTPUT_PER_1M": pricing_output_per_1m,
    }