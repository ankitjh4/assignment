"""Grounding helpers: prompt-injection detection and unknown-question handling."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


INJECTION_PATTERNS = [
    r"ignore (?:all )?(?:previous|above|prior) (?:instructions|prompts)",
    r"forget (?:everything|the above|all instructions)",
    r"reveal (?:the )?system prompt",
    r"print (?:the )?system prompt",
    r"act as (?:a |an )?(?:different|new) (?:persona|assistant)",
    r"you are no longer .*drinkoo",
    r"jailbreak",
    r"developer mode",
    r"disregard (?:the )?(?:rules|instructions|prompt|policy)",
]

INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


REFUSAL_MESSAGE = (
    "I can only help with DRINKOO questions grounded in our catalog and support content."
)

UNKNOWN_MESSAGE = (
    "I don't have that information in the DRINKOO knowledge base yet."
)


@dataclass
class GroundingDecision:
    refuse: bool
    reason: Optional[str]


def detect_injection(user_message: str) -> GroundingDecision:
    if not user_message:
        return GroundingDecision(False, None)
    match = INJECTION_REGEX.search(user_message)
    if match:
        return GroundingDecision(True, f"prompt_injection_pattern:{match.group(0).lower()}")
    return GroundingDecision(False, None)


def is_off_topic(user_message: str) -> bool:
    """Quick heuristic for clearly off-DRINKOO queries.

    Returns True only for messages with zero relation to beverages, the brand,
    or our policies. Used as a last resort; the main defense is grounded retrieval.
    """
    if not user_message:
        return True
    text_lower = user_message.lower()
    drinkoo_tokens = (
        "drink",
        "drinkoo",
        "beverage",
        "soda",
        "sparkling",
        "citrus",
        "berry",
        "tea",
        "coffee",
        "water",
        "kids",
        "sport",
        "order",
        "refund",
        "shipping",
        "promo",
        "promotion",
        "ingredient",
        "sugar",
        "calorie",
        "bulk",
        "allergen",
        "policy",
        "subscription",
        "gift",
        "product",
    )
    return not any(tok in text_lower for tok in drinkoo_tokens)
