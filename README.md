# Personal Wealth Manager

An app to manage different assets, including real estate, gold, stocks and cash.

Software Engineering mini-project, 5th Sem Section B, **Team 5**.

| SRN | Name |
|---|---|
| PES1UG24AM090 | Dhyan Rao |
| PES1UG24AM089 | Dhruvagouda Patil |
| PES1UG24AM110 | Hanshal Nagesh |
| PES1UG24AM122 | Jayant Mahishi |

## Tech stack

- **Backend:** Python 3.12, FastAPI
- **Database:** SQLite through SQLAlchemy
- **Frontend:** HTML, CSS and JavaScript served by FastAPI
- **Testing:** pytest. **Linting:** ruff
- **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`)

## Project structure

```
app/
  main.py        # creates the FastAPI app and plugs in the routers
  config.py      # settings (app name, version, database URL)
  database.py    # database connection and session
  routers/       # API layer: URL endpoints, one file per feature
  services/      # business logic (valuation, net worth, ...)
  models/        # database tables
  schemas/       # request/response shapes
  static/        # web pages (HTML/CSS/JS)
tests/           # pytest tests
docs/            # SRS, SAD and Test Plan
```

Requests flow **router → service → model**. Routers handle HTTP, services hold the logic, models talk to the database.

## Run it locally

```bash
python -m venv .venv
```

Activate the environment: `.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on Mac/Linux.

```bash
pip install -r requirements-dev.txt
```

```bash
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000 for the app
- http://127.0.0.1:8000/docs for the interactive API docs

## Run the checks (same as CI)

```bash
ruff check .
```

```bash
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how we use branches, pull requests and Jira.
