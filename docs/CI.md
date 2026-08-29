# CI Evidence

`.github/workflows/ci.yml` is configured for Ubuntu, macOS, and Windows across
Python 3.10–3.13. It installs FFmpeg through each runner's bounded package
manager, installs the package in a venv-backed job environment, runs help and
the relocated deterministic test suite, the ACS shell/stale-path/no-runtime
guard, and checks whitespace. The deterministic suite includes structural and
history proof tests; local Build evidence reports the result from the
environment where it ran rather than a fixed test count.

The checkout and Python setup actions are pinned to immutable commit revisions.
No third-party FFmpeg action is required. The matrix is configuration proof in
the Build checkout; live OS execution remains pending until the branch is
pushed by the separately authorized Ship step. Local macOS results must not be
reported as Windows/Linux results.
