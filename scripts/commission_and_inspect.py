"""Reproducible product workflow against a running local API; never fits a model."""
import argparse,json
from pathlib import Path
import httpx

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',required=True,choices=[f'Rollo{i}A' for i in range(1,8)])
    p.add_argument('--fabric-id');p.add_argument('--image',type=Path,help='Full physical source image; omit to select a catalog test patch')
    p.add_argument('--api',default='http://127.0.0.1:8000');a=p.parse_args();fabric=a.fabric_id or f'demo-{a.profile}'
    with httpx.Client(base_url=a.api,timeout=180) as c:
        existing=c.get('/fabrics/'+fabric)
        if existing.status_code==404:
            r=c.post('/fabrics',json={'fabric_id':fabric,'name':f'Demo {a.profile}','profile':a.profile});r.raise_for_status()
        else:
            existing.raise_for_status()
            if existing.json()['profile']!=a.profile:raise ValueError('Existing fabric uses a different profile')
        r=c.get('/demo/samples',params={'profile':a.profile,'split':'train','limit':4});r.raise_for_status();paths=[s['path'] for s in r.json()]
        r=c.post(f'/fabrics/{fabric}/sample-selection',json={'paths':paths});r.raise_for_status()
        r=c.post(f'/fabrics/{fabric}/commission');r.raise_for_status()
        if r.json()['commissioning_status']!='READY':raise RuntimeError(r.json()['commissioning_summary']['message'])
        if a.image:
            with a.image.open('rb') as f:r=c.post('/inspect',data={'fabric_id':fabric},files={'file':(a.image.name,f)})
        else:
            samples=c.get('/demo/samples',params={'profile':a.profile,'split':'test','limit':2});samples.raise_for_status()
            r=c.post('/demo/inspect',json={'fabric_id':fabric,'image_path':samples.json()[1]['path']})
        r.raise_for_status();print(json.dumps(r.json(),indent=2))
if __name__=='__main__':main()
