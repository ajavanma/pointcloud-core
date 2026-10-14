"""Deterministic NumPy voxel aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real

import numpy as np

from .arrays import PointCloud, PointCloudError, _int64, validate_cloud


@dataclass(frozen=True)
class VoxelizedCloud:
    """Voxel arrays plus an index for each original row (-1 means excluded)."""

    voxel_coords: np.ndarray
    features: np.ndarray
    labels: np.ndarray | None
    point_to_voxel: np.ndarray
    point_indices: np.ndarray


def voxelize(
    cloud: PointCloud, voxel_size: float, *, ignore_label: int = -1
) -> VoxelizedCloud:
    """Floor-quantize coordinates using a scalar size in the input's units.

    Voxels are lexicographically ordered. Features use a mean; labels use a
    nonignored majority and the smallest numeric ID on ties. Labels are NOT
    remapped: pass LabelMap.encode() output to use declared training order.
    A shared finite-coordinate/feature mask preserves original row alignment.
    No origin offset or boundary epsilon is applied. Inputs are never mutated.
    """
    if isinstance(voxel_size, (bool, np.bool_)) or not isinstance(voxel_size, Real):
        raise PointCloudError("voxel_size: expected a finite positive real number")
    try:
        size = float(voxel_size)
    except (OverflowError, ValueError) as error:
        raise PointCloudError("voxel_size: expected a finite positive real number") from error
    if not np.isfinite(size) or size <= 0:
        raise PointCloudError("voxel_size: expected a finite positive real number")
    ignored = _int64(ignore_label, "ignore_label")
    source = validate_cloud(cloud)
    finite = np.isfinite(source.coords).all(axis=1) & np.isfinite(source.features).all(axis=1)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        quantized = np.floor(source.coords[finite] / size)
    if (
        not np.isfinite(quantized).all()
        or np.any(quantized < -(2**63))
        or np.any(quantized >= 2**63)
    ):
        raise PointCloudError("voxel coordinates: quantized values exceed the int64 range")
    coords, inverse, counts = np.unique(
        quantized.astype(np.int64), axis=0, return_inverse=True, return_counts=True
    )
    inverse = inverse.reshape(-1)
    features = np.zeros((len(coords), source.features.shape[1]), dtype=np.float64)
    # Scale each voxel/feature independently. Summing raw values can overflow;
    # dividing each contribution by the count first can erase subnormal values.
    # Normalized contributions are bounded by 1. Divide their sum only once,
    # then restore the original scale. All-zero columns retain their zeros.
    maxima = np.zeros_like(features)
    finite_features = source.features[finite]
    np.maximum.at(maxima, inverse, np.abs(finite_features))
    scales = maxima[inverse]
    with np.errstate(over="ignore", invalid="ignore"):
        normalized = np.divide(
            finite_features, scales, out=np.zeros_like(finite_features), where=scales != 0
        )
        np.add.at(features, inverse, normalized)
        features /= counts[:, None]
        # A mean of values in [-1, 1] lies in [-1, 1]. Enforce that bound before
        # rescaling so rounding cannot turn a finite maximum into infinity.
        np.clip(features, -1, 1, out=features)
        features *= maxima
    if not np.isfinite(features).all():
        raise PointCloudError("features: voxel feature mean is not finite")
    labels = None
    if source.labels is not None:
        labels = np.full(len(coords), ignored, dtype=np.int64)
        valid_labels = source.labels[finite]
        included = valid_labels != ignored
        if np.any(included):
            pairs, frequencies = np.unique(
                np.column_stack((inverse[included], valid_labels[included])),
                axis=0, return_counts=True,
            )
            order = np.lexsort((pairs[:, 1], -frequencies, pairs[:, 0]))
            ranked = pairs[order]
            first = np.r_[True, ranked[1:, 0] != ranked[:-1, 0]]
            winners = ranked[first]
            labels[winners[:, 0]] = winners[:, 1]
    mapping = np.full(len(source.coords), -1, dtype=np.int64)
    mapping[finite] = inverse
    return VoxelizedCloud(coords, features, labels, mapping, source.point_indices)
