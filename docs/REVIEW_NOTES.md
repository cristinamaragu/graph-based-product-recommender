# Technical review / limitations

## Confirmed changes

- Corrected the README notebook reference (the original referred to a missing v5 file).
- Split the exploratory baseline from the more complete evaluated notebook.
- Re-executed both notebooks on the full dataset and committed them with outputs.
- Fixed the final chart to plot the corrected evaluation, and restricted the
  popularity baseline to the same evaluable catalogue as the graph methods.
- Cleaned the exploratory notebook: removed empty cells, duplicated sections, unused
  imports and a leftover work note; renamed the duplicated `recomendar` function and
  fixed section numbering.
- Replaced loading of untrusted Python pickle in the demo API with a JSON/JSON.gz
  format and strict model shape check. The existing pickle is **not shipped or loaded**.
- Removed the made-up product price fallback (a random-looking `hash()` value).
- Added query bounds, case-insensitive search, deterministic ordering and tests.
- Escaped product descriptions/codes before constructing browser HTML.
- Removed the proprietary/internal assignment PDF and Python caches.
- Set local binding for Docker ports and removed default hard-coded credentials.
- Added a first notebook cell that switches to the repository root, so relative
  paths to `data/` and `artifacts/` work when Jupyter opens the notebook in `notebooks/`.
- Split Docker images: the API image installs only FastAPI + Uvicorn; the analysis
  image (`Dockerfile.analysis`) holds the full Jupyter/graph stack.
- Restored a Neo4j health check (password read from the container environment) and
  made the notebook service wait for it.
- Unified the demo store UI in English to match the documentation.
- Added a reproducible synthetic offline demo that does not rely on a third-party
  service or the confidential challenge document.

## Not verified here

The Neo4j/GDS section was not re-executed (no Neo4j server available); its figures
are from the original run. Docker image builds were not executed.

## Suggested next engineering steps

- Move evaluation logic into tested Python modules and use a temporal holdout.
- Report cold-start cases (test products unseen in training) separately.
- For production: replace the demo with auth, observability and explicit resource
  limits; avoid any claim that recommendations are live commerce-ready.
