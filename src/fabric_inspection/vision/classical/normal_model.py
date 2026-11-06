"""Serialization-compatible frozen normal profiles; no model-fitting API.

The original artifact retains two historical residual-calibration fields. They
are preserved only for pickle compatibility and never used by Solution 1.
"""
from dataclasses import dataclass
import numpy as np
from sklearn.decomposition import PCA

@dataclass
class RobustNormalModel:
    median: np.ndarray
    scale: np.ndarray
    epsilon: float = 1e-6

    def standardize(self,features):
        return (features-self.median)/self.scale

@dataclass
class PcaNormalModel:
    standardizer: RobustNormalModel
    pca: PCA
    residual_median: float
    residual_scale: float
    distance_median: float
    distance_scale: float

    @property
    def retained_components(self):return int(self.pca.n_components_)
    @property
    def retained_variance(self):return float(self.pca.explained_variance_ratio_.sum())

    def score(self,features):
        shape=features.shape[:-1]
        standardized=self.standardizer.standardize(features).reshape(-1,features.shape[-1])
        projection=self.pca.transform(standardized)
        distance=np.sqrt(np.mean(projection**2/np.maximum(self.pca.explained_variance_,self.standardizer.epsilon),axis=1))
        calibrated=np.maximum((distance-self.distance_median)/self.distance_scale,0.0)
        return calibrated.reshape(shape).astype(np.float32)
