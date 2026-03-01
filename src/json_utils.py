from __future__ import annotations

import json
import re
from typing import Any


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_json_loose(text: str) -> dict[str, Any]:
    """
    Parse JSON from model output.

    Strategy:
    1) Try to parse the whole text as JSON.
    2) If that fails, extract the first {...} block and parse again.

    Raises ValueError if parsing fails.
    """
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty text; expected JSON.")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = _JSON_BLOCK_RE.search(raw)
        if not match:
            raise ValueError("Could not find a JSON object in the text.")
        return json.loads(match.group(0))