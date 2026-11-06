from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_grayscale(path: str | Path) -> np.ndarray:
    with Image.open(path) as source:
        return np.asarray(source.convert("L"), dtype=np.float32)

