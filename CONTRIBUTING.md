# Contributing

PointCloud Core is a small NumPy-only library. Keep file formats, dataset
manifests, model frameworks, storage, and CLI behavior outside its core API.

```sh
python -m pip install -e . 'build>=1.2,<2' 'twine>=6,<7'
python -m unittest discover -s tests -v
python -m build
python -m twine check --strict dist/*
```

Use a focused branch and include tests for changes to numerical behavior or
validation. Explain shape/dtype guarantees, invalid-point handling, label ties,
and original-row alignment when relevant. Use synthetic arrays in tests; do not
commit real datasets, model weights, local paths, credentials, or generated
outputs. Maintainers review API changes before a release.

Keep commit messages and pull-request titles short; put the explanation and
validation details in the pull-request description. Squash merges use the
pull-request title with an empty commit body.

CI tests Python 3.11 and 3.12 with the minimum supported NumPy and current
NumPy 2.x, then runs tests against an installed wheel outside the source tree.
No GPU is required. Preserve the [API compatibility policy](docs/api.md#compatibility-policy)
when preparing changes and record release changes in [CHANGELOG.md](CHANGELOG.md).
