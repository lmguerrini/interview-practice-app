from __future__ import annotations

import time
from typing import Optional, cast

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class LLMClient:
    """
    Small wrapper around the OpenAI client to keep all API calls consistent.

    Why this exists:
    - Centralizes retry logic
    - Centralizes timeouts
    - Keeps Streamlit UI code clean and beginner-friendly
    """

    def __init__(self, api_key: str) -> None:
        api_key = (api_key or "").strip()
        if not api_key:
            raise ValueError("Missing OpenAI API key.")
        self._client = OpenAI(api_key=api_key)

    def generate_text(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 450,
        timeout_seconds: float = 30.0,
        retries: int = 2,
        retry_sleep_seconds: float = 1.25,
        response_format: Optional[dict] = None,
    ) -> str:
        """
        Make a single OpenAI call and return the final assistant text.
        """
        last_error: Optional[Exception] = None

        for attempt in range(retries + 1):
            try:
                logger.info(
                    "OpenAI call | model={} | temp={} | top_p={} | attempt={}/{}",
                    model,
                    temperature,
                    top_p,
                    attempt + 1,
                    retries + 1,
                )

                system_msg = cast(
                    ChatCompletionMessageParam,
                    cast(object, {"role": "system", "content": system_prompt}),
                )
                user_msg = cast(
                    ChatCompletionMessageParam,
                    cast(object, {"role": "user", "content": user_prompt}),
                )
                messages: list[ChatCompletionMessageParam] = [system_msg, user_msg]

                kwargs = {}
                if response_format is not None:
                    kwargs["response_format"] = response_format

                response = self._client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    max_tokens=max_output_tokens,
                    timeout=timeout_seconds,
                    messages=messages,
                    **kwargs,
                )

                text = (response.choices[0].message.content or "").strip()
                if not text:
                    raise RuntimeError("Empty response from model.")
                return text

            except Exception as exc:
                last_error = exc
                logger.exception("OpenAI call failed: {}", exc)

                if attempt < retries:
                    time.sleep(retry_sleep_seconds * (attempt + 1))

        raise RuntimeError(f"OpenAI request failed after retries: {last_error}")