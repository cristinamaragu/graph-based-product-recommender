from fastapi.testclient import TestClient
import api
from scripts.build_sample_model import build

client=TestClient(api.app)

def test_model_and_recommendations():
    d=build(api.ROOT/'data/sample_transactions.csv')
    assert d['edges']['A101']['A102']['jaccard']>0
    assert 'B201' not in api.ranked(d,['A101'],k=10)
    assert 'A101' not in api.ranked(d,['A101'],k=10)
    assert not set(api.ranked(d,['A101','A102'],k=10)) & {'A101','A102'}

def test_endpoints():
    assert client.get('/health').status_code==200
    assert client.get('/').status_code==200
    assert client.get('/api/catalogo?q=mug').json()['total']==1
    assert client.get('/api/catalogo?q=NO-SUCH-PRODUCT').json()['items']==[]
    assert client.get('/api/recomendar?code=A101').status_code==200
    assert client.get('/api/recomendar?code=UNKNOWN').status_code==404
    cart=client.get('/api/recomendar_carrito?codes=A101,A102').json()
    assert all(p['code'] not in {'A101','A102'} for p in cart)

def test_input_limits():
    for url in ['/api/catalogo?page=0','/api/catalogo?size=1000',
                '/api/virales?n=-1','/api/recomendar?code=A101&k=10000']:
        assert client.get(url).status_code==422
