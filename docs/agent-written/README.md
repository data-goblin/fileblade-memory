# Omarchy Agent Memory

A blade module that shows the instruction, rule, and durable auto-memory files
that coding agents load, grouped by scope and kind, for the project you have
selected in the file tree. Every row carries a strip of agent marks; clicking a
mark links or unlinks that file for that agent through a single symlink.

## Required dependency and Install order

**Omarchy Fileblade (`data-goblin.fileblade`) must be installed and enabled first.**

Requires Omarchy 4.0.2 or later, core FileBlade and Python 3.11+. Follow the direct GitHub installation
and removal instructions in the [root README](../../README.md), then select
Memory in a FileBlade module slot. No marketplace listing is required.

The contribution uses `extensions["data-goblin.fileblade/blade"]` with
`hostContract: 2`. Its service supplies the missing-host prompt and provider
lifecycle. With FileBlade unavailable, the shared guard offers to install or
enable the host. It does not install anything without an explicit action.
Inventories reuse FileBlade's shared services; see the
[host contract](https://github.com/data-goblin/fileblade/blob/main/EXTENSIONS.md).
Removing the extension preserves host layout/view state, recoverable bins and
previous changes to the user's files or agent configuration.

## What it shows

```yaml
instructions:   CLAUDE.md, CLAUDE.local.md, AGENTS.md, AGENTS.override.md,
                GEMINI.md, copilot-instructions.md, *.instructions.md
rules:          .claude/rules/**, .agents/rules/**, .agent/rules/**,
                antigravity plugin rules/
auto-memory:    ~/.claude/projects/<project>/memory/MEMORY.md and topic files,
                badged agent-written, with the type and modified frontmatter
system-prompt:  Pi SYSTEM.md and APPEND_SYSTEM.md
extra:          any Markdown root you configure yourself (see below)
```

Each row is one file on disk, keyed by its real path. Where several agents read
the same file, through the same name or through symlinks with different names,
it stays one row and lists every reader with that agent's documented load
order. A shared `AGENTS.md` shows as one entry read by Codex, OpenCode, Pi, and
Copilot CLI rather than four duplicates. A row whose file is excluded by
`claudeMdExcludes`, inline in a managed settings file, or excluded for only some
readers carries `(excluded)`, `(inline)`, or `(partly excluded)` after its name.

### Column control

The gray label at the right of the header (or of the slot tab bar when several
modules share a slot) is the column control for this module. It is the shared
Fileblade control, so it behaves the same in every blade:

```yaml
Left click:     cycles the sort on the current column: descending, ascending, off
                (numbers and dates start descending, text starts ascending).
                The label shows ↓ or ↑ while sorted
Right click:    opens the menu: the column radio list (Off, Agents, Updated,
                Created, Tokens (estimated), Characters, Words, Size, Summary),
                Sort ascending, Sort descending, Clear sort, Filter…, Clear filter.
                Enter, Space, the Menu key, and Shift+F10 open the same menu;
                inside it j/k, arrows, g/G, Home/End, Enter, and Escape work
Filter…:        a popup with one section per date and number column. Date
                sections take since and until (ISO prefixes such as 2026-08, or
                7d, 3w, 2m, 1y, today, yesterday) and offer 7d, 30d, 90d, and 1y
                preset chips. Number sections take min and max (1.2k, 3m). Rows
                that fail any clause are hidden before grouping; the label shows
                a filter glyph while a filter is active
```

The column, sort, and filter are stored in that Fileblade slot's state under the
keys `metric`, `sort`, and `filter`; **Agents** is the default column. Sorting
happens inside each group, so the User and Project sections keep their order
while their rows reorder. Number columns draw a data bar behind the value,
scaled to the largest visible row.

Updated is the file's modification time. Created is the Linux filesystem birth
time when the filesystem exposes it, otherwise it displays as unavailable.
Characters are Unicode code points, so CJK, Cyrillic, Greek, Korean, combining
marks, and emoji remain valid input. Words use Unicode-aware word matching.
Tokens are an explicitly approximate UTF-8 byte count divided by four, rounded
up; they are not a model-specific tokenizer result. Size is the exact file byte
count.

Content-derived counts are bounded to the same 8 KiB descriptor read used for
discovery. Files larger than that still show exact size and dates, while token,
character, and word values display as unavailable rather than pretending a
partial count is complete. Inline managed instructions and remote-source
markers likewise expose no content counts because their text is deliberately
not read.

Summary is not a Memory category. It is the existing row description: the
Markdown frontmatter `description` value when present, otherwise the first
meaningful non-frontmatter line (with a leading Markdown heading marker
removed). It remains searchable even when another column or Off is selected.

### Agents strip

With the Agents column selected, every file row ends in a strip of agent marks:
one mark per agent the host detected as installed (a binary on `PATH` or the
agent's home directory present), in a fixed order, preceded by a robot glyph
when more than one agent is installed. A mark in its brand colour means that
agent reads this file, according to the readers discovery found; a grey mark
means it does not.

```yaml
click a grey mark:      runs apply --state on for that agent
click a coloured mark:  runs apply --state off for that agent
click the robot glyph:  runs apply for every installed agent at once: on unless
                        every installed agent already reads the file, in which
                        case off. The real file is never removed by this
hover:                  the agent name, and "Apply to all agents" on the glyph
```

While an apply runs the header status reads `Applying…`. When it finishes the
module rescans, so the strip reflects the readers discovery actually finds
rather than what the click intended. A refused apply leaves the backend
message in the header status until the next rescan (Shift+R, a selection
change, or reopening the blade).

### Per-agent names

`apply` uses the file name and directory that each agent documents, the same
ones discovery reads. Project scope places the link beside the memory file;
user scope places it in the agent's own directory, creating that directory
when it is missing.

```yaml
claude-code:  project CLAUDE.md beside the file      user ~/.claude/CLAUDE.md
codex:        project AGENTS.md beside the file      user $CODEX_HOME/AGENTS.md, default ~/.codex/AGENTS.md
opencode:     project AGENTS.md beside the file      user $XDG_CONFIG_HOME/opencode/AGENTS.md, default ~/.config/opencode/AGENTS.md
pi:           project AGENTS.md beside the file      user ~/.pi/agent/AGENTS.md
copilot-cli:  project AGENTS.md beside the file      user $COPILOT_HOME/copilot-instructions.md, default ~/.copilot/copilot-instructions.md
antigravity:  project <root>/.agents/rules/<file>    user ~/.gemini/GEMINI.md
```

Antigravity reads no project-root instruction file, only
`.agents/rules/*.md`, so its project link is placed there under the memory
file's real basename.

### What apply creates and refuses

```
agent-memoryctl apply --project <dir> --id <row id> --agent <agent id> [--agent <id> ...] --state on|off --json
-> { "ok", "schemaVersion": 1, "project", "message", "results": [ { "agent", "ok", "changed", "message", "touched": [paths] } ] }
```

`--id` is the row id from `list`, `--project` is the same anchor `list` was run
with, and `--agent` repeats once per agent. Top-level `ok` is true only when
every agent result is ok; `message` joins the failures as `agent: message` and
is what the header shows. Exit status is 0 whenever JSON was written.

`on` creates exactly one symlink per agent, named as in the table above, whose
target is the real path of the memory file. It reports `changed: false` with
`ok: true` when that name already resolves to the same real file, whether as
the file itself or through an existing link.

`on` refuses, with `ok: false`, `changed: false`, and nothing touched, when:

```yaml
- the name already exists as a real file, or as a symlink to a different file
- the row is a rules, auto-memory, system-prompt, or extra file: only
  instructions files have a documented per-agent equivalent
- the row's scope is managed, plugin, or extension, which have no per-agent
  location
- the file sits outside the directories between the project root and the
  selected folder, where the agent would not read the new name
- the agent id or the row id is unknown
- the link path would fall outside the agent directory or the project root
```

`off` removes that agent's link only when the path is a symlink resolving to
the memory file's real path. It never deletes a real file: when the name is the
memory file itself, a separate real file, or a link to some other file, it
reports `ok: true`, `changed: false`, and says why. A symlink you made by hand
at an agent's documented name is treated exactly like one apply made.

`list` writes nothing; a test snapshots a fixture tree before and after two
listings and asserts it is byte-for-byte unchanged, and the discovery modules
contain no link, unlink, or write calls at all.

### Agents and documented sources

Adapters follow each project's own documentation. A path that an agent does not
document is not claimed for that agent, so `~/.claude/AGENTS.md` is never listed
as a Claude Code source.

```yaml
claude-code:
  user:     ~/.claude/CLAUDE.md, ~/.claude/rules/, ~/.claude/projects/<p>/memory/, managed policy CLAUDE.md
  project:  CLAUDE.md, .claude/CLAUDE.md, CLAUDE.local.md, .claude/rules/
codex:
  user:     $CODEX_HOME/AGENTS.override.md else AGENTS.md
  project:  AGENTS.override.md, AGENTS.md per directory
opencode:
  user:     ~/.config/opencode/AGENTS.md, ~/.claude/CLAUDE.md fallback
  project:  AGENTS.md, CLAUDE.md
pi:
  user:     ~/.pi/agent/{AGENTS,CLAUDE,SYSTEM,APPEND_SYSTEM}.md
  project:  AGENTS.override.md, AGENTS.md, CLAUDE.md, .pi/SYSTEM.md
copilot-cli:
  user:     $COPILOT_HOME/copilot-instructions.md, instructions/**.instructions.md
  project:  .github/copilot-instructions.md, .github/instructions/**, AGENTS.md, CLAUDE.md, .claude/CLAUDE.md, GEMINI.md
antigravity:
  user:     ~/.gemini/GEMINI.md, plugin rules/
  project:  .agents/rules/, .agent/rules/
```

### Configuration read to find sources

Agent settings are read only to learn *where* memory lives, never to display
their contents:

```yaml
codex config.toml:      project_doc_fallback_filenames adds extra project
                        filenames to the AGENTS chain; each name must be a bare
                        basename, and at most eight are honoured
claude settings.json:   autoMemoryDirectory relocates the auto-memory root;
                        claudeMdExcludes marks matching files excluded, per
                        reader, so a shared file excluded only for Claude Code
                        is badged partly-excluded rather than hidden
claude managed claudeMd: inline managed instructions are represented as a
                        location and a byte count on the settings file itself.
                        The inline text is never read into a row
opencode.json:          instructions entries are expanded as local paths and
                        globs relative to that config file, bounded to 64
                        matches and contained below its directory. Remote URL
                        entries are counted, never fetched, and their URLs are
                        never emitted
COPILOT_CUSTOM_INSTRUCTIONS_DIRS: each existing directory in the comma
                        separated list is listed, at most eight
```

No configuration value other than these location hints reaches the output, and
a test asserts a canary string planted in every one of those config files never
appears in the payload.

Every environment variable naming a path is treated as a filesystem path rather
than display text. Leading, trailing, and repeated spaces and any Unicode are
preserved exactly, so a directory genuinely called `  дом   с  пробелами  `
resolves. Only an unset or empty value, an embedded NUL, or a value longer than
4096 characters is refused. The same rule covers
`CODEX_HOME`, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
`XDG_CONFIG_HOME`, for `apply` as much as for `list`.

Only bare filenames are honoured. A name is accepted when it is a real
filename, including CJK, Cyrillic, Greek, emoji, combining marks, a leading dot
such as `.context.md`, and consecutive dots such as `notes..md`. A name is
rejected when it is empty, longer than 255 characters, exactly `.` or `..`,
contains a path separator, or carries a NUL, control, format, or surrogate
character.

Every settings file is read no-follow and bounded, so a symlinked or oversized
file is skipped. The two default `/etc` locations must additionally be regular,
root owned, and not group or world writable. A path you select yourself through
one of the two environment variables is read on its own terms, without that
ownership requirement, because it is your choice rather than a system location
and the primary docs impose no ownership rule on it. Nothing else from those
settings files is read or emitted.

Two further documented keys shape the search, resolved through the same layers:

```yaml
context.discoveryMaxDirs:       number, default 200. Bounds the downward search
                                only, capped at 200 by this plugin regardless of
                                the configured value. It never limits the anchor
                                directory or the upward chain, so a value of 0
                                still lists the anchor and its ancestors
context.memoryBoundaryMarkers:  array, default [".git"]. Upward traversal stops
                                at the first directory containing any marker.
                                An empty array disables parent traversal, so
                                only the anchor directory is read. Traversal also
                                stops at the real home for an anchor below it, so
                                it never climbs into shared parents
```

### What it deliberately does not show

Session transcripts, private internal databases, and configuration files are
out of scope: `~/.claude/projects/**/*.jsonl`, `~/.codex/*.sqlite`,
`~/.pi/agent/sessions/`, `settings.json`, `trust.json`, `models.json`. Only
public Markdown document contracts are listed.

## Configuring extra roots

Personal note stores are opt-in and never hard-coded. Create
`$XDG_CONFIG_HOME/data-goblin.fileblade-memory/config.json`:

```json
{
  "extraRoots": [
    { "path": "~/notes/agents", "label": "notes" }
  ]
}
```

Entries appear under **Extra roots** and are marked `user-configured` so they
are never confused with a documented agent path. At most 16 roots are read.
They cannot be linked to an agent through the strip, because no agent
documents a location for them.

## Keys

Everything the mouse can do here has a keyboard equivalent.

```yaml
j / k, Down / Up:        move
h / l, Left / Right:     collapse or expand a branch, or step to its parent
g, Home:                 first row          G, End: last row
Ctrl+D / Ctrl+U:         half page down or up
PageDown / PageUp:       page down or up
/:                       search, Escape leaves the search
s:                       cycle the sort on the current column
f:                       open the filter popup for the current module
Enter, o:                open the file in your editor (same as double click)
r:                       reveal the file in the file tree
d, Delete:               delete the file (soft delete to the bin, or forever); restore from the Bin group
Shift+R:                 rescan
Escape:                  back out, then return focus to the previous module
Tab / Shift+Tab:         move between slots
Ctrl+Tab / Ctrl+Shift+Tab: left untouched so the host cycles slot tabs
```

Movement, hierarchy, paging, activation, reveal, search, sort, filter, and slot
traversal come from the host's shared `ArtifactTree`. This module claims only
`Shift+R` for rescanning. Its modifier test proves every host tab-cycle and
navigation chord remains unconsumed.

## Bin

`d` or `Delete` on a row (or the red trash glyph at the right of a hovered row)
asks whether to delete the file. The dialog, the bin, and the file moving all
belong to the Fileblade host (`ArtifactBin`); this module only describes the
row: its id, name, kind, scope, real path, and every path agents read it
through (the file plus each symlink). "Soft delete" hands that to
`fileblade _backend bin-put --module memory`, which copies every piece into
`$XDG_DATA_HOME/fileblade/bin/memory/<stamp>-<id>/` (default
`~/.local/share/fileblade/bin/memory/`) next to a `manifest.json`, then
unlinks the originals. Binned files show under a `Bin` group; `d` there offers
"Restore", which puts every piece back only if nothing took its place, or
"Delete forever". A rule that is itself a symlink into a vault is binned as
the symlink, so the vault file is never touched. Inline content that lives in
a settings file cannot be binned. The host refuses a path that no longer
resolves to the row's real file, never follows symlinks, and never walks or
removes anything it did not list first.

## Boundaries

- **One writer, one operation.** `list` never writes. `apply` is the only
  command that touches disk, and each agent result is at most one `symlink` or
  one `unlink` of a symlink that resolves to the memory file. Deleting and
  restoring are done by the Fileblade host's bin, never by this helper. It never writes
  file contents, never renames or replaces, never deletes a real file, and
  never follows a link to delete what it points at. Tests pin that the
  discovery modules contain no write, link, delete, or subprocess calls and
  that `apply.py` contains exactly one `os.symlink` and one `os.unlink`.
- **Bounded.** Descriptor reads stop at 8 KiB, files above 4 MiB are skipped,
  rule trees are walked 4 levels deep, and scans stop at 512 sources and 1000
  rows. Serialized helper output is capped at 1 MiB, reporting `truncated`
  rather than growing.
- **Irregular files ignored.** Each candidate is opened non-blocking and must
  pass an `fstat` regular-file check, so a FIFO or device node cannot stall the
  shell.
- **Observed inventories.** Views subscribe while open and expanded. The host
  owns shared scans, watches, deadlines and cancellation, and stops background
  inventory work when there are no observers.
- **Plain text only.** Every non-literal string renders with
  `textFormat: Text.PlainText`, so file contents cannot become rich text.

## State

`list` writes nothing. Explicit apply actions create or remove one symlink per agent. Recoverable
removals use the host's `$XDG_DATA_HOME/fileblade/bin/memory/` directory.
Recoverable removals and view settings belong to the FileBlade host. Removing
this plugin preserves those bins and settings, source-root configuration and
links previously created for agents.

## Validation

```bash
tests/run
LC_ALL=C omarchy plugin validate .
qmllint blades/Module.qml Service.qml
find . -path ./.git -prune -o -type l -print
git diff --check
```

## License

MIT. See `LICENSE`.

## Search syntax

The filter field is Fileblade's shared `PaneSearchField` with the FILES search
syntax: bare words match anywhere (case-insensitive), `"quoted text"` matches
exactly, `-word` excludes, `name:x` matches the row label only, and the
field keys shown in the placeholder (`agent, scope, kind`) take exact comma-separated
values, negatable with a leading `-` (`kind:rules agent:claude-code`). Unknown keys are searched as
plain text.
