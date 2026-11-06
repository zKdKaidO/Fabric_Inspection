from __future__ import annotations

import cv2
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def image_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    if np.unique(labels).size < 2:
        return {"image_auroc": float("nan"), "image_auprc": float("nan")}
    return {
        "image_auroc": float(roc_auc_score(labels, scores)),
        "image_auprc": float(average_precision_score(labels, scores)),
    }


class BinaryHistogram:
    """Bounded-memory pixel AUROC/AP with fixed score bins."""

    def __init__(self, bins: int, minimum: float, maximum: float) -> None:
        self.edges = np.linspace(minimum, maximum + np.finfo(np.float32).eps, bins + 1)
        self.positive = np.zeros(bins, dtype=np.int64)
        self.negative = np.zeros(bins, dtype=np.int64)

    def update(self, scores: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(scores).reshape(-1)
        truth = np.asarray(labels, dtype=bool).reshape(-1)
        self.positive += np.histogram(values[truth], bins=self.edges)[0]
        self.negative += np.histogram(values[~truth], bins=self.edges)[0]

    def compute(self) -> dict[str, float]:
        positives = self.positive.sum()
        negatives = self.negative.sum()
        if positives == 0 or negatives == 0:
            return {"pixel_auroc": float("nan"), "pixel_auprc": float("nan")}
        tp = np.cumsum(self.positive[::-1], dtype=np.float64)
        fp = np.cumsum(self.negative[::-1], dtype=np.float64)
        recall = tp / positives
        fpr = fp / negatives
        precision = tp / np.maximum(tp + fp, 1)
        auroc = np.trapezoid(np.r_[0.0, recall], np.r_[0.0, fpr])
        auprc = np.sum(np.diff(np.r_[0.0, recall]) * precision)
        return {"pixel_auroc": float(auroc), "pixel_auprc": float(auprc)}


class PerRegionOverlapHistogram:
    """Binned threshold-free per-region overlap, normalized through max FPR."""

    def __init__(
        self, bins: int, minimum: float, maximum: float, maximum_fpr: float = 0.30
    ) -> None:
        if not 0 < maximum_fpr <= 1:
            raise ValueError("maximum_fpr must be in (0, 1]")
        self.edges = np.linspace(minimum, maximum + np.finfo(np.float32).eps, bins + 1)
        self.negative = np.zeros(bins, dtype=np.int64)
        self.regions: list[np.ndarray] = []
        self.maximum_fpr = maximum_fpr

    def update(self, scores: np.ndarray, mask: np.ndarray) -> None:
        values = np.asarray(scores, dtype=np.float32)
        truth = np.asarray(mask, dtype=bool)
        self.negative += np.histogram(values[~truth], bins=self.edges)[0]
        count, labels = cv2.connectedComponents(truth.astype(np.uint8), connectivity=8)
        for label in range(1, count):
            self.regions.append(np.histogram(values[labels == label], bins=self.edges)[0])

    def compute(self) -> float:
        negatives = int(self.negative.sum())
        if negatives == 0 or not self.regions:
            return float("nan")
        fpr = np.cumsum(self.negative[::-1], dtype=np.float64) / negatives
        overlaps = []
        for histogram in self.regions:
            size = int(histogram.sum())
            overlaps.append(np.cumsum(histogram[::-1], dtype=np.float64) / size)
        pro = np.mean(np.stack(overlaps), axis=0)
        fpr = np.r_[0.0, fpr]
        pro = np.r_[0.0, pro]
        inside = fpr < self.maximum_fpr
        boundary = float(np.interp(self.maximum_fpr, fpr, pro))
        x = np.r_[fpr[inside], self.maximum_fpr]
        y = np.r_[pro[inside], boundary]
        return float(np.trapezoid(y, x) / self.maximum_fpr)
