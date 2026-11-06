"""Reproduce the frozen benchmark, without fitting, searching or changing policy."""
from pathlib import Path
import argparse,hashlib,json,sys,time
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import cv2
from PIL import Image
from threadpoolctl import threadpool_limits
from fabric_inspection.vision.classical.engine import ClassicalInspectionEngine
from fabric_inspection.vision.classical.preprocessing import load_grayscale
from fabric_inspection.evaluation.metrics import BinaryHistogram,PerRegionOverlapHistogram,image_metrics

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',type=Path,default=ROOT.parent);parser.add_argument('--output',type=Path,default=ROOT/'docs/verification/benchmark.json');parser.add_argument('--reference-maps',type=Path);args=parser.parse_args()
    fixture=ROOT/'tests/fixtures';records=json.loads((fixture/'benchmark_manifest.json').read_text())['records'];reference=json.loads((fixture/'benchmark_reference.json').read_text());frozen=json.loads((fixture/'frozen_metrics.json').read_text())
    engine=ClassicalInspectionEngine();before={p.name:sha(p) for p in [engine.model_path,engine.config_path]};cv2.setNumThreads(4)
    originals=np.load(args.reference_maps,mmap_mode='r') if args.reference_maps else None
    groups=['all']+list(engine.models)+[f'Q{i}' for i in range(1,5)];hist={s:BinaryHistogram(4096,0,25) for s in groups};pro=PerRegionOverlapHistogram(256,0,25,.30)
    scores=[];native_exact=stored_exact=0;map_error=score_error=0.;start=time.perf_counter()
    @lru_cache(maxsize=2)
    def parent(name):return load_grayscale(args.data_root/'images'/name)
    with threadpool_limits(limits=4):
        for i,r in enumerate(records):
            p=parent(r['parent']);tile_path=args.data_root/'MVTec'/('test/defect' if r['label'] else 'test/good')/Path(r['path']).name;tile=load_grayscale(tile_path)
            feature,_=engine.extract(tile,p,r['row_offset'],r['col_offset']);anomaly,_=engine.score_features(feature,r['roll']);assert anomaly.shape==(256,256) and np.isfinite(anomaly).all()
            score=float(np.float32(engine.image_score(anomaly)));scores.append(score);score_error=max(score_error,abs(score-reference['native_scores'][i]))
            native_exact+=hashlib.sha256(anomaly.tobytes()).hexdigest()==reference['native_map_payload_sha256'][i]
            stored=anomaly.astype(np.float16);stored_exact+=hashlib.sha256(stored.tobytes()).hexdigest()==reference['float16_map_payload_sha256'][i]
            if originals is not None:map_error=max(map_error,float(np.max(np.abs(anomaly-originals[i]))))
            truth=np.zeros((256,256),bool)
            if r['label']:
                with Image.open(args.data_root/'MVTec/ground_truth/defect'/Path(r['path']).name) as im:truth=np.asarray(im.convert('L'))==255
            assert int(truth.sum())==r['defect_area']
            values=stored.astype(np.float32);one=BinaryHistogram(4096,0,25);one.update(values,truth);membership=['all',r['roll']]+([f'Q{r["quartile"]}'] if r['label'] else [f'Q{q}' for q in range(1,5)])
            for s in membership:hist[s].positive+=one.positive;hist[s].negative+=one.negative
            pro.update(values,truth)
            if (i+1)%250==0:print(f'Frozen regression {i+1}/{len(records)}; native exact {native_exact}; stored exact {stored_exact}; score error {score_error:.3g}',flush=True)
    labels=np.array([r['label'] for r in records]);scores=np.array(scores,np.float32);result={};errors=[]
    for name in groups:
        m=np.array([name=='all' or r['roll']==name or (name.startswith('Q') and (not r['label'] or f'Q{r["quartile"]}'==name)) for r in records]);result[name]={**hist[name].compute(),**image_metrics(labels[m],scores[m])}
        for k,value in result[name].items():errors.append(abs(value-frozen['scopes'][name][k]))
    result['all']['aupro_0.30']=pro.compute();errors.append(abs(result['all']['aupro_0.30']-frozen['scopes']['all']['aupro_0.30']))
    cut=np.array([engine.thresholds(r['roll'])['review'] for r in records]);pred=scores>=cut;tp=int(np.sum(pred&(labels==1)));fp=int(np.sum(pred&(labels==0)))
    after={p.name:sha(p) for p in [engine.model_path,engine.config_path]};passed=before==after and max(errors)<=1e-6 and score_error<=1e-5 and (originals is None or map_error<=1e-5) and tp==240 and fp==26
    output={'passed':passed,'images':len(records),'native_maps_bit_exact':native_exact,'stored_maps_bit_exact':stored_exact,'native_map_max_abs_error':map_error if originals is not None else None,'native_score_max_abs_error':score_error,'maximum_metric_abs_error':max(errors),'scopes':result,'operating':{'TP':tp,'FP':fp,'recall':tp/687,'precision':tp/(tp+fp),'normal_FPR':fp/4969},'hashes_before':before,'hashes_after':after,'no_refit':True,'seconds':time.perf_counter()-start,'map_reference_supplied':originals is not None}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,indent=2));assert passed,output
    print(json.dumps({k:v for k,v in output.items() if k!='scopes'},indent=2))
if __name__=='__main__':main()
