# Contributing

PointCloud Core is a small NumPy-only library. Keep file formats, dataset
manifests, model frameworks, storage, and CLI behavior outside its core API.

```sh
python -m pip install -e . 'build>=1.2,<2'
python -m unittest discover -s tests -v
python -m build
```

Use a focused branch and include tests for changes to numerical behavior or
validation. Explain shape/dtype guarantees, invalid-point handling, label ties,
and original-row alignment when relevant. Use synthetic arrays in tests; do not
commit real datasets, model weights, local paths, credentials, or generated
outputs. Maintainers review API changes before a release.

CI tests Python 3.11 and 3.12 with the minimum supported NumPy and current
NumPy 2.x, then runs tests against an installed wheel outside the source tree.
No GPU is required.
