"""Detects phishing-indicative keywords/phrases in email text.

Keyword matches are an additional risk signal alongside the ML model's
prediction -- a single keyword hit must never, by itself, flip the
final classification.
"""

SUSPICIOUS_KEYWORDS = [
    "verify your account",
    "urgent",
    "immediate action",
    "password",
    "login",
    "account suspended",
    "click here",
    "confirm your identity",
    "otp",
    "security alert",
    "reset password",
    "congratulations",
    "claim reward",
    "prize",
    "bank",
    "payment",
    "invoice",
    "limited time",
]

# Weight per keyword hit, capped, used only to compute an auxiliary score.
KEYWORD_WEIGHT = 6
MAX_KEYWORD_SCORE = 100


def detect_keywords(text):
    """Return (matched_keywords: list[str], keyword_risk_score: int)."""
    if not text:
        return [], 0

    lowered = text.lower()
    matched = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lowered]
    score = min(len(matched) * KEYWORD_WEIGHT, MAX_KEYWORD_SCORE)
    return matched, score
