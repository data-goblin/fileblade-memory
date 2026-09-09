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

This file was written by an agent.

## Provider ownership and host availability

The blade contribution declares `provider: "Provider.qml"`. FileBlade creates
one nonvisual provider per enabled extension identity and shares it across its
views. It supplies `providerId`, the canonical absolute `providerRoot`, `files`,
and `inventoryComponentUrl` at construction. The provider exposes `inventory`,
`error`, `observers`, `viewCount`, `attach(context)`, `detach(context)`, and
`shutdown()`. Construction stays idle. Duplicate attachment is harmless, the
last detach suspends the shared inventory, and shutdown unloads it and refuses
late attachments. Existing inventory options and module contract 2 are preserved.

`Service.qml` resolves its directory from its own QML URL, even when the shell
strips the manifest's source directory. It lazily delegates to the same provider
only when an older FileBlade calls attach. The new host owns its provider directly,
so its companion Service never creates a second inventory. A legacy companion
without provider metadata still requires its actual old-shell service; a new
host on a restricted shell must request an extension update instead of loading
that old Service itself. Updating companions alone cannot repair an old core on
the restricted shell.

The missing-host card no longer inspects foreign registry entries.
`bin/fileblade-host-status` reads `omarchy plugin list --json`, validates unique
IDs and Boolean enabled states, then checks the enabled host with
`omarchy-shell data-goblin.fileblade status`. Each command has a two-second
deadline, 128 KiB stdout and 4 KiB stderr limits, and process-group cleanup.
Listings are limited to 512 rows; the helper returns only the four known companion
names and states. It reads no agent configuration and downloads nothing.

Missing, disabled, starting, ready, and unknown states stay distinct. Only a
confirmed disabled host offers the existing explicit Enable action. Starting
or failed checks never offer installation or enablement. The first enabled
companion in a successful listing owns the card. Polling backs off to 30 seconds,
and dismissal stops checks until the next shell start. This is presentation;
FileBlade's catalog separately controls permission to load providers and helpers.

The QML lifecycle and guard tests plus the standalone host-check tests are part
of `tests/run`. They cover cold creation, shared observers, last detach, terminal
shutdown, stripped manifests, both provider ownership paths, unavailable commands,
malformed authority, output limits and timeouts. User-visible expectation: an
enabled responding FileBlade produces no missing-host card on either shell API.

This file was written by an agent.

The explicit host-enable action acquires no code. It has a 20-second overall
command deadline with one second to terminate, a five-second enable deadline,
and bounded status attempts. It discards command output instead of accumulating
it in a shell variable; the button becomes retryable after the deadline.
