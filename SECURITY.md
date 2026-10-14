# Security policy

This pre-release library has no supported public release yet. It accepts
in-memory NumPy arrays; it does not deserialize files, load models, execute
plugins, or access a network. Callers must still bound input size before
processing untrusted arrays: voxelization allocates memory proportional to the
input and sorts coordinates.

Do not post suspected vulnerabilities or credentials in public issues. During
private development, report them to the repository owner through an existing
private channel. Before public launch, enable and verify GitHub private
vulnerability reporting and link its reporting form here.

Include a minimal synthetic reproducer, Python/NumPy versions, expected
behavior, and actual behavior. Avoid sharing private point clouds or other
sensitive data in the report.
