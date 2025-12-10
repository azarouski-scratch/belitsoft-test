## Setup

1. Create virtualenv: `python -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and edit if needed
4. Run tests: `pytest` or `pytest --html=report.html` or `pytest --alluredir=allure-results`


## Configuration
Configuration can be provided via `config.yaml` and/or environment variables loaded from `.env`.

Precedence: environment variables override `config.yaml`; `config.yaml` overrides built-in defaults.

Supported keys:
- YAML `config.yaml`:
  - `base_url` (string)
  - `default_timeout` (int)
  - `retry.attempts` (int)
  - `retry.wait_seconds` (int)
  - optional: `env` (string), `api_key` (string)
- Environment variables (`.env`):
  - `BASE_URL`, `DEFAULT_TIMEOUT`, `RETRY_ATTEMPTS`, `RETRY_WAIT`, `ENV`, `API_KEY`

Example `config.yaml`:

```
base_url: "http://localhost:80"
default_timeout: 10
retry:
  attempts: 3
  wait_seconds: 1
```

Example `.env`:

```
BASE_URL=http://localhost:80
DEFAULT_TIMEOUT=10
RETRY_ATTEMPTS=3
RETRY_WAIT=1
ENV=local
API_KEY=
```

## Notes
- `utils/retry.py` provides the custom retry decorator with logs for each attempt.
- `utils/faker_utils.py` produces randomized test data.
- `conftest.py` loads configuration from `config.yaml` and `.env`.
- CI uploads `allure-results` and `report.html` as artifacts.