"""RAW-FABRID dataset adapter using the already-audited split and mask rule."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from PIL import Image

@dataclass(frozen=True)
class RawFabridRecord:
    path: Path
    split: str
    label: int
    parent: str
    roll_id: str
    row_offset: int
    col_offset: int
    defect_area: int
    mask_path: Path | None


def _roll_id(parent: str) -> str:
    match = re.match(r"(Rollo[^_]+)", parent)
    if not match:
        raise ValueError(f"Cannot parse roll id from {parent!r}")
    return match.group(1)


class RawFabridDataset:
    """Patch dataset that preserves provenance and uses foreground == 255."""

    def __init__(
        self,
        root: str | Path,
        metadata_csv: str | Path,
        coco_json: str | Path,
        split: str,
        image_size: int = 256,
        indices: Iterable[int] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.image_size = image_size
        self.records = self._load_records(Path(metadata_csv), Path(coco_json), split)
        if indices is not None:
            self.records = [self.records[i] for i in indices]

    def _load_records(self, metadata_csv: Path, coco_json: Path, split: str) -> list[RawFabridRecord]:
        split_to_type = {"train": "train_good", "test": None}
        if split not in split_to_type:
            raise ValueError("split must be 'train' or 'test'")
        metadata = pd.read_csv(metadata_csv)
        rows = {str(row.patch_name): row for row in metadata.itertuples(index=False)}
        with coco_json.open("r", encoding="utf-8") as handle:
            coco_images = json.load(handle)["images"]
        records: list[RawFabridRecord] = []
        for item in coco_images:
            kind = str(item["type"])
            if split == "train" and kind != "train_good":
                continue
            if split == "test" and kind not in {"test_good", "test_defect"}:
                continue
            name = str(item["file_name"])
            row = rows[name]
            subset = "train/good" if kind == "train_good" else kind.replace("_", "/")
            label = int(kind == "test_defect")
            mask_path = self.root / "ground_truth" / "defect" / name if label else None
            records.append(
                RawFabridRecord(
                    path=self.root / subset / name,
                    split=kind,
                    label=label,
                    parent=str(item["parent"]),
                    roll_id=_roll_id(str(item["parent"])),
                    row_offset=int(item["r_offset"]),
                    col_offset=int(item["c_offset"]),
                    defect_area=int(row.defect_area),
                    mask_path=mask_path,
                )
            )
        records.sort(key=lambda r: str(r.path))
        missing = [str(r.path) for r in records if not r.path.is_file()]
        if missing:
            raise FileNotFoundError(f"Missing {len(missing)} dataset files; first: {missing[0]}")
        return records

    def __len__(self) -> int:
        return len(self.records)

