"""In-memory point-cloud contracts. No file formats or storage conventions."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike


class PointCloudError(ValueError):
    """Input arrays or parameters violate a point-cloud operation's contract."""


@dataclass(frozen=True)
class PointCloud:
    """Aligned source arrays; call :func:`validate_cloud` to normalize them.

    Rows identify points. ``point_indices`` are unique external point IDs,
    independent of row positions. Missing IDs default to ``arange(N)``.
    Missing features become an ``[N, 0]`` array. Labels remain optional.
    """

    coords: ArrayLike
    features: ArrayLike | None = None
    labels: ArrayLike | None = None
    point_indices: ArrayLike | None = None


def _array(value: ArrayLike, name: str) -> np.ndarray:
    try:
        return np.asarray(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise PointCloudError(f"{name}: expected a rectangular numeric array") from error


def _integers(value: ArrayLike, name: str) -> np.ndarray:
    result = _array(value, name)
    if result.dtype.kind not in "iu":
        raise PointCloudError(f"{name}: expected an integer array (not booleans)")
    if result.dtype.kind == "u" and result.size and np.any(result > np.iinfo(np.int64).max):
        raise PointCloudError(f"{name}: values exceed the int64 range")
    return result.astype(np.int64, copy=True)


def _int64(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise PointCloudError(f"{name}: expected an integer in the int64 range")
    result = int(value)
    if not -(2**63) <= result < 2**63:
        raise PointCloudError(f"{name}: expected an integer in the int64 range")
    return result


def _reals(value: ArrayLike, name: str) -> np.ndarray:
    result = _array(value, name)
    if result.dtype.kind not in "iuf":
        raise PointCloudError(f"{name}: expected a real numeric array")
    # An overflow during conversion must not silently turn a finite source row
    # into a discarded row in voxelize(). NaNs/infinities in the input are kept.
    with np.errstate(over="ignore", invalid="ignore"):
        converted = result.astype(np.float64, copy=True)
    if np.any(np.isfinite(result) & ~np.isfinite(converted)):
        raise PointCloudError(f"{name}: finite values exceed the float64 range")
    return converted


def validate_cloud(cloud: PointCloud) -> PointCloud:
    """Return owned float64/int64 arrays without reordering or dropping rows.

    Coordinates must be nonempty ``[N, 3]``; features are ``[N, F]`` (F may be
    zero), labels and IDs are ``[N]``. Nonfinite coordinate/feature rows are
    retained, but at least one row must have finite coordinates and features.
    Voxelization later excludes invalid rows with a shared mask.
    """
    if not isinstance(cloud, PointCloud):
        raise PointCloudError("cloud: expected a PointCloud")
    coords = _reals(cloud.coords, "coords")
    if coords.ndim != 2 or coords.shape[1] != 3 or len(coords) == 0:
        raise PointCloudError("coords: expected nonempty shape [N,3]")
    count = len(coords)
    features = (
        np.empty((count, 0), dtype=np.float64)
        if cloud.features is None else _reals(cloud.features, "features")
    )
    if features.ndim != 2 or features.shape[0] != count:
        raise PointCloudError("features: expected shape [N,F] aligned with coords")
    labels = None if cloud.labels is None else _integers(cloud.labels, "labels")
    if labels is not None and labels.shape != (count,):
        raise PointCloudError("labels: expected shape [N] aligned with coords")
    indices = (
        np.arange(count, dtype=np.int64)
        if cloud.point_indices is None else _integers(cloud.point_indices, "point_indices")
    )
    if indices.shape != (count,):
        raise PointCloudError("point_indices: expected shape [N] aligned with coords")
    if np.any(indices < 0) or len(np.unique(indices)) != count:
        raise PointCloudError("point_indices: expected unique nonnegative original point IDs")
    if not np.any(np.isfinite(coords).all(axis=1) & np.isfinite(features).all(axis=1)):
        raise PointCloudError("cloud: no rows have finite coordinates and features")
    return PointCloud(coords, features, labels, indices)
