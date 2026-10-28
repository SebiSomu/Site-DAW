# Mum's Homemade Jams

Online shop for mum's homemade jams. Frontend in **Svelte 5 + Vite + TypeScript**, backend in **Flask (Python)**. All site content is in English; prices are in lei (RON).

- Project plan: [`PLAN.md`](PLAN.md)
- Grading rubric: [`Barem_evaluare_proiect_web.md`](Barem_evaluare_proiect_web.md)
- Barem progress tracker: [`docs/BAREM.md`](docs/BAREM.md)
- Skill for AI agents: [`.agents/skills/gemuri-webdev/SKILL.md`](.agents/skills/gemuri-webdev/SKILL.md)

## Requirements

| Tool | Version | Check |
|---|---|---|
| Git | any recent version | `git --version` |
| Node.js | 20 or newer (includes npm) | `node -v` |
| Python | 3.12 | `python --version` |

## First-time setup

```powershell
git clone https://github.com/SebiSomu/Site-DAW.git
cd Site-DAW
```

### Frontend

```powershell
npm install
```

### Backend

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
flask db upgrade
flask seed --demo
cd ..
```

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
flask db upgrade
flask seed --demo
cd ..
```

If PowerShell refuses to activate the environment (`running scripts is disabled`), run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Running locally

Use two terminals.

Terminal 1, backend (from `backend/`, virtual environment active):

```powershell
flask run
```

Terminal 2, frontend (from the project root):

```powershell
npm run dev
```

Open http://localhost:5173. Vite forwards every `/api/*` and `/uploads/*` request to Flask on http://127.0.0.1:5000, so the frontend never needs the backend URL. The home page shows `Server: conectat` when both are running.

## Frontend commands

Run these from the project root.

| Command | What it does |
|---|---|
| `npm run dev` | Starts the dev server at http://localhost:5173 (reloads on every save) |
| `npm run check` | Type-checks TypeScript and Svelte components |
| `npm run build` | Builds the production version into `dist/` |
| `npm run preview` | Serves the `dist/` build locally |

## Backend commands

Run these from the `backend/` folder with the virtual environment active (`.\.venv\Scripts\Activate.ps1` on Windows, `source .venv/bin/activate` on macOS/Linux). The terminal prompt then starts with `(.venv)`.

Before the first run, edit `backend/.env`: set a long random `SECRET_KEY` and an `ADMIN_PASSWORD` (the admin account is only created when it is set).

| Command | What it does |
|---|---|
| `pip install -r requirements-dev.txt` | Installs app + test dependencies (run again after new packages are added) |
| `flask db upgrade` | Creates/updates the database in `backend/instance/gemuri.db` |
| `flask seed` | Adds roles, order statuses, categories, 13 jams and the admin account (safe to run repeatedly) |
| `flask seed --demo` | Same, plus a demo client `client@exemplu.ro` / `Client-Demo-123` |
| `flask db migrate -m "describe change"` | Generates a migration after changing a model; review it, then run `flask db upgrade` |
| `flask db downgrade` | Reverts the last migration |
| `flask run` | Starts the API at http://127.0.0.1:5000 (health check: `/api/health`) |
| `pytest` | Runs the backend tests |
| `deactivate` | Leaves the virtual environment |

To start over with an empty database, delete `backend/instance/gemuri.db`, then run `flask db upgrade` and `flask seed --demo`.

The database schema, ER diagram and 3NF explanation are in [`docs/DATABASE.md`](docs/DATABASE.md).

## Continuous integration

Every push and pull request to `main` runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml) on GitHub Actions:

- **Backend:** install dependencies, apply migrations, check the models match the migrations (`flask db check`), run `pytest`
- **Frontend:** `npm ci`, `npm run check`, `npm run build`, and upload `dist/` as a downloadable artifact

A pull request should only be merged when both jobs are green.

## Git workflow

```powershell
git pull
git checkout -b feat/feature-name
git add .
git commit -m "feat: short description"
git push -u origin feat/feature-name
```

Then open a Pull Request on GitHub into `main`.

Rules:

- Don't work directly on `main`; use one branch per feature.
- Commit messages follow Conventional Commits: `feat:`, `fix:`, `test:`, `chore:`, `docs:`, `style:`.
- Never commit `.env`, `node_modules/`, `backend/.venv/`, databases or logs (they're already in `.gitignore`).
- Run `npm run check` and `npm run build` before pushing.
- No comments in code; explanations go in the Pull Request or the README.
- All site text is in English. Prices are shown as `24.50 lei`.

## Common problems

| Problem | Fix |
|---|---|
| `git push` rejected with `non-fast-forward` | `git pull --rebase origin main`, then `git push` |
| `npm` is not recognized | Install Node.js and reopen the terminal |
| `python` opens the Microsoft Store | Install Python from python.org and tick "Add python.exe to PATH" |
| `Server: indisponibil` on the home page | Flask isn't running: start it with `flask run` in `backend/` |
| Many files show as modified after pulling `.gitattributes` | Run `git add --renormalize .` once and commit it (line endings are now normalized to LF) |
| Port 5173 is busy | Vite picks another port automatically; use the address shown in the terminal |
