# WebClean API

Turn a messy webpage into clean, structured data (title, description, emails,
phones, business hours, links, word count).

## Key facts

- FastAPI app. `main.py` (endpoints + auth) + `scraper.py` (extraction logic).
- Endpoints: `GET /api/extract?url=<webpage>` and `GET /api/quota`.
- Auth: `X-API-Key` header for direct users (demo keys: `demo-free`, `demo-pro`);
  `X-RapidAPI-Proxy-Secret` for RapidAPI calls. See `require_key` in `main.py`.
- Tests: `pytest` (8 tests). Run before pushing changes.
- Deploy: push to GitHub `main` → Render auto-deploys (`render.yaml` defines it).
- Live URL: `https://webclean-api.onrender.com`.

## Workflow

```bash
# from the repo root
python -m pytest
git add . && git commit -m "msg" && git push
```

## For the current human operator

Read `PROGRESS.md` in this folder first (it's gitignored, so it won't be in the
repo — keep it local). It has full handoff notes, keys, and RapidAPI status.
RapidAPI publishing is paused on their broken Test UI; the backend is done.
