# Repository Guidelines

This guide orients new contributors to Scootrate's Flask + Vue stack. Follow these practices to keep the backend, frontend, and data layers consistent.

## Project Structure & Module Organization
- `backend/` contains the Flask app: configuration in `config.py`, database helpers in `db.py`, and blueprints under `routes/`. SQL migrations live in `backend/migrations/`, while one-off scripts such as `seed_admin.py` sit beside them.
- `data/top-scoot.sqlite3` is the working database. Schema history is tracked via the migration runner and should never be edited manually.
- `frontend/` hosts the Vite-driven Vue 3 client. Source lives in `frontend/src/` with route definitions in `src/router/`, Pinia stores in `src/stores/`, and Element Plus assets under `public/`.

## Build, Test, and Development Commands
- Backend setup:
  ```bash
  python3 -m venv backend/venv && source backend/venv/bin/activate
  pip install -r backend/requirements.txt
  python backend/app.py
  ```
  The app boots on `http://localhost:5000`.
- Database migrations: `python backend/migrate.py --database data/top-scoot.sqlite3` applies any new SQL files in order.
- Frontend workflow:
  ```bash
  cd frontend
  npm install
  npm run dev   # Vite dev server on http://localhost:5173
  npm run build # Production bundle in frontend/dist
  ```

## Coding Style & Naming Conventions
- Python code follows 4-space indentation, type hints, and Flask blueprints named with clear verbs (`routes/public.py`). Keep modules snake_case and avoid committing `backend/venv/` updates.
- Vue files use the Composition API with single quotes, PascalCase component names (`RiderTable.vue`), and kebab-case route paths. Import shared utilities from `src/api.js` instead of duplicating axios calls.

## Testing Guidelines
- No automated suite exists yet; add backend tests under `backend/tests/` using `pytest` (`pytest backend/tests`). Wrap database fixtures in temporary copies of `data/top-scoot.sqlite3`.
- For the frontend, prefer component tests with Vitest when introduced, and exercise key flows manually in Vite preview before submitting.

## Commit & Pull Request Guidelines
- Match the existing Conventional Commits-style prefix (`chore:`, `feat:`, `fix:`) with a short imperative summary.
- Each pull request should describe scope, migrations run, and manual verification steps. Link relevant issues and attach UI screenshots or API responses when behavior changes.

## Security & Configuration Tips
- Store secrets in a `.env` file; key variables include `TOPSCOOT_SECRET`, `TOPSCOOT_DATABASE`, and `TOPSCOOT_CORS_ORIGINS`. Never commit credentials.
- For production builds, export `TOPSCOOT_ENV=production` to enforce secure cookies and review CORS to match the deployed frontend origin.
