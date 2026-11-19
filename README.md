# Personal Wealth Manager

An app to manage different assets, including real estate, gold, stocks and cash, and see your total net worth in one place.

Software Engineering mini-project, 5th Sem Section B, **Team 5**.

| SRN | Name |
|---|---|
| PES1UG24AM090 | Dhyan Rao |
| PES1UG24AM089 | Dhruvagouda Patil |
| PES1UG24AM110 | Hanshal Nagesh |
| PES1UG24AM122 | Jayant Mahishi |

## Features

- **Accounts:** register, log in and log out, with passwords stored as salted hashes and accounts locked after 5 failed logins
- **Real estate:** record properties and see the gain or loss on each
- **Gold:** record holdings by weight and purity, valued from a gold price you set
- **Stocks:** record holdings and update prices to see value and gain or loss
- **Cash:** record accounts, deposits and withdrawals, with a transaction history
- **Dashboard:** total net worth, allocation across asset classes, history over time and CSV export
- **Administration:** list users, and deactivate or reactivate accounts

## Tech stack

- **Backend:** Python 3.12, FastAPI
- **Database:** SQLite through SQLAlchemy
- **Frontend:** HTML, CSS and JavaScript served by FastAPI
- **Testing:** pytest and pytest-cov. **Linting:** ruff
- **CI/CD:** GitHub Actions and Docker

## Project structure

```
app/
  main.py          # creates the FastAPI app; loads every router automatically
  config.py        # settings (app name, database URL, session and lockout limits)
  database.py      # database connection and session
  dependencies.py  # who is calling, and do they own this record
  security.py      # password hashing and session tokens
  money.py         # exact decimal handling for amounts
  make_admin.py    # command to make a user an administrator
  routers/         # API layer: URL endpoints, one file per feature
  services/        # business logic (valuation, net worth, ...)
  models/          # database tables
  schemas/         # request/response shapes
  static/          # web pages (HTML/CSS/JS)
tests/             # pytest tests
docs/              # SRS, SAD and Test Plan
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

### Make yourself an administrator

Register in the app first, then run:

```bash
python -m app.make_admin you@example.com
```

Log in again and an **Admin** link appears in the navigation bar.

## Run the checks (same as CI)

```bash
ruff check .
```

```bash
pytest --cov=app --cov-fail-under=70
```

## CI/CD

- **CI** (`.github/workflows/ci.yml`) runs linting and tests on every push and pull request. The coverage must be at least 70%.
- **CD** (`.github/workflows/cd.yml`) runs after CI passes on `main`. It builds the Docker image, checks that it starts, and publishes it to GitHub Container Registry.

To run the published image, keeping the data in a named volume:

```bash
docker run -p 8000:8000 -v wealth-data:/data ghcr.io/dhyan-rao-10/personal-wealth-manager:latest
```

When deploying behind HTTPS, set `FORCE_HTTPS=1` so plain HTTP requests are redirected.

## Documents

See the [docs](docs/README.md) folder for the SRS, SAD and Test Plan.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how we use branches, pull requests and Jira.
