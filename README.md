# Graph-based product recommender — NetworkX, Leiden & Neo4j

A graph-based recommendation system built around real retail transactions, compared
across two graph technology stacks, with an interactive demo store powered by FastAPI.

> **Portfolio overview:** two Python/graph implementations, offline evaluation,
> a Cypher-based Neo4j version, and an HTTP API + browser demo. The original
> dataset is public UCI data, **not proprietary customer data**. A separate tiny
> **synthetic** dataset drives the immediately runnable demo.

## Visual overview

![NetworkX product community visualisation from the exploratory notebook](assets/networkx_community_visualization.png)

*Community visualisation produced in the original exploratory analysis.*

## Why this project

Given a product in a shopping basket, which other products are worth suggesting?
The system represents products as nodes and their co-occurrence in orders as weighted
edges. Community detection captures product clusters; edge-level similarity ranks
candidate products within those clusters.

## Two implementations

| Capability | NetworkX / Python | Neo4j / Graph Data Science |
|---|---|---|
| Graph creation | Co-purchase edges built from training invoices | Batch-loaded `Product` nodes and `BOUGHT_WITH` edges |
| Community detection | **Louvain**, with **Leiden** analysis/refinement using igraph | **GDS Louvain** |
| Ranking | Co-occurrence weight, **Jaccard** and **Lift** | **Cypher** recommendation query |
| Validation | Invoice holdout, Hit@5 / Precision@5 / Recall@5 / Coverage | Compare graph partitions using **ARI** and **NMI** |
| Role | Experimentation & model evaluation | Graph database integration & querying |

Both are covered in `notebooks/02_networkx_leiden_neo4j.ipynb`. The initial, simpler
NetworkX exploration is kept in `notebooks/01_exploratory_networkx.ipynb`: it uses
product descriptions as nodes and is a qualitative baseline, **not** the source of the
reported metrics.

## Results (reproduced 3 Nov 2026, corrected evaluation)

Re-run end to end on the full UCI dataset (541,909 rows → 2,560 products and 104,235
edges in the pruned training graph). All methods are evaluated on the **same 3,633
held-out baskets**: the seed is excluded, an empty list counts as a miss, and the
popularity baseline is restricted to the same evaluable catalogue.

| Method | Hit@5 | Precision@5 | Recall@5 | Coverage |
|---|---|---|---|---|
| Co-occurrence weight | 0.474 | 0.162 | 0.076 | 0.281 |
| **Jaccard** | **0.484** | **0.166** | **0.079** | 0.346 |
| Lift | 0.384 | 0.125 | 0.067 | **0.430** |
| Popularity baseline | 0.135 | 0.036 | 0.006 | 0.002 |

![Graph recommenders vs popularity baseline, comparable evaluation](assets/offline_metrics_comparable.png)

Community detection on the same graph: NetworkX Louvain 40 communities (Q = 0.301),
Leiden 37 (Q = 0.301); refining the 8 largest Louvain communities with Leiden yields
105 finer communities (Q = 0.230). The executed notebook is committed with its outputs.

**Neo4j comparison (historical run):** GDS Louvain Q = 0.302 vs NetworkX Q = 0.301,
ARI = 0.681 and NMI = 0.700 on 2,560 shared products. Neo4j was not available for the
published re-run, so these figures come from the original execution; reproduce them
with the `analysis` Docker Compose profile.

### Evaluation caveats

- **Invoice-level random** train/test split: it avoids invoice leakage, but it is not
  a forward-in-time test and not a live A/B experiment.
- Only test baskets with at least two products present in the pruned graph are
  evaluated (3,633 of 3,650); products unseen in training cannot be recommended.
- The legacy evaluation cell is kept for transparency; its numbers are almost identical
  for the graph methods, but its baseline (0.107) could include the seed product.
- NetworkX and GDS partitions are similar, not identical (Louvain is randomised).

## Technology stack

**Python**, **Pandas**, **NumPy**, **NetworkX**, **igraph**, **Leidenalg**, **scikit-learn**,
**Neo4j**, **Graph Data Science**, **Cypher**, **FastAPI**, **Docker Compose**,
**Jupyter**, **HTML/CSS/JavaScript**, **pytest**.

## Try the API and demo in minutes — without Neo4j

From this repository root:

```bash
python -m venv .venv
# Activate the environment, then:
pip install -r requirements-dev.txt
python scripts/build_sample_model.py
uvicorn api:app --reload
```

Visit http://localhost:8000. The `api.py` serves a demo store and these endpoints:

- `GET /api/catalogo?q=mug&page=1&size=24`
- `GET /api/virales?n=10`
- `GET /api/recomendar?code=A101&k=5`
- `GET /api/recomendar_carrito?codes=A101,A102&k=5`
- `GET /health`

The default model in `examples/sample_model.json` is **illustrative and generated from
invented transactions**, not from the UCI benchmark. A production-size model is exported
from the evaluated notebook as `artifacts/model.json.gz` and enabled with
`MODEL_PATH=artifacts/model.json.gz` (after generating it). No arbitrary Python
`pickle` deserialization is required by the API.

Or run the sample demo with Docker: `docker compose up --build api`. The API image
is intentionally minimal (FastAPI + Uvicorn only, from `requirements-api.txt`); the
full analysis stack lives in a separate `Dockerfile.analysis` used by the notebook service.

## Reproduce the full experiment

1. Download the **Online Retail** dataset from UCI and save it as
   `data/Online_Retail.xlsx`; see [data/README.md](data/README.md).
2. Install the full stack: `pip install -r requirements.txt`.
3. Run **`notebooks/02_networkx_leiden_neo4j.ipynb`** in Jupyter. Its first code cell
   switches to the repository root, so `data/` and `artifacts/` resolve correctly.
   The NetworkX/Leiden analysis works without Neo4j only if all Python dependencies
   are installed; the Neo4j section is optional.
4. To reproduce the Neo4j run: copy `.env.example` to `.env`, set your own unique
   `NEO4J_PASSWORD` and `JUPYTER_TOKEN`, then run
   `docker compose --profile analysis up --build neo4j notebook`.
   The notebook container waits until Neo4j passes its health check.
   The Neo4j browser is at http://localhost:7474 and Jupyter at http://localhost:8888.
5. **Warning:** the notebook's Neo4j section runs `MATCH (n) DETACH DELETE n`.
   Use a **dedicated, disposable database** only.
6. Run the export cell to create a model file under `artifacts/`. Start the API with
   that model path to switch from synthetic to UCI-derived recommendations.


## Files

```text
api.py                                  FastAPI endpoint and safe JSON loader
web/index.html                          Mini-store frontend
notebooks/01_exploratory_networkx.ipynb NetworkX exploration
notebooks/02_networkx_leiden_neo4j.ipynb Evaluated NetworkX + Leiden + Neo4j
scripts/build_sample_model.py           Generate a tiny synthetic example model
examples/sample_model.json              Included for instant API demo
data/sample_transactions.csv            Invented demo transactions
Dockerfile                              Minimal FastAPI image for the demo API
Dockerfile.analysis                     Full Jupyter/graph stack for the notebooks
docker-compose.yml                      API service + optional analysis profile
requirements-api.txt                    API runtime only (FastAPI, Uvicorn)
requirements.txt                        Full analysis dependencies
tests/                                  Offline API checks
```


## Data, Reproducibility & Deployment

This project is designed to support reproducible experimentation and demonstrate how graph-based recommendation systems can be integrated into practical applications.

- **Dataset:** Experiments use the publicly available *Online Retail* dataset from the UCI Machine Learning Repository. Instructions for obtaining and preparing the data are provided in the repository.
- **Reproducibility:** The notebooks document data preprocessing, graph construction, community detection and recommendation evaluation, including comparisons against a popularity-based baseline.
- **Demo environment:** The FastAPI application supports synthetic sample transactions and JSON/JSON.gz model artifacts, allowing the recommendation system to be explored without exposing customer information.
- **Deployment considerations:** The application serves as a functional prototype. Production deployment would require additional measures such as authentication, rate limiting and monitoring.

### Dataset Reference

Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository.

https://doi.org/10.24432/C5BW33

Dataset licensed under CC BY 4.0.
