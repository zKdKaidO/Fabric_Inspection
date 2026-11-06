from pathlib import Path
import hashlib,json
import cv2,numpy as np,pytest
from threadpoolctl import threadpool_limits
from fabric_inspection.vision.classical.engine import ClassicalInspectionEngine,PROJECT_ROOT
from fabric_inspection.vision.classical.preprocessing import load_grayscale

def test_golden_solution1_real_parent_context():
    fixture=PROJECT_ROOT/'tests/fixtures';spec=json.loads((fixture/'golden_solution1.json').read_text());r=spec['record'];p=PROJECT_ROOT.parent/'images'/r['parent']
    if not p.is_file():pytest.skip('External RAW-FABRID source image required for golden regression')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['parent_sha256']
    engine=ClassicalInspectionEngine();before=hashlib.sha256(engine.model_path.read_bytes()).hexdigest();cv2.setNumThreads(4)
    with threadpool_limits(limits=4):
        parent=load_grayscale(p);a=engine.inspect_tile(parent,r['row_offset'],r['col_offset'],r['roll']);b=engine.inspect_tile(parent,r['row_offset'],r['col_offset'],r['roll'])
    assert a.shape==(256,256) and np.isfinite(a).all() and np.array_equal(a,b)
    np.testing.assert_allclose(a,np.load(fixture/'golden_map.npy'),atol=spec['map_absolute_tolerance'],rtol=0)
    assert abs(engine.image_score(a)-spec['image_score'])<=spec['score_absolute_tolerance']
    assert hashlib.sha256(engine.model_path.read_bytes()).hexdigest()==before
