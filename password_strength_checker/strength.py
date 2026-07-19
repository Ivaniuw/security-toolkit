"""Password strength checker.

Scores a password against five criteria (length + four character classes)
and downgrades any password found in a list of common/breached passwords,
because a technically-complex password like ``Password123!`` is still weak
if everyone already uses it.
"""

# A tiny sample of the most common passwords. In a real deployment this would
# be loaded from a wordlist such as the SecLists "10k-most-common" file.
COMMON_PASSWORDS = {
    "password",
    "123456",
    "123456789",
    "qwerty",
    "abc123",
    "password1",
    "password123!",
    "admin",
    "letmein",
    "welcome",
    "iloveyou",
    "monkey",
}

# Modern guidance (NIST SP 800-63B) favours length over forced complexity.
MIN_LENGTH = 12

RATINGS = ("weak", "medium", "strong")


def _has_special(password):
    """True if the password contains at least one non-alphanumeric character."""
    return any(not c.isalnum() for c in password)


def check_strength(password):
    """Evaluate a password and return a structured report.

    Args:
        password: The password string to evaluate.

    Returns:
        A dict with keys:
            "score":     int 0..5 — how many criteria are satisfied.
            "rating":    "weak" | "medium" | "strong".
            "is_strong": bool — True only when the rating is "strong".
            "feedback":  list[str] — actionable tips for unmet criteria.
    """
    checks = {
        f"Use at least {MIN_LENGTH} characters": len(password) >= MIN_LENGTH,
        "Add a lowercase letter": any(c.islower() for c in password),
        "Add an uppercase letter": any(c.isupper() for c in password),
        "Add a digit": any(c.isdigit() for c in password),
        "Add a special character": _has_special(password),
    }

    score = sum(checks.values())
    feedback = [tip for tip, passed in checks.items() if not passed]

    if score <= 2:
        rating = "weak"
    elif score <= 4:
        rating = "medium"
    else:
        rating = "strong"

    # A common/breached password is weak no matter how complex it looks.
    if password.lower() in COMMON_PASSWORDS:
        rating = "weak"
        feedback.insert(0, "Avoid common or breached passwords")

    return {
        "score": score,
        "rating": rating,
        "is_strong": rating == "strong",
        "feedback": feedback,
    }
