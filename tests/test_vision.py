import numpy as np
import pytest
from fabric_inspection.vision.classical.engine import ClassicalInspectionEngine
from fabric_inspection.vision.classical.center_surround import normalized_parent_window
from fabric_inspection.vision.classical.texture_features import gabor_dense_features
from fabric_inspection.vision.classical.center_surround import contrast_grid
from fabric_inspection.vision.classical.scoring import grid_to_anomaly_map

@pytest.fixture(scope='module')
def engine():return ClassicalInspectionEngine()

def test_preprocessing_and_constant_input():
    a=np.arange(256*256,dtype=np.float32).reshape(256,256)%256
    n,_=normalized_parent_window(a,a,0,0);assert n.dtype==np.float32 and n.min()==0 and n.max()==1
    constant=np.ones((256,256),np.float32)
    assert np.all(normalized_parent_window(constant,constant,0,0)[0]==0)

def test_gabor_phase_magnitude_and_texture_shape(engine):
    a=np.random.default_rng(42).random((296,296),dtype=np.float32)
    texture,responses=gabor_dense_features(a,engine.bank)
    assert len(engine.bank)==12 and responses.shape==(296,296,12) and texture.shape==(296,296,24)
    assert np.isfinite(texture).all() and np.all(responses>=0)

def test_contrast_and_25D_construction(engine):
    constant=np.ones((296,296),np.float32)
    assert np.all(contrast_grid(constant,(20,20))==0)
    parent=np.random.default_rng(42).integers(0,256,(300,300)).astype(np.float32)
    f,c=engine.extract(parent[20:276,20:276],parent,20,20)
    assert f.shape==(64,64,25) and np.array_equal(f[...,24],c)
    with pytest.raises(ValueError,match='mismatch'):engine.extract(np.zeros((256,256),np.float32),parent,20,20)

def test_frozen_PCA_and_distance_formula(engine):
    assert {r:m.retained_components for r,m in engine.models.items()}=={f'Rollo{i}A':18 if i==7 else 19 for i in range(1,8)}
    model=engine.models['Rollo1A'];features=np.broadcast_to(model.standardizer.median,(64,64,25)).copy()
    z=model.pca.transform(model.standardizer.standardize(features).reshape(-1,25))
    radius=np.sqrt(np.mean(z**2/np.maximum(model.pca.explained_variance_,1e-6),axis=1))
    expected=np.maximum((radius-model.distance_median)/model.distance_scale,0).reshape(64,64).astype(np.float32)
    assert np.array_equal(model.score(features),expected)
    assert not hasattr(model,'fit')

def test_map_generation_and_full_frame(engine):
    out=grid_to_anomaly_map(np.ones((64,64),np.float32),(256,256),1.5,25)
    assert out.shape==(256,256) and np.isfinite(out).all() and np.allclose(out,1)
    p=np.full((256,256),120,np.float32)
    assert np.array_equal(engine.inspect_frame(p,'Rollo1A'),engine.inspect_tile(p,0,0,'Rollo1A'))
    with pytest.raises(ValueError):engine.inspect_frame(np.ones((32,32)), 'Rollo1A')
