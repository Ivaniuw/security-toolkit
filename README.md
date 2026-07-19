# security-toolkit

A collection of small command-line security and data-hygiene tools, written in Python and developed test-first (pytest).

## Tools

| Tool | Description | Status |
|------|-------------|--------|
| [password-strength-checker](password_strength_checker/) | Scores password strength against length and character-class rules, flags common passwords | 🚧 in progress |
| csv-cleaner | Normalizes and validates messy CSV data | ⏳ planned |
| log-parser | Parses auth/web logs and surfaces suspicious activity | ⏳ planned |
| url-status-checker | Bulk-checks a list of URLs for HTTP status and reachability | ⏳ planned |
| http-header-inspector | Inspects HTTP response headers for missing security headers | ⏳ planned |

## Running the tests

```bash
python -m pytest -v
```

## Tech

- Python 3.14
- pytest
- Test-driven development throughout
