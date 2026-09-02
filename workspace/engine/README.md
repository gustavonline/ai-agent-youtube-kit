# ACS technical boundary

The technical surface is intentionally small:

| Responsibility | Surface |
| --- | --- |
| Content graph and handoff validation | `scripts/check-content-graph.mjs` |
| Repository/link/stale checks | `scripts/check-repository.mjs` |
| External Diffusion checkout, DAPI, and browser companion | `scripts/diffusion-studio.mjs` |
| Contract and platform proof | `tests/*.test.mjs` |
| Human production context | `templates/` |
| Optional local helpers | transcript/reference scripts and requirements |

These scripts do not edit media, generate derivatives, package posts, or
publish. Diffusion editor code is external and HyperFrames specialist work stays upstream.
