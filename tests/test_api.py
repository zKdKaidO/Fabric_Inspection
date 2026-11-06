from pathlib import Path
import hashlib,sys
import pytest
import numpy as np
from fastapi.testclient import TestClient
from fabric_inspection.product.api import create_app

def test_real_API_commission_inspect_evidence_history(tmp_path,monkeypatch):
    app=create_app(tmp_path/'store');service=app.state.service
    if service.catalog is None:pytest.skip('External RAW-FABRID catalog required for real integration')
    before=hashlib.sha256(service.engine.model_path.read_bytes()).hexdigest()
    with TestClient(app) as c:
        assert c.get('/health').status_code==200 and len(c.get('/profiles').json())==7
        bad=c.post('/fabrics',json={'fabric_id':'unknown-fabric','name':'New','profile':'new-fabric'})
        assert bad.status_code==422 and 'New-fabric model fitting is not supported' in bad.text
        assert c.post('/fabrics',json={'fabric_id':'test-01','name':'Known fabric','profile':'Rollo1A','threshold':0}).status_code==422
        assert c.post('/fabrics',json={'fabric_id':'test-01','name':'Known fabric','profile':'Rollo1A'}).status_code==201
        refs=c.get('/demo/samples',params={'profile':'Rollo1A','split':'train','limit':4}).json()
        assert c.post('/fabrics/test-01/sample-selection',json={'paths':[r['path'] for r in refs]}).status_code==200
        ready=c.post('/fabrics/test-01/commission');assert ready.status_code==200,ready.text
        assert ready.json()['commissioning_status']=='READY',ready.text
        samples=c.get('/demo/samples',params={'profile':'Rollo1A','split':'test','limit':2}).json()
        r=c.post('/demo/inspect',json={'fabric_id':'test-01','image_path':samples[1]['path']});assert r.status_code==200,r.text
        value=r.json();assert value['engine']=='classical_solution1' and value['status'] in ['PASS','REVIEW','HOLD']
        assert c.get(value['artifacts']['original']).status_code==200
        assert c.get(value['artifacts']['anomaly_map']).status_code==200
        assert c.get(value['artifacts']['overlay']).status_code==200
        assert c.get('/inspections').json()[0]['inspection_id']==value['inspection_id']
        assert c.get('/inspections/'+value['inspection_id']).status_code==200
        # A deterministic flagged map exercises the human-review route; the actual engine ran above.
        monkeypatch.setattr(service,'_map',lambda *args:np.full((256,256),25,np.float32))
        flagged=c.post('/demo/inspect',json={'fabric_id':'test-01','image_path':samples[1]['path']}).json()
        assert flagged['status']=='HOLD' and flagged['review'] is None
        reviewed=c.post('/inspections/'+flagged['inspection_id']+'/review',json={'decision':'CONFIRMED_DEFECT','notes':'Human confirmation in API test'})
        assert reviewed.status_code==200 and reviewed.json()['review']['decision']=='CONFIRMED_DEFECT'
        assert c.get('/inspections/'+flagged['inspection_id']).json()['review']['notes']=='Human confirmation in API test'
        assert c.get('/artifacts/inspection.db').status_code==404
        # Unsupported alternate inference routes are absent.
        assert c.get('/benchmarks').status_code==404
    assert hashlib.sha256(service.engine.model_path.read_bytes()).hexdigest()==before
    assert not any('experiments' in str(getattr(m,'__file__','')) for m in sys.modules.values() if m is not None)

def test_api_missing_and_unready_fabric(tmp_path):
    with TestClient(create_app(tmp_path/'store')) as c:
        assert c.get('/fabrics/missing').status_code==404
        c.post('/fabrics',json={'fabric_id':'test-02','name':'Known fabric','profile':'Rollo2A'})
        assert c.post('/fabrics/test-02/commission').status_code==400
