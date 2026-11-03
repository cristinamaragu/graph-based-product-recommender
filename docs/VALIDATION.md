# Validation record — 3 November 2026

**Completed**

- Re-ran `notebooks/02_networkx_leiden_neo4j.ipynb` end to end on the full UCI
  Online Retail dataset (541,909 rows). The notebook is committed with its outputs.
- Corrected evaluation: all methods scored on the same 3,633 held-out baskets, seed
  excluded, empty lists counted as misses, popularity baseline restricted to the
  products in the pruned graph. Jaccard Hit@5 = 0.484 vs baseline 0.135.
- The final chart now plots the corrected results (`comparable_results`).
- Exported `artifacts/model.json.gz` from the notebook and served it through the API
  (2,560 products; health, catalogue, trending and recommendation endpoints checked).
- Executed `notebooks/01_exploratory_networkx.ipynb` end to end after cleanup.
- Rebuilt the synthetic sample model and passed the 3 pytest test functions
  (recommendation constraints, endpoints, 404s and query bounds).
- Ran the API with only `requirements-api.txt` installed (FastAPI + Uvicorn).
- Parsed frontend JavaScript with Node.js; validated `docker-compose.yml` and CI as YAML.

**Not completed**

- Neo4j GDS section: no Neo4j server was available, so the notebook skips it. The
  GDS figures in the README come from the original run.
- Docker image builds were not executed. No load testing, API authentication or
  deployment security assessment.

To repeat the offline checks:

```bash
pip install -r requirements-dev.txt
python scripts/build_sample_model.py
python -m pytest -q tests
```
