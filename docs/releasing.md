# Release preparation

The public source repository prepares version **0.1.0** of distribution
`pointcloud-core`, imported as `pointcloud_core`. It has not yet been published
to PyPI. The package name is not reserved by this repository; PyPI's project
JSON endpoint returned 404 on 2026-10-14. Register and verify the publisher
before creating a release tag or requesting publication.

The first release contains only NumPy array primitives. See the
[release notes](releases/0.1.0.md) and [API compatibility policy](api.md#compatibility-policy).
It contains no research images, datasets, model weights, copied Git history,
file readers, model frameworks, or PCW artifact schemas.

## Maintainer checklist

1. Review the API and numerical changes in `CHANGELOG.md`, preserve the MIT
   attribution, and set the release version in
   `src/pointcloud_core/_version.py`. Verify both the source archive and wheel
   metadata, contents, and license. Run the built wheel outside the checkout
   against minimum NumPy 1.26.4 and current NumPy 2.x.
2. Merge the release PR after all four required Python/NumPy checks pass. Run
   **Prepare or publish Python package** on `main` with `publish` left **false**.
   This rehearses the build, metadata validation, and wheel tests and retains
   the resulting distributions for seven days. It does not start the publish
   job, request environment approval, or grant OIDC credentials.
   Prepare an unpublished GitHub release draft with these tested distributions
   attached for review. Keep the draft unpublished and leave the version tag
   uncreated until publication is authorized.
3. Configure a [PyPI Trusted Publisher](https://docs.pypi.org/trusted-publishers/)
   for project `pointcloud-core`, owner `ajavanma`, repository `pointcloud-core`,
   workflow `release.yml`, and environment `pypi`. For a new PyPI project, use a
   pending publisher. Provider-side setup is still pending; a workflow file
   alone does not register a publisher or reserve a project name. Trusted
   Publishing uses short-lived OIDC credentials, with no permanent upload token.
4. Verify GitHub's `pypi` environment requires `@ajavanma` approval and restricts
   deployments to tags matching `v*`. Keep prevention of self-review disabled
   for this solo-maintainer approval step. Verify version tags cannot be
   modified or deleted. These settings are separate from the workflow file.
5. After an explicit publication decision, create immutable tag `v0.1.0` on the
   reviewed release commit. Dispatch **Prepare or publish Python package** on
   that tag with `publish` set **true**. The workflow rebuilds and tests the
   distributions, then waits for `pypi` environment approval before publishing
   with attestations. Only the publish job has OIDC permission.
6. Verify a fresh installation from the intended index and refresh the draft's
   wheel and source archive from the final successful publishing run. That run
   rebuilds the distributions, so the preparation artifacts must not be assumed
   byte-identical. Verify their checksums against the PyPI files before
   publishing the GitHub release; immutable releases prevent replacing assets
   afterwards. Record the published release and checksums, and update the
   README and release status. Never move a published tag or reuse a version.
   If a publish partially fails, inspect the index before retrying; the workflow
   does not silently skip existing files.

The destination is [PyPI: pointcloud-core](https://pypi.org/project/pointcloud-core/).
It remains a planned destination until the first authorized publication succeeds.
Documentation lives in this repository; no separate docs host is required for
this initial API. The original RPTU documentation is a separate project.

## Workflow guards

`.github/workflows/release.yml` has only a manual dispatch trigger and defaults
`publish` to false. Both modes refuse a private or unintended repository and
require the selected commit to be on `main`'s history. Preparation accepts
`main` or an exact version tag; publishing requires an exact `v<package version>`
tag. Development and local versions are refused. Neither mode creates tags or
GitHub releases.

The workflow builds a source archive and a wheel from that archive, checks them
with `twine check --strict`, and tests the installed wheel outside the checkout
against NumPy 1.26.4 and current NumPy 2.x. Publishing downloads those same tested
distributions. Pull-request CI and the build job have read-only repository
permissions. Build-only dispatch skips the publish job entirely.

## Repository controls

On 2026-10-14, the repository was made public and its branch, security, and
external-contributor controls below were applied and verified. The `pypi`
environment requires `@ajavanma` review, allows self-review for the sole
maintainer, and accepts only `v*` tags. An active tag ruleset blocks updates and
deletion of `v*` tags with no bypass actors. PyPI's provider-side Trusted
Publisher still needs registration before publication. Immutable GitHub
releases are enabled, protecting release assets after publication while
allowing an unpublished draft to be reviewed and refreshed.

The maintained public-repository configuration is previewed with
`python scripts/apply-public-settings.py` and applied by an administrator with
`--apply`. The script requires this repository to already be public and never
changes visibility or publishes anything. It stops on a failed setting; earlier
applied settings remain. It verifies protected `main`, the four up-to-date CI
checks from the GitHub Actions application, secret scanning, push protection,
dependency alerts, private vulnerability reporting, and approval for all
external contributors' workflow runs.

The branch policy requires pull requests, linear history, resolved conversations,
and forbids force pushes and deletions, including for administrators. Required
review count is zero so a solo maintainer can merge a tested PR. Repository
settings use squash-only merges, automatic branch cleanup, and read-only
Actions tokens without PR-review permission. The initial Python and GitHub
Actions CodeQL scans completed with zero findings. The active `main` CodeQL
ruleset requires analysis, blocks security findings at high severity or above
and code-quality findings at error severity, and has no bypass actors.

## Integration into PointCloud Workflows

PCW uses a narrow adapter with compatibility tests, pinned to the prepared
`0.1.0` source revision `5c28a700c30aee6186cfe30f6cd74708289f0743` and its archive
hash. This supports integration before PyPI publication without depending on an
unpublished package-index version. PCW still owns its manifests, readers, model
execution, checkpoints, and artifact schemas. Its adapter retains the historical
divide-before-sum feature means; Core's public numerical API keeps its scaled
mean. See the [integration guide](https://github.com/ajavanma/PointCloud-Workflows/blob/main/docs/core-integration.md)
and [standalone example](https://github.com/ajavanma/PointCloud-Workflows/blob/main/examples/core_roundtrip.py).

After Core is published, replace PCW's transitional source dependency with the
tested package-index version, regenerate PCW's lockfile, and rerun compatibility
checks before publishing PCW. Its release workflow rejects direct URL
dependencies.
