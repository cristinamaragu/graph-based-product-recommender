"""Build an illustrative, deliberately synthetic model; no employer data needed."""
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]

def build(input_path):
    baskets=defaultdict(set); descriptions={}; prices={}
    with open(input_path,encoding='utf-8',newline='') as file:
        for row in csv.DictReader(file):
            code=row['StockCode']; invoice=row['InvoiceNo']
            baskets[invoice].add(code)
            descriptions[code]=row['Description']; prices[code]=float(row['UnitPrice'])
    pop=Counter(); pairs=Counter()
    for basket in baskets.values():
        for a in basket: pop[a]+=1
        pairs.update(combinations(sorted(basket),2))
    # Only training on this tiny synthetic dataset; no evaluation claims.
    edges={code:{} for code in pop}
    for (a,b),count in pairs.items():
        score=round(count/(pop[a]+pop[b]-count),6)
        edge={'weight':count,'jaccard':score,
              'lift':round(count*len(baskets)/(pop[a]*pop[b]),6)}
        edges[a][b]=edge; edges[b][a]=edge
    # Distinct illustrative groups: sample product codes are labelled for demo
    # only. Full experiment uses Louvain/Leiden and Neo4j (see notebooks).
    communities={code:code[0] for code in pop}
    return {'edges':edges,'com':communities,'desc':descriptions,'pop':dict(pop),'price':prices}

if __name__=='__main__':
    model=build(BASE/'data/sample_transactions.csv')
    target=BASE/'examples/sample_model.json'
    target.parent.mkdir(exist_ok=True,parents=True)
    target.write_text(json.dumps(model,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Saved synthetic demo model:',target)
