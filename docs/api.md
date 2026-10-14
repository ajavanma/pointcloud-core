# API reference

All public imports come from `pointcloud_core`. Invalid inputs raise
`PointCloudError`, a subclass of `ValueError`.

## PointCloud and validation

`PointCloud(coords, features=None, labels=None, point_indices=None)` stores
array-like inputs. Construction itself does not validate them.

`validate_cloud(cloud)` returns normalized, independently owned NumPy arrays:

| Field | Shape | Normalized dtype | Contract |
| --- | --- | --- | --- |
| `coords` | `[N, 3]` | float64 | Real numeric, nonempty |
| `features` | `[N, F]` | float64 | Optional; missing becomes `[N, 0]` |
| `labels` | `[N]` | int64 | Optional; no implicit float/bool conversion |
| `point_indices` | `[N]` | int64 | Unique, nonnegative; missing becomes `arange(N)` |

Numeric strings, complex arrays, booleans as coordinates/labels/IDs, ragged
arrays, integer overflow, and mismatched row counts are rejected. Integer
coordinate/feature inputs normalize to float64 and therefore inherit its
precision limits. NaN/infinity rows are retained for shared-mask preprocessing,
but there must be at least one row with finite coordinates and features.

Dataclasses are frozen, but their NumPy arrays remain mutable. Validation and
voxelization do not return arrays that share memory with their inputs.

## LabelMap

`LabelMap(class_ids, ignore_label=-1)` takes nonempty, unique int64 class IDs in
the desired encoded order. The ignore label must differ from every class ID.
Original IDs may be negative. Encoded class IDs are `0..C-1`; encoded ignore is
always `-1`.

- `encode(labels)` rejects every unknown original ID and preserves input shape.
- `decode(labels)` accepts only `-1` or an encoded class ID and restores the
  original label space.

Both return owned int64 arrays. Apply `encode` before voxelization so unknown
labels are checked even on rows later removed by the finite mask.

## Voxelization

`voxelize(cloud, voxel_size, *, ignore_label=-1)` validates the cloud, excludes
nonfinite coordinate/feature rows, and returns `VoxelizedCloud`:

| Field | Shape | Meaning |
| --- | --- | --- |
| `voxel_coords` | `[V, 3]` | Sorted int64 floor-quantized coordinates |
| `features` | `[V, F]` | float64 mean features |
| `labels` | `[V]` or `None` | int64 nonignored majority labels |
| `point_to_voxel` | `[N]` | int64 voxel indices; `-1` for excluded rows |
| `point_indices` | `[N]` | Original point IDs in original row order |

The size must be finite and positive; booleans are rejected. Units are the
caller's responsibility. Quantization must fit int64, and feature means must
remain finite. Labels are not remapped automatically. Ties choose the smallest
numeric ID; voxels containing only ignored labels remain ignored.

Feature means scale each voxel/feature by its maximum absolute value before
summing, divide once by the count, then restore that scale. This avoids raw-sum
overflow and preserves constant subnormal values that dividing each input first
could erase. All-zero columns remain zero. As with ordinary floating reduction,
mixed magnitudes and cancellation may lose precision; results are repeatable for
the same arrays and runtime but may differ after row permutation or across runtimes.

## Original-row reconstruction

`lift_voxel_values(values, point_to_voxel, *, fill_value=-1)` maps numeric
`[V, ...]` values to `[N, ...]` rows. It supports labels, scores, and other
per-voxel payloads, including boolean arrays with an appropriate fill.

- Each mapping must be `-1` or a valid voxel index; other negative indices are
  rejected instead of using NumPy's negative indexing.
- `fill_value` is a scalar used for all trailing components of excluded rows.
- The output retains the payload dtype. Integer payloads require integer fills
  within range; boolean payloads require 0/1 or False/True. Floating fills must
  fit the dtype's range, although explicit NaN/infinity are allowed.
- Floating payload values are copied without a finiteness policy; callers
  decide whether their algorithm permits NaNs or infinities.
- Empty typed mappings are supported. With no voxels, every mapping must be
  `-1`. Original point IDs never serve as offsets into the values array.

This function does not decode label classes. Compose it with `LabelMap.decode`
when returning from encoded model labels to original dataset labels.
