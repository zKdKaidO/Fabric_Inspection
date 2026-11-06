from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class GaborSpec:
    wavelength: float
    orientation_deg: float
    sigma: float
    gamma: float = 0.5

    @property
    def label(self) -> str:
        return f"lambda={self.wavelength:g}, theta={self.orientation_deg:g}deg"


class GaborFilterBank:
    """Small multi-scale, multi-orientation complex Gabor bank.

    Real and quadrature kernels form a phase-insensitive magnitude response, so
    harmless weave phase shifts do not dominate the texture measurement.
    """

    def __init__(
        self,
        wavelengths: list[float] | tuple[float, ...],
        orientations_deg: list[float] | tuple[float, ...],
        sigma_ratio: float = 0.56,
        gamma: float = 0.5,
        phases_rad: tuple[float, float] = (0.0, math.pi / 2),
    ) -> None:
        self.specs: list[GaborSpec] = []
        self.kernels: list[tuple[np.ndarray, np.ndarray]] = []
        for wavelength in wavelengths:
            sigma = sigma_ratio * wavelength
            kernel_size = max(7, int(math.ceil(6 * sigma)) | 1)
            for orientation in orientations_deg:
                spec = GaborSpec(float(wavelength), float(orientation), sigma, gamma)
                kernels = []
                for phase in phases_rad:
                    kernel = cv2.getGaborKernel(
                        (kernel_size, kernel_size), sigma, math.radians(orientation),
                        wavelength, gamma, phase, ktype=cv2.CV_32F,
                    )
                    kernel -= kernel.mean()
                    kernel /= max(float(np.linalg.norm(kernel)), 1e-8)
                    kernels.append(kernel.astype(np.float32))
                self.specs.append(spec)
                self.kernels.append((kernels[0], kernels[1]))

    def __len__(self) -> int:
        return len(self.kernels)

    def responses(self, image: np.ndarray) -> np.ndarray:
        """Return phase-invariant response magnitudes as [H,W,F]."""
        channels = []
        for real_kernel, imaginary_kernel in self.kernels:
            real = cv2.filter2D(image, cv2.CV_32F, real_kernel, borderType=cv2.BORDER_REFLECT101)
            imaginary = cv2.filter2D(
                image, cv2.CV_32F, imaginary_kernel, borderType=cv2.BORDER_REFLECT101
            )
            channels.append(cv2.magnitude(real, imaginary))
        return np.stack(channels, axis=-1).astype(np.float32)

