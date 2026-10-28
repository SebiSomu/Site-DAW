# Gemuri ca la mama acasă

Online shop for mum's homemade jams. Frontend in **Svelte 5 + Vite + TypeScript**, backend in **Flask (Python)**. All text on the site is in Romanian.

- Project plan: [`PLAN.md`](PLAN.md)
- Grading rubric: [`Barem_evaluare_proiect_web.md`](Barem_evaluare_proiect_web.md)
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
pip install -r requirements.txt
cd ..
```

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

If PowerShell refuses to activate the environment (`running scripts is disabled`), run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Frontend commands

Run these from the project root.

| Command | What it does |
|---|---|
| `npm run dev` | Starts the dev server at http://localhost:5173 (reloads on every save) |
| `npm run check` | Type-checks TypeScript and Svelte components |
| `npm run build` | Builds the production version into `dist/` |
| `npm run preview` | Serves the `dist/` build locally |

## Backend commands

Activate the virtual environment first (`.\backend\.venv\Scripts\Activate.ps1` on Windows, `source backend/.venv/bin/activate` on macOS/Linux). The terminal prompt then starts with `(.venv)`.

| Command | What it does |
|---|---|
| `pip install -r backend/requirements.txt` | Installs the Python dependencies (run again after new packages are added) |
| `pip install <package>` then `pip freeze > backend/requirements.txt` | Adds a new package and saves it to the list |
| `deactivate` | Leaves the virtual environment |

> The Flask app, database and tests are added in phases 0–1 of `PLAN.md`. The `flask run`, `flask db upgrade`, `python seed.py` and `pytest` commands will be documented here once they exist.

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
- Site text is in Romanian with correct diacritics (ș, ț with comma below).

## Common problems

| Problem | Fix |
|---|---|
| `git push` rejected with `non-fast-forward` | `git pull --rebase origin main`, then `git push` |
| `npm` is not recognized | Install Node.js and reopen the terminal |
| `python` opens the Microsoft Store | Install Python from python.org and tick "Add python.exe to PATH" |
| Port 5173 is busy | Vite picks another port automatically; use the address shown in the terminal |
