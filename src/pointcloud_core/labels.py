"""Explicit class-order mappings, independent of a dataset manifest."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from .arrays import PointCloudError, _int64, _integers


@dataclass(frozen=True)
class LabelMap:
    """Map ordered original class IDs to 0..C-1; encoded ignore is always -1."""

    class_ids: tuple[int, ...]
    ignore_label: int = -1

    def __post_init__(self) -> None:
        try:
            ids = tuple(_int64(value, "class_ids") for value in self.class_ids)
        except TypeError as error:
            raise PointCloudError("class_ids: expected a nonempty sequence of integers") from error
        if not ids or len(set(ids)) != len(ids):
            raise PointCloudError("class_ids: expected nonempty unique class IDs")
        ignored = _int64(self.ignore_label, "ignore_label")
        if ignored in ids:
            raise PointCloudError("ignore_label: must differ from every class ID")
        object.__setattr__(self, "class_ids", ids)
        object.__setattr__(self, "ignore_label", ignored)

    def encode(self, labels: ArrayLike) -> np.ndarray:
        """Encode every element; reject unknown IDs, even on excluded rows."""
        values = _integers(labels, "labels")
        result = np.full(values.shape, -1, dtype=np.int64)
        known = values == self.ignore_label
        for training_id, original_id in enumerate(self.class_ids):
            selected = values == original_id
            result[selected] = training_id
            known |= selected
        if not np.all(known):
            raise PointCloudError(f"labels: unknown class IDs: {np.unique(values[~known]).tolist()}")
        return result

    def decode(self, labels: ArrayLike) -> np.ndarray:
        """Restore original IDs and the original ignore label."""
        values = _integers(labels, "encoded labels")
        if np.any((values < -1) | (values >= len(self.class_ids))):
            raise PointCloudError("encoded labels: expected -1 or a declared encoded class ID")
        result = np.full(values.shape, self.ignore_label, dtype=np.int64)
        for training_id, original_id in enumerate(self.class_ids):
            result[values == training_id] = original_id
        return result
