from pathlib import Path
import hashlib
import numpy as np
import pytest
from PIL import Image
from fabric_inspection.vision.classical.engine import ClassicalInspectionEngine
from fabric_inspection.product.commissioning import ClassicalCommissioner,UNSUPPORTED
from fabric_inspection.product.database import ProductDatabase
from fabric_inspection.product.service import ProductService
from fabric_inspection.product.decision import decide

def test_frozen_policy_boundaries():
    p={'review':8.,'hold':10.}
    assert [decide(s,p) for s in [7.99,8,9.99,10]]==['PASS','REVIEW','REVIEW','HOLD']
    with pytest.raises(ValueError):decide(float('nan'),p)

def test_validation_activates_only_existing_profile_without_refit(tmp_path):
    engine=ClassicalInspectionEngine();commissioner=ClassicalCommissioner(engine);before=hashlib.sha256(engine.model_path.read_bytes()).hexdigest()
    paths=[]
    for i in range(4):
        p=tmp_path/f'normal{i}.png';Image.fromarray(np.full((256,256),120,np.uint8)).save(p);paths.append(p)
    low=engine.thresholds('Rollo1A')['review']-1
    good=commissioner.commission('Rollo1A',paths,lambda p,r:low)
    bad=commissioner.commission('Rollo1A',paths,lambda p,r:low+1)
    assert good['validation_passed'] and not good['refitted'] and not bad['validation_passed']
    assert hashlib.sha256(engine.model_path.read_bytes()).hexdigest()==before
    with pytest.raises(ValueError,match='New-fabric'):commissioner.commission('unknown',paths,lambda p,r:0)

def test_failed_validation_blocks_inspection_and_preserves_history(tmp_path,monkeypatch):
    db=ProductDatabase(tmp_path/'db.sqlite');service=ProductService(db,tmp_path/'store')
    service.create_fabric({'fabric_id':'test-01','name':'Test','profile':'Rollo1A'})
    paths=[]
    for i in range(4):
        p=tmp_path/f'n{i}.png';Image.fromarray(np.full((256,256),120,np.uint8)).save(p);paths.append(str(p))
    service.add_samples('test-01',paths)
    monkeypatch.setattr(service,'_map',lambda *args:np.zeros((256,256),np.float32))
    assert service.commission('test-01')['commissioning_status']=='READY'
    result=service.inspect('test-01',paths[0]);assert result['decision']=='PASS'
    for key in ['original_path','anomaly_map_path','anomaly_map_image_path','overlay_path']:assert Path(result[key]).is_file()
    assert db.get_inspection(result['inspection_id'])['anomaly_score']==0
    monkeypatch.setattr(service,'_map',lambda *args:np.full((256,256),25,np.float32))
    assert service.commission('test-01')['commissioning_status']=='VALIDATION_FAILED'
    with pytest.raises(ValueError,match='Validate normal'):service.inspect('test-01',paths[0])
    assert len(db.list_inspections())==1
