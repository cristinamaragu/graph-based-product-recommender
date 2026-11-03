"""Read-only educational recommendation API. Use JSON, never untrusted pickle."""
from __future__ import annotations
import gzip
import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="Graph recommendation demo", version="1.0.0")

@lru_cache(maxsize=1)
def load_model():
    raw = Path(os.environ.get("MODEL_PATH", "examples/sample_model.json"))
    path = raw if raw.is_absolute() else ROOT / raw
    if not path.is_file():
        raise FileNotFoundError(f"Model not found at {path}; build it first.")
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        model = json.load(stream)
    expected = {'edges','com','desc','pop','price'}
    if not isinstance(model, dict) or not expected.issubset(model):
        raise ValueError('Unexpected model schema')
    model['catalog'] = sorted(model['edges'], key=lambda c: (-model['pop'].get(c, 0), c))
    return model

def info(model, code):
    price = model['price'].get(code)
    return {'code':code, 'desc':model['desc'].get(code,code),
            'price':round(float(price),2) if price is not None else None,
            'pop':int(model['pop'].get(code, 0))}

def ranked(model, seeds, k=5):
    """Sum Jaccard scores for neighbours in the same community, exclude seeds."""
    edges, groups = model['edges'], model['com']
    selected = {c for c in seeds if c in edges and c in groups}
    scores = {}
    for code in selected:
        for other, features in edges.get(code, {}).items():
            if other in selected or groups.get(other) != groups[code]:
                continue
            scores[other] = scores.get(other,0.0) + float(features.get('jaccard',0))
    return sorted(scores, key=lambda c: (-scores[c], c))[:k]

@app.get('/', response_class=HTMLResponse)
def home():
    return (ROOT/'web/index.html').read_text(encoding='utf-8')

@app.get('/health')
def health():
    try:
        model=load_model()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503,detail=f'Model unavailable: {type(exc).__name__}') from exc
    return {'status':'ok', 'products':len(model['catalog']),
            'dataset':'synthetic demo' if os.getenv('MODEL_PATH','examples/sample_model.json')=='examples/sample_model.json' else 'configured model'}

@app.get('/api/catalogo')
def catalogo(q: str = '', page: int = Query(1,ge=1), size: int = Query(24,ge=1,le=100)):
    model=load_model()
    codes=model['catalog']
    if q.strip():
        term=q.strip().casefold()
        codes=[c for c in codes if term in model['desc'].get(c,'').casefold() or term in c.casefold()]
    start=(page-1)*size
    return {'total':len(codes),'page':page,'size':size,
            'items':[info(model,c) for c in codes[start:start+size]]}

@app.get('/api/virales')
def virales(n: int=Query(10,ge=1,le=100)):
    model=load_model()
    return [info(model,c) for c in model['catalog'][:n]]

@app.get('/api/recomendar')
def recomendar(code: str, k: int=Query(6,ge=1,le=50)):
    model=load_model()
    if code not in model['edges'] or code not in model['com']:
        raise HTTPException(status_code=404,detail='Product not found')
    return [info(model,c) for c in ranked(model,[code],k)]

@app.get('/api/recomendar_carrito')
def recomendar_carrito(codes: str='', k: int=Query(8,ge=1,le=50)):
    model=load_model()
    items=[c.strip() for c in codes.split(',') if c.strip()][:50]
    return [info(model,c) for c in ranked(model,items,k)]
