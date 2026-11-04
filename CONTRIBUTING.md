# How we work

Every piece of work is a **Jira story**, done on its **own branch**, and merged through a **pull request (PR)**.
Nobody pushes directly to `main`.

## Steps for each story

1. **Pick up your story in Jira** and move it to *In Progress*. Note its key, e.g. `PWM-12`.
2. **Get the latest `main`:**
   ```bash
   git checkout main
   git pull
   ```
3. **Create a branch** named after the Jira key and a short description:
   ```bash
   git checkout -b PWM-12-add-gold-assets
   ```
4. **Write the code and a test for it.** Run the checks before pushing:
   ```bash
   ruff check .
   pytest
   ```
5. **Commit with the Jira key at the start of the message:**
   ```bash
   git commit -m "PWM-12: add gold asset model and API"
   ```
6. **Push and open a PR into `main`:**
   ```bash
   git push -u origin PWM-12-add-gold-assets
   ```
   Put the Jira key in the PR title too, and fill in the PR template.
7. **Wait for CI to pass** (the green tick on the PR) and for a review from the repo owner.
8. **After it's merged**, move the Jira story to *Done*. This keeps the burndown chart accurate.

## Where code goes

| You're adding... | Put it in |
|---|---|
| A new API endpoint | `app/routers/<feature>.py`, then include it in `app/main.py` |
| Calculation or business rules | `app/services/<feature>.py` |
| A new database table | `app/models/<feature>.py`, then import it in `app/models/__init__.py` |
| Request/response shapes | `app/schemas/<feature>.py` |
| A page or UI change | `app/static/` |
| Tests | `tests/test_<feature>.py` |

## Rules

- One story per branch and per PR. Keep PRs small.
- The person assigned the story is the one who opens its PR.
- Don't merge a PR with failing CI.
- Don't commit `wealth.db`, `.venv/` or `.env` (they're in `.gitignore`).
