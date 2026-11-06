"""Optional local demonstration catalog with authoritative parent offsets."""
from pathlib import Path
from ..data.raw_fabrid import RawFabridDataset
from ..vision.classical.engine import PROJECT_ROOT

class DemoCatalog:
    def __init__(self,config):
        c=config['dataset'];self.root=(PROJECT_ROOT/c['root']).resolve();self.images=(PROJECT_ROOT/c['images']).resolve()
        args={'root':self.root,'metadata_csv':(PROJECT_ROOT/c['metadata_csv']).resolve(),'coco_json':(PROJECT_ROOT/c['coco_json']).resolve(),'image_size':256}
        self.train=RawFabridDataset(**args,split='train');self.test=RawFabridDataset(**args,split='test')
        self.by_path={str(r.path.resolve()):r for d in [self.train,self.test] for r in d.records}
    def find(self,path):return self.by_path.get(str(Path(path).resolve()))
    def record(self,path):
        r=self.find(path)
        if r is None:raise ValueError('Choose an image from the local demonstration catalog')
        return r
    def samples(self,profile,split='test',limit=24):
        records=[r for r in (self.train if split=='train' else self.test).records if r.roll_id==profile]
        if split=='test':
            normal=[r for r in records if not r.label];defect=[r for r in records if r.label]
            records=[r for pair in zip(normal,defect) for r in pair]+normal[min(len(normal),len(defect)):]+defect[min(len(normal),len(defect)):]
        return [{'path':str(r.path),'filename':r.path.name,'profile':r.roll_id,'preview_url':'/demo-data/'+r.path.relative_to(self.root).as_posix()} for r in records[:limit]]
