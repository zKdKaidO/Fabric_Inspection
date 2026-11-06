from __future__ import annotations

import cv2
import numpy as np


def grid_to_anomaly_map(
    grid: np.ndarray,
    output_shape: tuple[int, int],
    gaussian_sigma: float = 1.5,
    clip: float = 25.0,
) -> np.ndarray:
    score = cv2.resize(
        np.asarray(grid, dtype=np.float32),
        (output_shape[1], output_shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )
    if gaussian_sigma > 0:
        score = cv2.GaussianBlur(score, (0, 0), gaussian_sigma)
    return np.clip(score, 0.0, clip).astype(np.float32)


def image_anomaly_score(anomaly_map: np.ndarray, quantile: float = 0.999) -> float:
    return float(np.quantile(anomaly_map, quantile))

