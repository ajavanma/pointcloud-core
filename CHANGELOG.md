# Changelog

## 0.1.0.dev0 — unreleased

- Introduce NumPy-only point-cloud array validation and explicit label maps.
- Add deterministic voxel aggregation with original-row and point-ID mappings.
- Add safe reconstruction of per-voxel labels and multidimensional values.
- Document numerical contracts and provide synthetic CPU tests and wheel CI.

This is a separate library extracted from PointCloud Workflows. It has no PCW
artifact-format dependency and is not yet a dependency of PCW.
