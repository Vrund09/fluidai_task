INJECTION_PATTERNS = [
    "ignore previous",
    "ignore your instructions",
    "ignore all instructions",
    "reveal system prompt",
    "reveal your prompt",
    "reveal instructions",
    "all salaries",
    "everyone's salary",
    "every employee salary",
]


def check(question: str) -> tuple[bool, str]:
    """Run input guardrails. Returns (ok: bool, reason: str)."""
    stripped = question.strip()
    if not stripped:
        return False, "Question cannot be empty."
    if len(stripped) > 2000:
        return False, "Question too long (max 2000 characters)."

    q_lower = stripped.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in q_lower:
            return False, "I can't process that request."

    return True, ""
