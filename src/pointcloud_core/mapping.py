"""Restore per-voxel values to original point rows."""

from __future__ import annotations

from numbers import Integral, Rational, Real

import numpy as np
from numpy.typing import ArrayLike

from .arrays import PointCloudError, _array, _integers


def _fill(value: Real, dtype: np.dtype):
    if not isinstance(value, (Real, np.bool_)):
        raise PointCloudError("fill_value: expected a real numeric scalar")
    if dtype.kind in "iu":
        if not isinstance(value, (Integral, np.bool_)):
            raise PointCloudError("fill_value: integer values require an integer fill")
        bounds = np.iinfo(dtype)
        if not bounds.min <= int(value) <= bounds.max:
            raise PointCloudError("fill_value: outside values' integer dtype range")
    elif dtype.kind == "b":
        if value not in (0, 1):
            raise PointCloudError("fill_value: boolean values require 0, 1, False or True")
    try:
        with np.errstate(over="ignore", invalid="ignore"):
            converted = np.asarray(value, dtype=dtype).item()
        finite_source = True if isinstance(value, Rational) else np.isfinite(value)
        if dtype.kind == "f" and finite_source and not np.isfinite(converted):
            raise PointCloudError("fill_value: outside values' floating dtype range")
    except (ValueError, OverflowError, TypeError) as error:
        if isinstance(error, PointCloudError):
            raise
        raise PointCloudError("fill_value: cannot represent scalar in values' dtype") from error
    return converted


def lift_voxel_values(
    values: ArrayLike, point_to_voxel: ArrayLike, *, fill_value: Real = -1
) -> np.ndarray:
    """Return ``[N, ...]`` values in source row order from ``[V, ...]`` values.

    Every mapping must be -1 or in [0, V). Excluded rows receive fill_value.
    The output preserves values' numeric dtype and never aliases the input.
    Fill must fit that dtype; integer arrays require integer fills. Floating
    payloads and fills may contain NaN/infinity. Point IDs are not row offsets.
    """
    payload = _array(values, "values")
    if payload.ndim < 1 or payload.dtype.kind not in "biuf":
        raise PointCloudError("values: expected numeric shape [V,...]")
    mapping = _integers(point_to_voxel, "point_to_voxel")
    if mapping.ndim != 1 or np.any(mapping < -1) or np.any(mapping >= len(payload)):
        raise PointCloudError("point_to_voxel: expected a vector of -1 or existing voxel indices")
    fill = _fill(fill_value, payload.dtype)
    result = np.full((len(mapping), *payload.shape[1:]), fill, dtype=payload.dtype)
    included = mapping >= 0
    result[included] = payload[mapping[included]]
    return result
