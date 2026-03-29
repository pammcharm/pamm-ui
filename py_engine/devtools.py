from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import sysconfig
import xml.etree.ElementTree as ET
from pathlib import Path

from py_engine.config import ProjectConfig


RECOMMENDED_EXTENSIONS = [
    "ms-python.python",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
]

RECOMMENDED_PYTHON_TOOLS = ["black", "ruff"]

WORKSPACE_SETTINGS = {
    "files.associations": {
        "*.htmlpy": "html",
        "*.csspy": "css",
    },
    "editor.formatOnSave": True,
    "editor.codeActionsOnSave": {
        "source.organizeImports.ruff": "explicit",
        "source.fixAll.ruff": "explicit",
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": True,
    },
    "[html]": {
        "editor.defaultFormatter": "vscode.html-language-features",
        "editor.formatOnSave": True,
    },
    "[css]": {
        "editor.defaultFormatter": "vscode.css-language-features",
        "editor.formatOnSave": True,
    },
    "black-formatter.importStrategy": "fromEnvironment",
    "ruff.importStrategy": "fromEnvironment",
    "files.exclude": {
        "**/__pycache__": True,
    },
}


def run_doctor(config_path: str | None = None, fix: bool = False) -> int:
    print("PAMM Doctor")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    scripts_dir = Path(sysconfig.get_path("scripts"))
    print(f"Scripts directory: {scripts_dir}")
    path_entries = {Path(entry).resolve() for entry in _path_entries() if Path(entry).exists()}
    print(f"Scripts directory on PATH: {scripts_dir.resolve() in path_entries}")
    if sys.platform.startswith("win"):
        persisted_user_path = _read_windows_user_path_entries()
        print(f"Scripts directory on persisted user PATH: {scripts_dir.resolve() in persisted_user_path}")
        if fix and scripts_dir.resolve() not in persisted_user_path:
            _ensure_windows_user_path(scripts_dir)
            print("Applied PATH fix for the current user.")

    pamm_cmd = shutil.which("pamm")
    print(f"Resolved pamm command: {pamm_cmd or 'not found'}")
    black_available = _module_available("black")
    ruff_available = _module_available("ruff")
    print(f"Black formatter module: {'available' if black_available else 'not installed'}")
    print(f"Ruff module: {'available' if ruff_available else 'not installed'}")
    code_cmd = _find_code_command()
    print(f"VS Code CLI: {code_cmd or 'not found'}")
    if code_cmd:
        installed = set(_list_vscode_extensions(code_cmd))
        missing = [ext for ext in RECOMMENDED_EXTENSIONS if ext not in installed]
        print(f"Missing recommended VS Code extensions: {', '.join(missing) if missing else 'none'}")

    if config_path:
        config_file = Path(config_path).resolve()
        print(f"Config path: {config_file}")
        if not config_file.exists():
            print("Config status: missing")
            return 1

        config = ProjectConfig.from_file(config_file)
        project_root = Path(config.working_directory).resolve() if config.working_directory else config_file.parent
        print(f"Project root: {project_root}")
        print(f"HTML entry: {(project_root / config.html).exists()}")
        print(f"CSS files: {len(config.css)}")
        print(f"Logic files: {len(config.logic)}")
        if config.dll_path:
            print(f"DLL exists: {(project_root / config.dll_path).exists()}")
        print(f"Autoreload: {config.autoreload}")

    return 0


def format_project(target: str | Path = ".") -> int:
    root = Path(target).resolve()
    python_files = list(root.rglob("*.py"))
    htmlpy_files = list(root.rglob("*.htmlpy"))
    csspy_files = list(root.rglob("*.csspy"))

    for file_path in htmlpy_files:
        file_path.write_text(format_htmlpy(file_path.read_text(encoding="utf-8")), encoding="utf-8")

    for file_path in csspy_files:
        file_path.write_text(format_csspy(file_path.read_text(encoding="utf-8")), encoding="utf-8")

    if python_files:
        try:
            subprocess.run([sys.executable, "-m", "black", *[str(path) for path in python_files]], check=True)
            ruff_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "--fix", *[str(path) for path in python_files]],
                check=False,
                capture_output=True,
                text=True,
            )
            if ruff_result.returncode not in (0,):
                print("Ruff reported remaining issues after auto-fix.")
        except Exception:
            for file_path in python_files:
                file_path.write_text(_normalize_text(file_path.read_text(encoding="utf-8")), encoding="utf-8")

    print(f"Formatted {len(python_files)} Python, {len(htmlpy_files)} htmlpy, and {len(csspy_files)} csspy files.")
    return 0


def setup_dev(target: str | Path = ".", install_extensions: bool = True, install_python_tools: bool = False) -> int:
    root = Path(target).resolve()
    vscode_dir = root / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)

    settings_path = vscode_dir / "settings.json"
    existing = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    merged = _deep_merge(existing, WORKSPACE_SETTINGS)
    settings_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    code_cmd = _find_code_command()
    if install_extensions and code_cmd:
        installed = set(_list_vscode_extensions(code_cmd))
        for extension in RECOMMENDED_EXTENSIONS:
            if extension not in installed:
                subprocess.run([code_cmd, "--install-extension", extension], check=False)

    if install_python_tools:
        subprocess.run([sys.executable, "-m", "pip", "install", *RECOMMENDED_PYTHON_TOOLS], check=False)

    print(f"Updated workspace settings at {settings_path}")
    if code_cmd:
        print("VS Code setup checked.")
    else:
        print("VS Code CLI not found. Settings were still written.")
    if install_python_tools:
        print("Python formatter tools install attempted.")
    return 0


def format_htmlpy(source: str) -> str:
    wrapped = f"<fragment>{source}</fragment>"
    root = ET.fromstring(wrapped)
    lines: list[str] = []
    for child in root:
        _append_xml_lines(child, lines, 0)
    return "\n".join(lines).rstrip() + "\n"


def format_csspy(source: str) -> str:
    lines: list[str] = []
    current_indent = 0
    tokens = source.replace("{", "{\n").replace("}", "\n}\n").replace(";", ";\n").splitlines()
    for raw in tokens:
        token = raw.strip()
        if not token:
            continue
        if token == "}":
            current_indent = max(0, current_indent - 1)
        lines.append(("    " * current_indent) + token)
        if token.endswith("{"):
            current_indent += 1
        if token == "}":
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _append_xml_lines(node: ET.Element, lines: list[str], depth: int) -> None:
    indent = "    " * depth
    attrs = " ".join(f'{key}="{value}"' for key, value in node.attrib.items())
    text = (node.text or "").strip()

    if len(node) == 0 and not text:
        if attrs:
            lines.append(f"{indent}<{node.tag} {attrs} />")
        else:
            lines.append(f"{indent}<{node.tag} />")
        return

    open_tag = f"{indent}<{node.tag}"
    if attrs:
        open_tag += f" {attrs}"
    open_tag += ">"

    if len(node) == 0 and text:
        lines.append(f"{open_tag}{text}</{node.tag}>")
        return

    lines.append(open_tag)
    if text:
        lines.append(f"{indent}    {text}")
    for child in node:
        _append_xml_lines(child, lines, depth + 1)
    lines.append(f"{indent}</{node.tag}>")


def _normalize_text(source: str) -> str:
    return "\n".join(line.rstrip() for line in source.splitlines()).rstrip() + "\n"


def _path_entries() -> list[str]:
    separator = ";" if os.name == "nt" else ":"
    return [entry for entry in os.environ.get("PATH", "").split(separator) if entry]


def _read_windows_user_path_entries() -> set[Path]:
    try:
        from winreg import HKEY_CURRENT_USER, KEY_READ, OpenKey, QueryValueEx

        with OpenKey(HKEY_CURRENT_USER, r"Environment", 0, KEY_READ) as key:
            value, _ = QueryValueEx(key, "Path")
        return {Path(entry).resolve() for entry in value.split(";") if entry and Path(entry).exists()}
    except Exception:
        return set()


def _ensure_windows_user_path(scripts_dir: Path) -> None:
    from winreg import HKEY_CURRENT_USER, KEY_READ, KEY_SET_VALUE, OpenKey, QueryValueEx, REG_EXPAND_SZ, SetValueEx

    with OpenKey(HKEY_CURRENT_USER, r"Environment", 0, KEY_READ | KEY_SET_VALUE) as key:
        try:
            value, _ = QueryValueEx(key, "Path")
        except FileNotFoundError:
            value = ""
        parts = [part for part in value.split(";") if part]
        if str(scripts_dir) not in parts:
            updated = value.rstrip(";")
            if updated:
                updated += ";"
            updated += str(scripts_dir)
            SetValueEx(key, "Path", 0, REG_EXPAND_SZ, updated)


def _module_available(name: str) -> bool:
    try:
        subprocess.run([sys.executable, "-m", name, "--version"], check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False


def _find_code_command() -> str | None:
    for candidate in ("code", "code.cmd", "code.exe"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _list_vscode_extensions(code_cmd: str) -> list[str]:
    try:
        result = subprocess.run([code_cmd, "--list-extensions"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _deep_merge(base: dict, updates: dict) -> dict:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
