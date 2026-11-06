"""Local API for the single frozen inspection product."""
from pathlib import Path
from typing import Literal
import sqlite3
import uvicorn
from fastapi import FastAPI,HTTPException,UploadFile,File,Form,Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field,ConfigDict,field_validator
from .database import ProductDatabase
from .service import ProductService
from .catalog import DemoCatalog
from ..vision.classical.engine import ClassicalInspectionEngine,PROJECT_ROOT

Profile=Literal['Rollo1A','Rollo2A','Rollo3A','Rollo4A','Rollo5A','Rollo6A','Rollo7A']
class StrictModel(BaseModel):model_config=ConfigDict(extra='forbid')
class FabricCreate(StrictModel):
    fabric_id:str=Field(min_length=2,max_length=64,pattern=r'^[A-Za-z0-9][A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=120)
    description:str=Field(default='',max_length=1000)
    profile:str
    @field_validator('profile')
    @classmethod
    def known_profile(cls,value):
        if value not in [f'Rollo{i}A' for i in range(1,8)]:
            raise ValueError('New-fabric model fitting is not supported in this frozen research release.')
        return value
class SampleSelection(StrictModel):
    paths:list[str]=Field(min_length=1,max_length=50)
class DemoInspection(StrictModel):
    fabric_id:str
    image_path:str
class OperatorReview(StrictModel):
    decision:Literal['CONFIRMED_DEFECT','FALSE_ALARM','UNSURE']
    notes:str=Field(default='',max_length=2000)

def create_app(storage_dir=None,service=None):
    storage=Path(storage_dir or PROJECT_ROOT/'inspection_store/product').resolve();storage.mkdir(parents=True,exist_ok=True)
    if service is None:
        database=ProductDatabase(storage/'inspection.db');engine=ClassicalInspectionEngine()
        try:catalog=DemoCatalog(engine.config)
        except FileNotFoundError:catalog=None
        service=ProductService(database,storage,engine,catalog)
    database=service.database
    app=FastAPI(title='RAW-FABRID Frozen Solution 1',version='2.0.0');app.state.service=service
    app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['*'],allow_headers=['*'])
    evidence=storage/'inspections';evidence.mkdir(exist_ok=True)
    app.mount('/artifacts/inspections',StaticFiles(directory=evidence),name='evidence')
    if service.catalog:app.mount('/demo-data',StaticFiles(directory=service.catalog.root),name='demo-data')
    def call(fn,*args):
        try:return fn(*args)
        except KeyError as e:raise HTTPException(404,str(e)) from e
        except sqlite3.IntegrityError as e:raise HTTPException(409,'Fabric ID already exists or record conflict') from e
        except (ValueError,FileNotFoundError,OSError) as e:raise HTTPException(400,str(e)) from e
    def catalog():
        if service.catalog is None:raise HTTPException(503,'Local RAW-FABRID dataset is unavailable; upload a full parent frame instead')
        return service.catalog
    @app.get('/health')
    def health():return {'status':'ok','engine':'classical_solution1','profiles':list(service.engine.models),'model_sha256':service.engine.config['model_sha256'],'new_fabric_fitting_supported':False}
    @app.get('/profiles')
    def profiles():return [{'profile':p,'label':p} for p in service.engine.models]
    @app.get('/fabrics')
    def fabrics():return database.list_fabrics()
    @app.post('/fabrics',status_code=201)
    def create(payload:FabricCreate):return call(service.create_fabric,payload.model_dump())
    @app.get('/fabrics/{fabric_id}')
    def fabric(fabric_id:str):
        f=call(service._fabric,fabric_id);f['samples']=database.list_samples(fabric_id);return f
    @app.post('/fabrics/{fabric_id}/samples')
    async def samples(fabric_id:str,files:list[UploadFile]=File(...)):
        call(service._fabric,fabric_id)
        paths=[str(call(service.store_upload,f.filename or 'sample.png',await f.read(),'normal')) for f in files]
        count=call(service.add_samples,fabric_id,paths);return {'sample_count':count}
    @app.post('/fabrics/{fabric_id}/sample-selection')
    def select(fabric_id:str,payload:SampleSelection):
        f=call(service._fabric,fabric_id);c=catalog()
        for p in payload.paths:
            r=call(c.record,p)
            if r.split!='train_good' or r.roll_id!=f['profile']:raise HTTPException(400,'Select training-normal samples from the fabric profile')
        return {'sample_count':call(service.add_samples,fabric_id,payload.paths,'frozen_normal_catalog')}
    @app.post('/fabrics/{fabric_id}/commission')
    def commission(fabric_id:str):return call(service.commission,fabric_id)
    @app.post('/inspect')
    async def inspect(fabric_id:str=Form(...),file:UploadFile=File(...)):
        call(service._fabric,fabric_id)
        p=call(service.store_upload,file.filename or 'inspection.png',await file.read(),'inspection')
        return service.present_inspection(call(service.inspect,fabric_id,p))
    @app.get('/demo/samples')
    def demo_samples(profile:Profile,split:Literal['train','test']='test',limit:int=Query(24,ge=1,le=50)):
        return catalog().samples(profile,split,limit)
    @app.post('/demo/inspect')
    def demo_inspect(payload:DemoInspection):
        r=call(catalog().record,payload.image_path)
        if r.split=='train_good':raise HTTPException(400,'Choose an unseen test image for demonstration inspection')
        return service.present_inspection(call(service.inspect,payload.fabric_id,r.path))
    @app.get('/inspections')
    def history(fabric_id:str|None=None,limit:int=Query(100,ge=1,le=500)):
        return [service.present_inspection(r) for r in database.list_inspections(fabric_id=fabric_id,limit=limit)]
    @app.get('/inspections/{inspection_id}')
    def detail(inspection_id:str):
        r=database.get_inspection(inspection_id)
        if r is None:raise HTTPException(404,'Inspection not found')
        return service.present_inspection(r)
    @app.post('/inspections/{inspection_id}/review')
    def review(inspection_id:str,payload:OperatorReview):
        r=database.get_inspection(inspection_id)
        if r is None:raise HTTPException(404,'Inspection not found')
        if r['decision']=='PASS':raise HTTPException(409,'Human review is available for flagged inspections')
        return service.present_inspection(database.save_review(inspection_id,payload.decision,payload.notes))
    return app

def run():uvicorn.run('fabric_inspection.product.api:create_app',factory=True,host='127.0.0.1',port=8000)
if __name__=='__main__':run()
