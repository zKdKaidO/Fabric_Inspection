"""Validate normal references against an existing frozen profile; never fit."""
from pathlib import Path
import time
import numpy as np
from PIL import Image
from ..vision.classical.engine import ClassicalInspectionEngine
from ..vision.classical.preprocessing import load_grayscale

UNSUPPORTED = 'New-fabric model fitting is not supported in this frozen research release.'

class ClassicalCommissioner:
    def __init__(self,engine: ClassicalInspectionEngine):
        self.engine=engine

    @staticmethod
    def validate_samples(paths,minimum=1):
        if len(paths)<minimum:raise ValueError(f'At least {minimum} normal reference images are required')
        result=[]
        for p in paths:
            path=Path(p).resolve()
            if not path.is_file():raise FileNotFoundError(f'Normal sample does not exist: {path.name}')
            with Image.open(path) as image:
                if min(image.size)<256:raise ValueError('Normal samples must be at least 256x256; no resizing is performed')
                image.verify()
            result.append(path)
        return result

    def commission(self,profile,sample_paths,score_sample):
        if profile not in self.engine.models:raise ValueError(UNSUPPORTED)
        started=time.perf_counter();paths=self.validate_samples(sample_paths,4)
        scores=[float(score_sample(path,profile)) for path in paths]
        threshold=self.engine.thresholds(profile)
        passed=all(np.isfinite(s) and s<threshold['review'] for s in scores)
        model=self.engine.models[profile]
        return {'profile':profile,'number_of_samples':len(paths),'score_distribution':scores,'validation_passed':passed,'validation_rule':'Every normal sample score must remain below the unchanged review threshold','model_artifact_path':str(self.engine.model_path.resolve()),'model_sha256':self.engine.config['model_sha256'],'thresholds':{'pass':threshold['review'],'review':threshold['review'],'fail':threshold['hold'],'pixel':threshold['pixel']},'fail_enabled':True,'pca_components':model.retained_components,'pca_explained_variance':model.retained_variance,'commissioning_time_seconds':time.perf_counter()-started,'normal_only':True,'refitted':False,'message':'Selected frozen profile activated.' if passed else 'Normal validation failed. Profile not activated; select the correct fabric profile.'}
