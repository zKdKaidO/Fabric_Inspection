"""Display artifacts do not modify the saved continuous anomaly map."""
from pathlib import Path
import cv2
import numpy as np
from scipy import ndimage
from PIL import Image

def save_evidence(folder,image,anomaly,pixel_threshold):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    if image.shape[:2]!=anomaly.shape or not np.isfinite(anomaly).all():raise ValueError('Invalid map/image evidence')
    paths={k:folder/name for k,name in [('original_path','original.png'),('anomaly_map_path','anomaly_map.npy'),('anomaly_map_image_path','anomaly_heatmap.png'),('overlay_path','overlay.png')]}
    Image.fromarray(image).save(paths['original_path']);np.save(paths['anomaly_map_path'],anomaly.astype(np.float32))
    # Fixed display scale, not image-specific calibration.
    heat=cv2.applyColorMap((np.clip(anomaly/25,0,1)*255).astype(np.uint8),cv2.COLORMAP_INFERNO)
    if not cv2.imwrite(str(paths['anomaly_map_image_path']),heat):raise OSError('Could not save heatmap')
    active=anomaly>=pixel_threshold;overlay=image.astype(np.float32);overlay[active]=.45*overlay[active]+.55*np.array([255,32,32])
    Image.fromarray(np.clip(overlay,0,255).astype(np.uint8)).save(paths['overlay_path'])
    labels,n=ndimage.label(active);regions=[]
    for k in range(1,n+1):
        ys,xs=np.where(labels==k)
        if len(ys)>=4:regions.append({'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'area_px':int(len(ys)),'score':float(anomaly[ys,xs].max())})
    return {k:str(p) for k,p in paths.items()},sorted(regions,key=lambda r:r['score'],reverse=True)
