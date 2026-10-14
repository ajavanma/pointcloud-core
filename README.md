# PointCloud Core

NumPy primitives for validating point clouds, aggregating points into voxels,
and mapping voxel results back to the original points. No GPU, training
framework, command-line interface, or dataset format is required.

The project is in private development at version `0.1.0.dev0`. It has not been
published to PyPI; install from a local checkout for now. The API is provisional
until the first supported release.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Python 3.11 or later and NumPy 1.26.4 or later (below 3) are required.

## Example

```python
import numpy as np
from pointcloud_core import LabelMap, PointCloud, lift_voxel_values, voxelize

classes = LabelMap((7, 42), ignore_label=255)
cloud = PointCloud(
    coords=[[0.1, 0, 0], [0.2, 0, 0], [1.1, 0, 0], [np.nan, 0, 0]],
    features=[[2], [4], [8], [10]],
    labels=classes.encode([7, 7, 42, 255]),
    point_indices=[100, 105, 900, 901],
)
voxels = voxelize(cloud, voxel_size=1.0)
assert voxels.voxel_coords.tolist() == [[0, 0, 0], [1, 0, 0]]
assert voxels.features.tolist() == [[3.0], [8.0]]
assert voxels.point_to_voxel.tolist() == [0, 0, 1, -1]

# A model or another algorithm can supply one value per voxel.
encoded_predictions = np.array([0, 1], dtype=np.int64)
point_predictions = classes.decode(
    lift_voxel_values(encoded_predictions, voxels.point_to_voxel)
)
assert point_predictions.tolist() == [7, 7, 42, 255]
assert voxels.point_indices.tolist() == [100, 105, 900, 901]
```

Every output row maps back to an input row. Original point IDs remain separate
from row positions. Invalid coordinate/feature rows receive mapping `-1`, so
they cannot accidentally index the final voxel during reconstruction.

## Numerical contract

- Coordinates use floor division by a scalar voxel size in the caller's units.
  Negative coordinates are handled by floor; no origin offset or boundary
  epsilon is applied.
- Voxels are sorted lexicographically. Features are arithmetic means. Labels
  use the most frequent nonignored value, with the smallest numeric label on
  ties. Use `LabelMap` first when declared class order should break ties.
- Coordinates/features normalize to float64; labels, coordinates of voxels,
  mappings, and point IDs use int64. Inputs are not mutated.
- Coordinates and features share one finite mask. At least one finite row is
  required. Input labels are validated even on excluded rows.
- Operations hold arrays in memory. This is not a streaming or out-of-core
  implementation, and floating reductions are not promised to be bit-identical
  across arbitrary input permutations or NumPy versions.

See the [API reference](docs/api.md), [contribution guide](CONTRIBUTING.md), and
[release plan](docs/releasing.md).

## Relationship to PointCloud Workflows

The numerical methods were extracted and generalized from
[PointCloud Workflows](https://github.com/ajavanma/PointCloud-Workflows).
PointCloud Core owns only in-memory array operations. PCW owns dataset
manifests, file readers, model execution, checkpoints, and run artifacts. PCW
does not yet depend on this unpublished library; integration will follow a
tested release. The original MIT attribution is retained in [LICENSE](LICENSE).
