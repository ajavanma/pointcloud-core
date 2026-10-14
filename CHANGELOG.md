# Changelog

## 0.1.0 — prepared, not yet published

- Introduce NumPy-only point-cloud array validation and explicit label maps.
- Add deterministic voxel aggregation with original-row and point-ID mappings.
- Add safe reconstruction of per-voxel labels and multidimensional values.
- Document numerical contracts and provide synthetic CPU tests and wheel CI.
- Declare the supported top-level API and compatibility policy for 0.x releases.
- Prepare source and wheel distributions, release notes, and an approved
  environment workflow for PyPI Trusted Publishing.

This is a separate library extracted from PointCloud Workflows. It has no PCW
artifact-format dependency and is not yet a dependency of PCW.
