from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOCKET = "data-goblin.fileblade/blade"
HOST_ID = "data-goblin.fileblade"
BUILTIN_OPEN = re.compile(r"(?<![.\w])open\(")

def manifest_contract() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1
    assert manifest["id"] == "data-goblin.fileblade-memory"
    for key in ("name", "version", "author", "description", "license", "kinds", "entryPoints"):
        assert isinstance(manifest[key], (str, list, dict)) and manifest[key], key
    assert manifest["kinds"] == ["service"]
    assert (ROOT / manifest["entryPoints"]["service"]).is_file()
    modules = manifest["extensions"][SOCKET]
    assert isinstance(modules, list) and modules
    for module in modules:
        assert module["hostContract"] == 2
        assert (ROOT / module["entry"]).is_file()
        assert module["singleton"] is True

def qml_contract() -> None:
    module = (ROOT / "blades" / "Module.qml").read_text(encoding="utf-8")
    lines = module.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("Text {"):
            continue
        window = lines[index + 1:index + 14]
        assert any("textFormat: Text.PlainText" in entry for entry in window), f"Text at line {index + 1} lacks PlainText"
    assert 'context.ui.url("PaneHeader")' in module
    assert "inventory ? inventory.anchorPath" in module
    assert "inventory ? inventory.projectArguments" in module
    assert 'context.ui.url("ArtifactTree")' in module
    for option in ("caseSensitive", "regex"):
        assert f'item.{option} = module.{option}' in module
        assert f'item.{option} = Qt.binding(function() {{ return module.{option} }})' in module
    assert "item.optionsToggled.connect" in module
    assert "item.showOptions = true" in module
    assert "item.fileActionsFor = function(entry)" in module
    assert 'context.ui.url("PaneView")' in module
    assert "readonly property var metricOptions:" in module
    assert "readonly property var view: viewLoader.item" in module
    assert 'context.metrics.options(["off", "agents", "updated", "created", "tokens", "characters", "words", "bytes", "summary"])' in module
    assert 'label: "Tokens' not in module
    assert 'item.defaultMetric = "tokens"' in module
    assert 'item.defaultSorts = [{ key: "tokens", desc: true }]' in module
    assert "item.options = module.metricOptions" in module
    assert "item.view = Qt.binding(function() { return module.view })" in module
    assert "item.installedAgents = Qt.binding(function() { return module.files ? module.files.installedAgents : [] })" in module
    assert "item.appliedAgents = function(entry) { return module.appliedAgents(entry) }" in module
    assert "function appliedAgents(entry)" in module
    assert "item.agentToggled.connect(function(entry, agentId, on) { module.applyAgents(entry, [agentId], on) })" in module
    assert "item.agentsAllRequested.connect(function(entry, on) { module.applyAll(entry, on) })" in module
    assert 'context.ui.url("ArtifactBin")' in module and 'item.module = "memory"' in module
    assert 'setSource(module.context.ui.url("ArtifactBin"), { service: module.files })' in module
    assert 'item.module = "memory"\n      item.context = Qt.binding(function() { return module.context })' in module
    assert "item.rowAction = function(entry) { return bin.item ? bin.item.rowAction(entry) : null }" in module
    assert "item.actionRequested.connect(function(entry) { if (bin.item) bin.item.ask(entry) })" in module
    assert "function binItem(entry)" in module and "entry.inlineBytes !== null && entry.inlineBytes !== undefined) return null" in module
    assert "realpath: String(entry.realpath || \"\")" in module
    assert "bin.item.mergeRows(items, binned, function(entry) { return module.groupPath(entry) })" in module
    assert "position: Math.max(0, allRows().indexOf(entry))" in module
    assert "groups: groupPath(entry)" in module
    assert 'return kind === "Instructions" ? [scope] : [scope, kind]' in module
    assert "item.groupGlyph = function(path) { return module.groupGlyph(path) }" in module
    assert "metrics: entry.metrics" in module
    assert "ActionDialog {" not in module and not (ROOT / "blades" / "ActionDialog.qml").exists()
    assert "item.filterRequested.connect(function() { module.openFilter() })" in module
    assert "header.item.openFilter()" in module
    assert '"--project", anchorPath, "--id", String(entry.id || "")' in module
    assert '"--state", on ? "on" : "off", "--json"' in module
    assert 'command.push("--agent", String(agents[i]))' in module
    assert "readonly property string status: {" in module
    assert 'return "Applying…"' in module and "if (applyError !== \"\") return applyError" in module
    assert 'if (busy) return "Scanning…"' in module and 'items.length + " files (capped)"' in module
    assert "item.status = Qt.binding(function() { return module.status })" in module
    assert module.count("item.status = ") == 1
    assert "applyAgents(entry, installedAgents(), on)" in module
    assert "function applyAll(entry, on)" in module
    assert 'inventory.mutate("apply", command)' in module
    assert "Process {" not in module and "StdioCollector" not in module
    for retired in ("metricKey", "setMetric", "restoreMetric", "validMetric", "metricChosen",
                    "specialMetricValue", "readerBadge", "leafBadge"):
        assert retired not in module, retired
    assert "DESC" not in module and "showDescriptions" not in module and "showDetails" not in module
    assert "item.groupBadge = function(path)" in module
    assert "module.projectRoot || module.anchorPath" not in module
    assert 'context.ui.url("PaneSearchField")' in module
    assert "property var context: null" in module
    assert "Component.onDestruction: if (attachedProvider) attachedProvider.detach(attachedContext)" in module
    assert "onActiveChanged: syncProvider()" in module
    assert 'KeyPlan.action(event.key, event.modifiers) !== "rescan"' in module
    assert "context.collapsed !== true" in module
    assert "item.tabIndex = Qt.binding(function() { return module.context.tabIndex })" in module
    assert "active: module.active" in module
    plan = (ROOT / "blades" / "KeyPlan.js").read_text(encoding="utf-8")
    assert "function action(" in plan
    for host_key in ("Qt.Key_Tab", "Qt.Key_Backtab", "Qt.Key_PageDown", "Qt.Key_Home"):
        assert host_key not in plan
    assert '"rescan"' in plan
    assert "readonly property var inventory: provider ? provider.inventory : null" in module
    assert "property bool truncated" in module and "files (capped)" in module
    service = (ROOT / "Service.qml").read_text(encoding="utf-8")
    assert "property var shell: null" in service and "required property" not in service
    assert 'context.ui.url("ArtifactInventory")' in service
    assert "observers: Qt.binding(function() { return service.observers })" in service
    helper = json.loads((ROOT / "manifest.json").read_text())["extensions"]["data-goblin.fileblade/helper"][0]
    assert helper == {"id": "inventory", "entry": "bin/agent-memoryctl", "read": ["list"], "write": ["apply"], "timeoutMs": 8000}

def audit_gap_contract() -> None:
    adapters = (ROOT / "agent_memory" / "adapters.py").read_text(encoding="utf-8")
    for name in ("codex_fallback_names", "claude_settings", "auto_memory_roots",
                 "opencode_instructions", "copilot_extra_dirs"):
        assert f"def {name}(" in adapters, name
    assert "COPILOT_CUSTOM_INSTRUCTIONS_DIRS" in adapters
    assert "claudeMdExcludes" in adapters and "autoMemoryDirectory" in adapters
    assert "project_doc_fallback_filenames" in adapters
    assert "is_remote(entry)" in adapters
    common = (ROOT / "agent_memory" / "common.py").read_text(encoding="utf-8")
    for guard in ("MAX_CONFIG_BYTES", "MAX_GLOB_MATCHES", "MAX_FALLBACK_NAMES",
                  "MAX_INSTRUCTION_ENTRIES", "MAX_ENV_DIRS"):
        assert guard in common, guard
    assert "def bounded_glob(" in common and "def safe_basename(" in common
    module = (ROOT / "blades" / "Module.qml").read_text(encoding="utf-8")
    assert "entry.excluded === true" in module and "entry.inlineBytes" in module
    assert "partly-excluded" in module
    discovery = (ROOT / "agent_memory" / "discovery.py").read_text(encoding="utf-8")
    assert '"inlineBytes"' in discovery and '"excluded"' in discovery
    assert "partly-excluded" in discovery

def helper_contract() -> None:
    helper = ROOT / "bin" / "agent-memoryctl"
    assert helper.is_file() and helper.stat().st_mode & 0o111
    sources = list((ROOT / "agent_memory").glob("*.py"))
    assert sources
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for forbidden in ("subprocess", "os.system", "shutil.rmtree", "urllib", "socket", "eval(", "exec(",
                          "os.remove", "os.rmdir", "os.rename", "os.replace", "os.truncate"):
            assert forbidden not in text, f"{source.name} references {forbidden}"
        assert not BUILTIN_OPEN.search(text), f"{source.name} uses builtin open()"
        assert ".write_text(" not in text and ".write_bytes(" not in text
        if source.name != "apply.py":
            assert "os.unlink" not in text and "os.symlink" not in text and "os.makedirs" not in text, source.name
        assert "os.rmdir" not in text and "os.write" not in text, source.name
    applying = (ROOT / "agent_memory" / "apply.py").read_text(encoding="utf-8")
    assert "native_link(target, source)" in applying and "native_unlink(target, source, current)" in applying
    assert "os.symlink(" not in applying and "os.unlink(" not in applying
    assert "stat.S_ISLNK(current.st_mode)" in applying
    assert "if not same_place(target, source):" in applying
    assert "a real file is never deleted" in applying
    assert 'LINKABLE_KIND = "instructions"' in applying
    assert "def contained(" in applying and "safe_basename(target.name) != target.name" in applying
    for name in ("COPILOT_HOME", "XDG_CONFIG_HOME", "CODEX_HOME"):
        assert name in applying, name
    discovery_text = (ROOT / "agent_memory" / "discovery.py").read_text(encoding="utf-8")
    assert "def build_context(" in discovery_text and "def collect_in(" in discovery_text
    assert "apply" not in discovery_text
    cli = (ROOT / "agent_memory" / "cli.py").read_text(encoding="utf-8")
    assert "MAX_OUTPUT_BYTES = 1024 * 1024" in cli and "def encoded(" in cli
    assert 'commands.add_parser("apply"' in cli
    assert 'linking.add_argument("--id", required=True)' in cli
    assert 'linking.add_argument("--agent", action="append", required=True)' in cli
    assert 'linking.add_argument("--state", choices=list(apply.STATES), required=True)' in cli
    assert 'commands.add_parser("delete"' not in cli and not (ROOT / "agent_memory" / "bin.py").exists()

def readme_contract() -> None:
    readme = (ROOT / "docs" / "agent-written" / "README.md").read_text(encoding="utf-8")
    assert "Omarchy Fileblade" in readme
    assert HOST_ID in readme
    assert "install order" in readme.lower()
    assert (ROOT / "LICENSE").is_file()
    flat = " ".join(readme.split())
    assert "agent-memoryctl apply --project <dir> --id <row id> --agent <agent id> [--agent <id> ...] --state on|off --json" in flat
    assert "fileblade _backend bin-put --module memory" in flat and "fileblade/bin/memory" in flat
    for phrase in ("Left click", "Right click", "since", "until", "min", "max", "Applying", "one symlink per agent",
                   ".agents/rules/", "~/.copilot/copilot-instructions.md", "~/.pi/agent/AGENTS.md",
                   "~/.config/opencode/AGENTS.md", "~/.codex/AGENTS.md", "never deletes a real file"):
        assert phrase in flat, phrase
    assert "No writes" not in readme

def main() -> None:
    manifest_contract()
    audit_gap_contract()
    qml_contract()
    helper_contract()
    readme_contract()
    print("contract tests: ok (6 groups)")

if __name__ == "__main__":
    main()
