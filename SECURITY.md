# Security policy

Version 0.1.0 is prepared but has not been published. Once released, the latest
0.1.x patch will receive fixes while that series is supported. The library accepts
in-memory NumPy arrays; it does not deserialize files, load models, execute
plugins, or access a network. Callers must still bound input size before
processing untrusted arrays: voxelization allocates memory proportional to the
input and sorts coordinates.

Do not post suspected vulnerabilities or credentials in public issues. Use
[GitHub's private vulnerability reporting form](https://github.com/ajavanma/pointcloud-core/security/advisories/new)
to contact the maintainer confidentially.

Include a minimal synthetic reproducer, Python/NumPy versions, expected
behavior, and actual behavior. Avoid sharing private point clouds or other
sensitive data in the report.
