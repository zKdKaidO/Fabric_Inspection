"""The single final detector: frozen Solution 1, with real parent context."""
from __future__ import annotations

from pathlib import Path
import hashlib
import joblib
import numpy as np
import yaml

from .preprocessing import load_grayscale
from .gabor import GaborFilterBank
from .texture_features import gabor_dense_features
from .center_surround import contrast_grid, normalized_parent_window
from .scoring import grid_to_anomaly_map, image_anomaly_score

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class ClassicalInspectionEngine:
    """Load the frozen seven-profile artifact; inference never fits or calibrates.

    inspect_tile requires the actual parent and authoritative pixel offsets.
    inspect_frame retains that same context while assembling overlapping tiles.
    Frame-level assembly is a product operation, not the patch benchmark.
    """

    patch_size = 256
    engine_name = 'classical_solution1'

    def __init__(self, model_path=None, config_path=None):
        self.model_path = Path(model_path or PROJECT_ROOT/'models/classical_solution1.joblib')
        self.config_path = Path(config_path or PROJECT_ROOT/'configs/classical_solution1.yaml')
        self.config = yaml.safe_load(self.config_path.read_text(encoding='utf-8'))
        digest = hashlib.sha256(self.model_path.read_bytes()).hexdigest()
        if digest != self.config['model_sha256']:
            raise ValueError('Frozen model integrity check failed')
        artifact = joblib.load(self.model_path)
        self.models = artifact['models']
        if artifact['descriptor_dimensions'] != 25 or not artifact['normal_only']:
            raise ValueError('Expected the frozen 25-dimensional normal-only model')
        g = self.config['gabor']
        self.bank = GaborFilterBank(g['wavelengths'], g['orientations_deg'], g['sigma_ratio'], g['gamma'], tuple(g['phases_rad']))
        for roll, model in self.models.items():
            if model.retained_components != self.config['pca_ranks'][roll]:
                raise ValueError(f'Frozen PCA rank mismatch for {roll}')

    def extract(self, gray, parent, y, x):
        gray=np.asarray(gray,dtype=np.float32);parent=np.asarray(parent,dtype=np.float32)
        if gray.shape != (256,256) or parent.ndim != 2:
            raise ValueError('A tile must be 256x256 and the parent must be grayscale')
        if y<0 or x<0 or y+256>parent.shape[0] or x+256>parent.shape[1]:
            raise ValueError('Tile lies outside its actual parent')
        if not np.isfinite(parent).all() or not np.array_equal(gray,parent[y:y+256,x:x+256]):
            raise ValueError('Tile/parent mismatch or nonfinite source pixels')
        normalized,origin=normalized_parent_window(gray,parent,y,x)
        dense,_=gabor_dense_features(normalized,self.bank,local_window=15)
        cy,cx=origin
        texture=dense[cy:cy+256,cx:cx+256][2::4,2::4]
        contrast=contrast_grid(normalized,origin)
        features=np.concatenate((texture,contrast[...,None]),axis=-1)
        return features,contrast

    def score_features(self, features, roll):
        if roll not in self.models:
            raise ValueError('Choose a commissioned frozen fabric profile')
        if features.shape != (64,64,25) or not np.isfinite(features).all():
            raise ValueError('Expected finite 64x64x25 features')
        grid=self.models[roll].score(features)
        return grid_to_anomaly_map(grid,(256,256),1.5,25),grid

    def inspect_tile(self, parent, y, x, roll):
        parent=np.asarray(parent,dtype=np.float32)
        features,_=self.extract(parent[y:y+256,x:x+256],parent,y,x)
        return self.score_features(features,roll)[0]

    @staticmethod
    def image_score(anomaly_map):
        return image_anomaly_score(anomaly_map,.999)

    def thresholds(self,roll):
        return dict(self.config['operating_policy'][roll])

    def inspect_frame(self, parent, roll):
        parent=np.asarray(parent,dtype=np.float32)
        if parent.ndim != 2 or min(parent.shape)<256:
            raise ValueError('Upload the full parent image, at least 256x256; no resizing is performed')
        def starts(n):
            points=list(range(0,n-255,224))
            if points[-1]!=n-256:points.append(n-256)
            return points
        total=np.zeros(parent.shape,np.float32);count=np.zeros(parent.shape,np.float32)
        for y in starts(parent.shape[0]):
            for x in starts(parent.shape[1]):
                total[y:y+256,x:x+256]+=self.inspect_tile(parent,y,x,roll)
                count[y:y+256,x:x+256]+=1
        return total/count

    def inspect_path(self,path,roll):
        return self.inspect_frame(load_grayscale(path),roll)
