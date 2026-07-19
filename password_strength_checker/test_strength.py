import pytest

from strength import check_strength, COMMON_PASSWORDS


# check_strength(password) -> dict:
#   "score":     int 0..5  — скільки з 5 критеріїв виконано
#   "rating":    "weak" | "medium" | "strong"
#   "is_strong": bool
#   "feedback":  list[str] — англомовні поради щодо НЕвиконаних критеріїв
#
# 5 критеріїв (кожен +1 до score):
#   1) довжина >= 12
#   2) є мала літера      [a-z]
#   3) є велика літера    [A-Z]
#   4) є цифра            [0-9]
#   5) є спецсимвол       (не літера і не цифра)


# --- score: підрахунок виконаних критеріїв ---
def test_empty_password_scores_zero():
    assert check_strength("")["score"] == 0


def test_all_five_criteria_met():
    assert check_strength("Str0ng!Password")["score"] == 5


def test_only_lowercase_and_length():
    # 12 малих літер → критерії довжини + малої літери = 2
    assert check_strength("abcdefghijkl")["score"] == 2


def test_short_but_all_classes():
    # "Aa1!" — усі класи символів, але коротко (4) → без бала за довжину = 4
    assert check_strength("Aa1!")["score"] == 4


def test_digits_only_short():
    # лише цифри, коротко → тільки критерій цифри = 1
    assert check_strength("12345")["score"] == 1


# --- rating: категорія за балами ---
def test_rating_weak_when_score_low():
    # score <= 2 → weak
    assert check_strength("abcdefghijkl")["rating"] == "weak"


def test_rating_medium_when_score_mid():
    # score 3 або 4 → medium ("Aa1!" дає 4)
    assert check_strength("Aa1!")["rating"] == "medium"


def test_rating_strong_when_all_met():
    # score == 5 → strong
    assert check_strength("Str0ng!Password")["rating"] == "strong"


def test_is_strong_flag():
    assert check_strength("Str0ng!Password")["is_strong"] is True
    assert check_strength("abc")["is_strong"] is False


# --- feedback: поради щодо невиконаних критеріїв ---
def test_feedback_empty_when_strong():
    assert check_strength("Str0ng!Password")["feedback"] == []


def test_feedback_mentions_missing_length():
    fb = check_strength("Aa1!")["feedback"]
    assert any("12" in msg for msg in fb)


def test_feedback_mentions_missing_uppercase():
    # "lowercase123!" має все, крім великої літери
    fb = check_strength("lowercase123!")["feedback"]
    assert any("uppercase" in msg.lower() for msg in fb)


# --- common passwords: чорний список має пріоритет ---
def test_common_password_is_in_blacklist():
    assert "password123!" in COMMON_PASSWORDS


def test_common_password_forced_weak():
    # "Password123!" виконав би всі 5 критеріїв,
    # але він у чорному списку → rating примусово weak
    report = check_strength("Password123!")
    assert report["rating"] == "weak"
    assert report["is_strong"] is False


def test_common_check_is_case_insensitive():
    # той самий пароль іншим регістром — теж має ловитись
    assert check_strength("PASSWORD123!")["rating"] == "weak"
