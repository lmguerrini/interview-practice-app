from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostEstimate:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    note: str


# IMPORTANT:
# Token pricing changes over time. These values are placeholders for educational purposes.
# Update them to match the official pricing for your chosen models if needed.
#
# Units: USD per 1,000,000 tokens
PRICING_USD_PER_1M_INPUT = {
    "gpt-4.1": 0.0,
    "gpt-4.1-mini": 0.0,
    "gpt-4.1-nano": 0.0,
    "gpt-4o": 0.0,
    "gpt-4o-mini": 0.0,
}
PRICING_USD_PER_1M_OUTPUT = {
    "gpt-4.1": 0.0,
    "gpt-4.1-mini": 0.0,
    "gpt-4.1-nano": 0.0,
    "gpt-4o": 0.0,
    "gpt-4o-mini": 0.0,
}


def approx_tokens_from_text(text: str, chars_per_token: int = 4) -> int:
    """
    Rough token estimation from character count.

    A commonly used approximation is ~4 characters per token for English text.
    This is not exact, but it's good enough to reason about relative cost.
    """
    text = text or ""
    if chars_per_token <= 0:
        chars_per_token = 4
    return max(1, len(text) // chars_per_token)


def estimate_call_cost_usd(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_tokens: int,
) -> CostEstimate:
    """
    Estimate cost for one call based on approximate token usage and a per-model price table.
    """
    input_tokens = approx_tokens_from_text(system_prompt) + approx_tokens_from_text(user_prompt)
    output_tokens = max(1, int(output_tokens))
    total_tokens = input_tokens + output_tokens

    in_price = PRICING_USD_PER_1M_INPUT.get(model, 0.0)
    out_price = PRICING_USD_PER_1M_OUTPUT.get(model, 0.0)

    estimated_cost = (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price

    note = (
        "Token + cost are approximate. Update PRICING_USD_PER_1M_* in src/pricing.py "
        "to match official pricing if you want exact numbers."
    )
    return CostEstimate(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost,
        note=note,
    )