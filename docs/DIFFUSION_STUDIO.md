# Diffusion Studio route

Diffusion Studio is ACS's only ordinary video Studio. The editor remains an
external thin fork of official upstream; ACS owns only a small launcher and the
production files, reviews, and content graph returned from the editor.

## Reviewed pin and ownership

- fork: <https://github.com/onlinesourdough/editor.git>
- tested branch: `codex/diffusion-upstream-browser-companion-r6`
- pin: `71a306fb33d06f969114a47e9eba85aa47cef395`
- official upstream: <https://github.com/diffusionstudio/editor.git>
- reviewed upstream base: `635a2907d9dd717879d6f7bdf9a78ee42910415c`
- upstream PR: <https://github.com/diffusionstudio/editor/pull/54>

The checkout keeps official upstream as `origin` and the thin fork as `fork`.
Do not copy editor code into ACS. Do not update silently. `check` and `status`
report the pinned local state plus live fork/upstream heads so drift is visible
without changing the checkout.

## Setup and check

The deterministic defaults are `~/Library/Application Support/Agentic Content
System/diffusion-studio/editor` on macOS,
`~/.local/share/agentic-content-system/diffusion-studio/editor` on Linux, and
`%LOCALAPPDATA%\Agentic Content System\diffusion-studio\editor` on Windows. An
arbitrary checkout override is not accepted.

```text
node workspace/engine/scripts/diffusion-studio.mjs setup
node workspace/engine/scripts/diffusion-studio.mjs check
```

`setup` is an explicit external write. It clones official upstream, adds the
fork, checks out the exact pin detached, and runs the repository's lockfile and
declared desktop packaging command. The command reads the upstream public
browser-build values from `apps/web/.env.example` into the packaging process;
it does not write an `.env` file or copy credentials into ACS. It refuses a
mismatched existing checkout.

## Open, inspect, and stop

```text
node workspace/engine/scripts/diffusion-studio.mjs open workspace/productions/<slug>/diffusion-project
node workspace/engine/scripts/diffusion-studio.mjs status
node workspace/engine/scripts/diffusion-studio.mjs logs
node workspace/engine/scripts/diffusion-studio.mjs stop
```

`open` accepts only a project inside `workspace/productions/`. The pinned built
DAPI CLI launches the checkout's packaged Electron host in the background,
opens and compiles the project, and returns JSON containing the one-time
companion URL. Codex opens that URL in its built-in browser; neither launcher
nor DAPI opens an OS browser.

Electron and DAPI remain authoritative for open, compile, watch, export, AI,
filesystem, and logs. The loopback browser companion is human-only and
read-only: preview, play/pause, scrub, and inspection. It has no browser DAPI,
persistent edits, export, AI, checkout, authentication, arbitrary filesystem
access, or widened main-process wire. The host is hidden where supported and
may truthfully report `minimized-fallback` otherwise. The companion is
local-only; status must show zero egress attempts.

`stop` releases the companion listener and resources, then runs `dapi context`
to prove the authoritative host survived. It does not stop or corrupt DAPI.

## Platform evidence and re-pin

Inspect command/path construction without claiming physical parity:

```text
node workspace/engine/scripts/diffusion-studio.mjs describe --platform darwin
node workspace/engine/scripts/diffusion-studio.mjs describe --platform linux
node workspace/engine/scripts/diffusion-studio.mjs describe --platform win32
```

Repository acceptance physically proves macOS only unless a task records
otherwise. Linux and Windows evidence covers deterministic paths and commands,
not installation, Electron, browser, or export execution.

To update, rebase the thin fork against official upstream and review that fork
change first. Then update the ACS branch/pin/base constants in one bounded
change and repeat checkout, build, DAPI, export, browser-companion, denial,
stop, and three-platform construction proof. Roll back an ACS re-pin by
reverting that ACS commit and restoring the last reviewed external application;
never hide drift by resetting owner state.
