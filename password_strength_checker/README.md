# password-strength-checker

A command-line tool that rates password strength and explains *why* a password
is weak — including catching common passwords that look complex but aren't.

## Why another password checker?

Most naive checkers only ask "does it have an uppercase letter and a digit?".
That passes `Password123!` — one of the most breached passwords in the world.

This tool combines two ideas:

1. **Complexity scoring** — 5 criteria, following modern
   [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) guidance
   that favours **length** (≥ 12 characters) over forced symbol soup.
2. **Common-password blacklist** — any password on the list is rated **weak**
   regardless of its score, because entropy doesn't help if attackers already
   have it in their wordlist.

## Usage

```bash
# Check a password passed as an argument
python cli.py "MyPassw0rd!"

# Or run with no argument to be prompted securely (input is not echoed)
python cli.py
```

Example:

```text
$ python cli.py "Password123!"
Strength : WEAK  █░░  (5/5)
Suggestions:
  - Avoid common or breached passwords
```

Note that the score is 5/5 but the rating is **weak**: `Password123!` satisfies
every complexity rule, yet it sits on the common-password list, which overrides
the score. That override is the whole point of the tool.

The tool exits with code `0` for a strong password and `1` otherwise, so it can
be used as a gate in scripts and CI pipelines.

## Scoring

| Criterion | Points |
|-----------|--------|
| Length ≥ 12 characters | +1 |
| Contains a lowercase letter | +1 |
| Contains an uppercase letter | +1 |
| Contains a digit | +1 |
| Contains a special character | +1 |

| Score | Rating |
|-------|--------|
| 0–2 | weak |
| 3–4 | medium |
| 5 | strong |

A password found in `COMMON_PASSWORDS` is forced to **weak**.

## Testing

```bash
python -m pytest -v
```

15 tests cover scoring, ratings, feedback, and the blacklist override.
