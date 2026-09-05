# Memory integration

Memory requires an enabled FileBlade host with module contract 2. The provider
service owns one shared `ArtifactInventory`; visual modules attach only while
open and expanded. Search, selection, grouping and presentation remain in the
shared FileBlade widgets and each view's state.

The manifest declares the bundled `agent-memoryctl` helper's read-only `list`
and mutating `apply` methods. FileBlade's resident backend runs them with bounded
input/output and an eight-second deadline. Nothing compiles or downloads when
the plugin loads. Python 3 and the enabled FileBlade host are required.

Scans cannot publish results for an earlier project or overwrite post-mutation
state. Accepted link changes retain their original project and finish even if
the visual module closes; disabling the provider cancels its owned work.

Discovery records source directories, including parents of missing sources,
for FileBlade's filesystem subscriptions. New sources, edits, removals and
directory replacements trigger a debounced rescan. Closing the last view stops
reads and watches; reopening reconciles changes made while hidden. Watch plans
are capped at 512 directories and 64 KiB of serialized paths. Incomplete watch
coverage is shown in the status; Rescan remains available.

Glob discovery bounds both visited directories and entries before collecting
matches. Symlink traversal must remain inside the configured root. Actionable
paths use the host's native-byte codec, independently of display labels.

Link changes use the core's native mutation boundary. Creation is exclusive;
unlink captures the intended symlink's identity and refuses a changed entry.
Descriptor-relative operations do not follow a replacement parent symlink.

`tests/run` checks discovery, link safety, path identity, watch planning, shared
UI contracts and read-only helper imports. The shared inventory's asynchronous
lifetime regressions live in FileBlade's gate.

## Missing host

`Service.qml` loads `HostGuard.qml` once the shell injects `pluginRegistry`.
`HostGuard.js` decides from the registry alone: nothing shows while
`data-goblin.fileblade` is installed and enabled; otherwise the alphabetically
first enabled plugin that declares a `data-goblin.fileblade/*` extension owns
one overlay listing every waiting extension. Install runs detached through
`sh -c` because the clone landing in the plugins directory hot-reloads every
third-party plugin, guard included: `omarchy plugin add --enable --yes` (or
`omarchy plugin enable` when the host is installed but disabled), a wait for
the entry in `shell.json` and the host IPC target, then
`omarchy restart shell`. Failure raises a critical notification with the last
error line and rescans plugins so a fresh guard reappears. The close glyph or
Escape hides it until the next shell start. The card reuses the host's look:
`assets/fileblade-logo.png` tinted with the accent colour, and the welcome
tab's accent Install button. `tests/tst_host_guard.qml` covers the
decision table offscreen.
