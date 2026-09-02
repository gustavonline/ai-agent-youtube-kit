# CI evidence

`.github/workflows/ci.yml` configures Node 22 checks on Ubuntu, macOS, and
Windows. It runs the zero-dependency tests, neutral graph/handoff proof,
repository link/stale-reference checks, and whitespace validation.

The matrix is configuration evidence until an authorized push runs it. Local
macOS results are not Windows/Linux execution results. The Diffusion launcher
tests prove checkout, package, host, and DAPI command/path construction for each
OS; physical Electron, browser-companion, and export evidence must be reported
per OS. Current repository acceptance physically covers macOS only.
