import numpy as np

# Fixed supports, not hyperparameters searched in this experiment.
DY,DX=np.meshgrid(np.arange(-12,13,dtype=np.int32),np.arange(-12,13,dtype=np.int32),indexing='ij')
CENTER=(np.abs(DY)<=7)&(np.abs(DX)<=7)
RING=~CENTER
OFFSETS=((DY[CENTER],DX[CENTER],112),(DY[RING],DX[RING],199))
assert int(CENTER.sum())==225 and int(RING.sum())==400


def mirror_indices(index,length):
    """Existing OpenCV REFLECT101 index convention; support radius<image extent."""
    index=np.where(index<0,-index,index)
    return np.where(index>=length,2*length-2-index,index).astype(np.int32)


def contrast_grid(normalized_halo,tile_origin):
    """Lower-median15x15 minus surrounding25x25\15x15, at the unchanged grid."""
    cy,cx=map(int,tile_origin)
    ys=cy+np.arange(2,256,4,dtype=np.int32)
    xs=cx+np.arange(2,256,4,dtype=np.int32)
    medians=[]
    for dy,dx,order in OFFSETS:
        yy=mirror_indices(ys[:,None]+dy[None,:],normalized_halo.shape[0])
        xx=mirror_indices(xs[:,None]+dx[None,:],normalized_halo.shape[1])
        samples=normalized_halo[yy[:,None,:],xx[None,:,:]]
        samples.partition(order,axis=-1)
        medians.append(samples[...,order].copy())
    return np.abs(medians[0]-medians[1]).astype(np.float32)


def normalized_parent_window(gray,parent,y,x):
    """Exact first part of frozen H1.extract, for normal-column preparation only."""
    low,high=np.percentile(gray,(5,95))
    y0,x0=max(0,y-20),max(0,x-20)
    halo=parent[y0:min(parent.shape[0],y+276),x0:min(parent.shape[1],x+276)]
    normalized=np.clip((halo-low)/max(float(high-low),1.),0,1).astype(np.float32)
    return normalized,(y-y0,x-x0)
