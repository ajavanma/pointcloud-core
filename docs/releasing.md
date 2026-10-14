# Release preparation

This repository and package remain private/unpublished until an explicit
publication decision. The selected distribution name is `pointcloud-core` and
the import name is `pointcloud_core`. The name is not reserved by this source
tree. PyPI's project JSON endpoint returned 404 on 2026-10-14; recheck when
registering a publisher.

1. Review the provisional API and test the built wheel outside the checkout.
   Run the minimum NumPy and current NumPy test jobs; inspect both distribution
   archives for unintended files.
2. Set a supported release version and document API/numerical changes in
   `CHANGELOG.md`. Preserve the MIT notice. This repository contains no research
   images, datasets, model weights, or copied repository history.
3. Approve the repository visibility change separately. Inspect the offline
   preview from `python scripts/apply-public-settings.py`. Once the repository
   is public, an administrator can run it with `--apply` to configure and verify
   protected main, the four Python/NumPy CI checks, secret scanning, push
   protection, dependency alerts, and private vulnerability reporting. The
   script refuses private or unintended repositories and never changes
   visibility. It stops on a failed setting; earlier applied settings remain.
4. Set up a repository/workflow/environment-scoped
   [PyPI Trusted Publisher](https://docs.pypi.org/trusted-publishers/) for project
   `pointcloud-core`, owner `ajavanma`, repository `pointcloud-core`, workflow
   `release.yml`, and environment `pypi`. Account setup is still required;
   this file does not reserve the package name. Create the GitHub `pypi`
   environment with `@ajavanma` as required reviewer and deployments restricted
   to tags matching `v*`. Leave prevention of self-review disabled for the
   solo-maintainer approval step. Protect version tags from modification and
   deletion. Trusted Publishing uses short-lived OIDC credentials; no permanent
   upload token is needed.
5. Publish a tested immutable version only after explicit release approval.
   Verify installation from the intended index in a fresh environment. No
   package or credentials have been published by this preparation.
6. Integrate the published library into PointCloud Workflows through a narrow
   adapter with array-parity tests. PCW's artifact schemas stay in PCW. Do not
   add an unresolved package-index dependency while this library is unpublished.

Documentation currently lives in this repository. A separate public docs host
is optional for the initial small API; choose and configure one at launch if
needed. Existing RPTU documentation is not this library's documentation site.

## Manual package workflow

The prepared `.github/workflows/release.yml` has only a manual dispatch trigger.
It refuses private repositories, unintended repository names, branch refs,
development versions, tags that do not exactly match `v<package version>`, and
commits outside `main`. Publishing requires a non-development version in
`src/pointcloud_core/_version.py` and the corresponding immutable tag.

After the release PR passes all four required CI jobs and merges, create the
version tag on the reviewed commit and dispatch **Publish Python package** on
that tag. The workflow builds the source archive and wheel, checks package
metadata, and tests the built wheel outside the checkout against NumPy 1.26.4
and current NumPy 2.x. The later `pypi` job downloads the tested distributions
and publishes them with attestations only after environment approval. Only
that job has OIDC permission; pull-request CI has read-only permissions.

PyPI's target is `https://pypi.org/project/pointcloud-core/`. It is a planned
destination until the first authorized publication succeeds. Verify a fresh
installation from that index afterwards. Never move a published tag or reuse
a version. If a publish partially fails, inspect the index before retrying;
the workflow does not silently skip existing files.

The branch policy requires PRs, all four up-to-date matrix checks from the
GitHub Actions application, linear history, and resolved conversations. It
blocks force pushes/deletions and applies to administrators. Required review
count is zero to allow a solo maintainer to merge a tested PR. Before accepting
external PRs, require approval for all external contributors' workflow runs and
keep repository token defaults read-only.

## Private staging status (2026-10-14)

Both repositories remain private. Squash-only merges, automatic branch cleanup,
read-only Actions tokens without PR review approval, and dependency alerts are
configured. GitHub rejected protected branches, secret scanning, private
vulnerability reporting, external-contributor workflow approval, and required
environment reviewers under the current private-repository eligibility. These
controls remain pending; workflow environment names alone do not enforce review.
The public-only publication guard prevents release dispatches in this state.

After an explicitly authorized visibility change, apply and verify the prepared
controls, configure protected release environments and immutable release tags,
and enable Python CodeQL default setup in Security settings before publishing.
