from __future__ import annotations

import cv2
import numpy as np

from .gabor import GaborFilterBank


def sample_feature_grid(features: np.ndarray, stride: int) -> np.ndarray:
    if stride < 1:
        raise ValueError("stride must be at least one pixel")
    offset = stride // 2
    return features[offset::stride, offset::stride].astype(np.float32)


def gabor_dense_features(
    image: np.ndarray,
    bank: GaborFilterBank,
    local_window: int = 15,
    include_energy: bool = True,
    include_dispersion: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Return dense local features and individual Gabor magnitudes."""
    response = bank.responses(image)
    channels: list[np.ndarray] = []
    for index in range(response.shape[-1]):
        magnitude = response[..., index]
        mean = cv2.boxFilter(
            magnitude, cv2.CV_32F, (local_window, local_window),
            normalize=True, borderType=cv2.BORDER_REFLECT101,
        )
        mean_square = cv2.boxFilter(
            magnitude * magnitude, cv2.CV_32F, (local_window, local_window),
            normalize=True, borderType=cv2.BORDER_REFLECT101,
        )
        if include_energy:
            channels.append(np.sqrt(np.maximum(mean_square, 0.0)))
        if include_dispersion:
            channels.append(np.sqrt(np.maximum(mean_square - mean * mean, 0.0)))
    dense = np.stack(channels, axis=-1)
    return dense.astype(np.float32), response


def gabor_local_features(
    image: np.ndarray,
    bank: GaborFilterBank,
    local_window: int = 15,
    stride: int = 4,
    include_energy: bool = True,
    include_dispersion: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Return sampled-grid features and full-resolution Gabor magnitudes."""
    dense, response = gabor_dense_features(
        image, bank, local_window, include_energy, include_dispersion
    )
    return sample_feature_grid(dense, stride), response

