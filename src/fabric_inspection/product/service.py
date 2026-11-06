"""One frozen engine, explicit business policy, evidence and history."""
from pathlib import Path
import uuid,time,hashlib
from datetime import datetime,UTC
import numpy as np
import cv2
from PIL import Image
from ..vision.classical.engine import ClassicalInspectionEngine,PROJECT_ROOT
from ..vision.classical.preprocessing import load_grayscale
from .commissioning import ClassicalCommissioner,UNSUPPORTED
from .decision import decide
from .evidence import save_evidence

class ProductService:
    def __init__(self,database,storage_dir,engine=None,catalog=None):
        self.database=database;self.storage_dir=Path(storage_dir).resolve();self.storage_dir.mkdir(parents=True,exist_ok=True)
        self.engine=engine or ClassicalInspectionEngine();self.commissioner=ClassicalCommissioner(self.engine);self.catalog=catalog

    def _fabric(self,fabric_id):
        fabric=self.database.get_fabric(fabric_id)
        if fabric is None:raise KeyError('Fabric not found')
        return fabric

    def create_fabric(self,values):
        if values.get('profile') not in self.engine.models:raise ValueError(UNSUPPORTED)
        return self.database.create_fabric(values)

    def add_samples(self,fabric_id,paths,source='upload'):
        self._fabric(fabric_id)
        paths=self.commissioner.validate_samples(paths)
        return self.database.add_samples(fabric_id,[str(p) for p in paths],source)

    def _map(self,path,profile,normal_only=False):
        # Catalog offsets are authoritative; filenames are never used as grid coordinates.
        record=self.catalog.find(path) if self.catalog else None
        if record is not None:
            if record.roll_id!=profile:raise ValueError('Selected sample belongs to a different frozen roll profile')
            if normal_only and record.split!='train_good':raise ValueError('Normal validation accepts training-normal catalog samples only')
            parent=load_grayscale(self.catalog.images/record.parent)
            tile=load_grayscale(record.path)
            features,_=self.engine.extract(tile,parent,record.row_offset,record.col_offset)
            return self.engine.score_features(features,profile)[0]
        return self.engine.inspect_path(path,profile)

    def commission(self,fabric_id):
        fabric=self._fabric(fabric_id);profile=fabric.get('profile')
        if profile not in self.engine.models:raise ValueError(UNSUPPORTED)
        paths=[r['path'] for r in self.database.list_samples(fabric_id)]
        self.database.mark_commissioning(fabric_id,'VALIDATING')
        try:
            summary=self.commissioner.commission(profile,paths,lambda p,r:self.engine.image_score(self._map(p,r,True)))
            return self.database.complete_commissioning(fabric_id,summary)
        except Exception:
            self.database.mark_commissioning(fabric_id,'VALIDATION_FAILED');raise

    def inspect(self,fabric_id,image_path):
        start=time.perf_counter();fabric=self._fabric(fabric_id);summary=fabric.get('commissioning_summary') or {}
        if fabric['commissioning_status']!='READY' or summary.get('model_sha256')!=self.engine.config['model_sha256'] or summary.get('refitted') is not False:
            raise ValueError('Validate normal samples against a frozen profile before inspection')
        path=Path(image_path).resolve();profile=fabric['profile'];anomaly=self._map(path,profile)
        score=self.engine.image_score(anomaly);policy=self.engine.thresholds(profile);decision=decide(score,policy)
        with Image.open(path) as im:image=np.asarray(im.convert('RGB')).copy()
        ident=uuid.uuid4().hex;folder=self.storage_dir/'inspections'/ident
        evidence,regions=save_evidence(folder,image,anomaly,policy['pixel'])
        row={'inspection_id':ident,'timestamp':datetime.now(UTC).isoformat(),'fabric_id':fabric_id,'engine':'classical_solution1','anomaly_score':score,'decision':decision,'defect_count':len(regions),'latency_ms':(time.perf_counter()-start)*1000,'image_path':str(path),'thresholds':policy,'defects':regions,**evidence}
        return self.database.save_inspection(row)

    def store_upload(self,filename,content,category):
        if category not in ('normal','inspection'):raise ValueError('Unknown upload category')
        suffix=Path(filename).suffix.lower()
        if suffix not in ('.png','.jpg','.jpeg','.tif','.tiff','.bmp'):raise ValueError('Use a readable image file')
        if len(content)>50*1024*1024:raise ValueError('Image exceeds the 50 MiB upload limit')
        folder=self.storage_dir/'uploads'/category;folder.mkdir(parents=True,exist_ok=True)
        path=folder/f'{uuid.uuid4().hex}{suffix}';path.write_bytes(content)
        try:self.commissioner.validate_samples([path])
        except Exception:path.unlink();raise
        return path

    def present_inspection(self,value):
        result=dict(value);result['status']=result.pop('decision')
        # Preserve historical stored labels; presentation uses HOLD, never automatic confirmation.
        if result['status']=='FAIL':result['status']='HOLD'
        result['explanation']={'PASS':'Image is consistent with the selected frozen normal profile.','REVIEW':'Anomalous texture detected. Operator review recommended.','HOLD':'Strong anomalous evidence detected. Human confirmation required.'}[result['status']]
        result['artifacts']={k:'/artifacts/'+Path(result[f]).resolve().relative_to(self.storage_dir).as_posix() for k,f in [('original','original_path'),('anomaly_map','anomaly_map_image_path'),('overlay','overlay_path'),('raw_map','anomaly_map_path')]}
        return result
