# FreeCut browser Studio

FreeCut is the one ordinary local Studio. It is a built browser app served on
strict loopback; no Electron/Tauri or other desktop shell is required.

The repository-local `freecut-studio` skill owns setup, check, work, and
recovery details. The ACS launcher adds only deterministic checkout validation
and a cross-platform Vite preview command.

## Launch from ACS

```text
node workspace/engine/scripts/freecut-studio.mjs check
node workspace/engine/scripts/freecut-studio.mjs serve
```

When the preview is ready, Codex opens `http://127.0.0.1:4173/` in its in-app
browser. The human chooses the native FreeCut workspace and controls folder
permission. Native project bytes remain external ACS truth until a reviewed
export is copied into a production.

## Platform paths

| OS | Fixed checkout | Preview executable |
| --- | --- | --- |
| macOS | `~/.local/share/freecut` | `npm` |
| Linux | `~/.local/share/freecut` | `npm` |
| Windows | `%LOCALAPPDATA%\freecut` | `npm.cmd` |

All platforms pass the same arguments:

```text
run preview -- --host 127.0.0.1 --port 4173 --strictPort
```

The built Studio uses the same Node/Vite/Chromium route on all three. The
launcher never binds beyond loopback or opens an OS-default browser.

## Handoff back to ACS

After human review, copy the approved export into the production. Record it as
a `master` node with actual hash, provenance, lineage, and review reference.
Every excerpt, adaptation, variant, companion, or promotion is a separate node
with separate review. Validate the graph and optional supervised publisher
handoff. ACS performs no second render.
