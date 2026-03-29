from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from py_engine.devtools import format_project, run_doctor, setup_dev
from py_engine.runner import run_from_config


APP_JSON_TEMPLATE = {
    "app_name": None,
    "html": "frontend/pages/app.htmlpy",
    "css": [
        "frontend/styles/base.csspy",
        "frontend/styles/theme.csspy",
        "frontend/styles/app.csspy",
    ],
    "logic": [
        "main.py",
        "frontend/app_logic.py",
        "backend/main.py",
        "backend/services.py",
    ],
    "dll_path": None,
    "frontend_dir": "frontend",
    "backend_dir": "backend",
    "dev_mode": True,
    "autoreload": True,
    "watch": [
        "frontend",
        "backend",
        "main.py",
    ],
}

MAIN_HTML_TEMPLATE = """<mainwin title="{title}" width="1280" height="820" borderless="false" icon="frontend/assets/app_icon.bmp" background="#0f1522">
    <include src="../layouts/shell.htmlpy" />
</mainwin>
"""

SHELL_HTML_TEMPLATE = """<cwin id="hero" class="hero" x="32" y="28" width="1216" height="144">
    <label text="{title}" x="24" y="22" />
    <label text="PAMM project with frontend, backend, components, layouts, pages, assets, public, and db." x="24" y="66" />
</cwin>

<cwin id="content" class="panel" x="32" y="194" width="1216" height="596">
    <include src="../components/sidebar.htmlpy" />
    <include src="../pages/home.htmlpy" />
</cwin>
"""

SIDEBAR_HTML_TEMPLATE = """<cwin id="sidebar" class="sidebar" x="20" y="20" width="280" height="556">
    <label text="Navigation" x="20" y="18" />
    <button id="nav_home" class="nav_button" text="Home" x="20" y="76" width="220" height="52" on_click="show_home" />
    <button id="nav_gallery" class="nav_button" text="Gallery" x="20" y="142" width="220" height="52" on_click="show_gallery" />
    <button id="nav_about" class="nav_button" text="About" x="20" y="208" width="220" height="52" on_click="show_about" />
</cwin>
"""

HOME_HTML_TEMPLATE = """<cwin id="page_home" class="page_card" x="332" y="20" width="864" height="556">
    <label text="Starter Dashboard" x="24" y="20" />
    <label id="status_text" text="Edit htmlpy, csspy, or Python files and save to see dev autoreload." x="24" y="62" />
    <button id="primary_action" class="primary" text="Run Demo Action" x="24" y="128" width="220" height="58" on_click="run_demo_action" />
    <progress id="startup_progress" x="24" y="216" width="460" height="34" value="72" max="100" />
    <img id="hero_image" x="520" y="34" width="300" height="180" src="frontend/assets/showcase.bmp" />
    <cwin id="media_card" class="media_card" x="24" y="288" width="796" height="224">
        <label text="Media and animation ready" x="20" y="18" />
        <label text="Place videos in frontend/public and connect them in your htmlpy." x="20" y="62" />
        <label text="Backend services live in backend/ and can feed frontend/app_logic.py." x="20" y="100" />
    </cwin>
</cwin>
"""

BASE_CSS_TEMPLATE = """mainwin {
    background: #0f1522;
}

label {
    color: #f5f7fb;
    font-size: 24px;
}

button {
    color: #edf3ff;
    border-radius: 18px;
}
"""

THEME_CSS_TEMPLATE = """.hero {
    gradient-start: #203150;
    gradient-end: #13243d;
}

.panel {
    background: #131d2f;
    border-radius: 28px;
    border-width: 1px;
    border-color: rgba(255, 255, 255, 0.10);
}

.sidebar {
    background: #172338;
    border-radius: 22px;
}

.page_card {
    background: #1a2438;
    border-radius: 24px;
}

.media_card {
    background: #121c2d;
    border-radius: 20px;
}
"""

APP_CSS_TEMPLATE = """.nav_button {
    background: #344766;
}

.nav_button:hover {
    background: #476089;
}

.primary {
    gradient-start: #ff9460;
    gradient-end: #ffd166;
    color: #1d2430;
}

#status_text {
    color: #c8d6ef;
}
"""

ROOT_MAIN_PY_TEMPLATE = """from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_import_path() -> None:
    try:
        import py_engine  # noqa: F401

        return
    except ModuleNotFoundError:
        pass

    current = Path(__file__).resolve().parent
    for candidate in [current, *current.parents]:
        if (candidate / "py_engine").exists():
            path_str = str(candidate)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
            break


_bootstrap_import_path()

from py_engine import run_from_config  # noqa: E402


if __name__ == "__main__":
    config_path = Path(__file__).resolve().parent / "app.json"
    run_from_config(str(config_path), dev=True)
"""

FRONTEND_LOGIC_TEMPLATE = """from backend.services import get_app_message


def _find(app, element_id: str):
    for element in app.iter_elements():
        if element.element_id == element_id:
            return element
    return None


def _set_status(app, text: str) -> None:
    status = _find(app, "status_text")
    if status:
        status.attrs["text"] = text


def run_demo_action(app, element) -> None:
    _set_status(app, f"Frontend event fired. Backend says: {get_app_message()}")


def show_home(app, element) -> None:
    _set_status(app, "Home page selected.")


def show_gallery(app, element) -> None:
    _set_status(app, "Gallery page selected. Add more htmlpy includes under frontend/pages.")


def show_about(app, element) -> None:
    _set_status(app, "About page selected. Extend frontend/app_logic.py or backend/services.py.")
"""

BACKEND_MAIN_TEMPLATE = """from backend.services import get_app_message


def bootstrap() -> str:
    return get_app_message()
"""

BACKEND_SERVICES_TEMPLATE = """def get_app_message() -> str:
    return "backend ready"
"""

BACKEND_DB_TEMPLATE = """DATABASE = {
    "engine": "sqlite",
    "name": "app.db"
}
"""

README_TEMPLATE = """# {title}

## Quick Start
```powershell
pamm run app.json --dev
```

## Run Without Global Install
- `python main.py`

## Development
- Edit files under `frontend/` or `backend/`
- Dev autoreload is enabled by default in `app.json`
- Run `pamm dev app.json` for development mode
- Run `pamm format .` to format Python, htmlpy, and csspy files
- Run `pamm setup-dev . --install-python-tools` to prepare VS Code and install formatter tools

## Config
- App entry file: `frontend/pages/app.htmlpy`
- CSS files are listed in `app.json`
- Python logic files are listed in `app.json`
- Watch paths for autoreload are listed in `app.json`

## Structure
- `frontend/pages/`: page htmlpy files
- `frontend/components/`: reusable htmlpy pieces
- `frontend/layouts/`: app shells and shared layout blocks
- `frontend/styles/`: csspy files
- `frontend/assets/`: images and icons
- `frontend/public/`: user-facing static files
- `frontend/db/`: frontend-side local data/mock files
- `backend/`: Python backend logic and services

## Python API
```python
from pamm import run_from_config

run_from_config("app.json", dev=True)
```
"""


def create_project(project_name: str, target_dir: str | None = None, autoreload: bool | None = None) -> Path:
    root = _resolve_project_root(project_name, target_dir)
    title = project_name.replace("-", " ").replace("_", " ").title()
    use_autoreload = True if autoreload is None else autoreload

    folders = [
        root / "frontend" / "pages",
        root / "frontend" / "components",
        root / "frontend" / "layouts",
        root / "frontend" / "styles",
        root / "frontend" / "assets",
        root / "frontend" / "public",
        root / "frontend" / "db",
        root / "backend",
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    config = dict(APP_JSON_TEMPLATE)
    config["app_name"] = project_name
    config["autoreload"] = use_autoreload

    (root / "app.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (root / "main.py").write_text(ROOT_MAIN_PY_TEMPLATE, encoding="utf-8")
    (root / "README.md").write_text(README_TEMPLATE.format(title=title), encoding="utf-8")
    (root / "frontend" / "pages" / "app.htmlpy").write_text(MAIN_HTML_TEMPLATE.format(title=title), encoding="utf-8")
    (root / "frontend" / "layouts" / "shell.htmlpy").write_text(SHELL_HTML_TEMPLATE.format(title=title), encoding="utf-8")
    (root / "frontend" / "components" / "sidebar.htmlpy").write_text(SIDEBAR_HTML_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "pages" / "home.htmlpy").write_text(HOME_HTML_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "styles" / "base.csspy").write_text(BASE_CSS_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "styles" / "theme.csspy").write_text(THEME_CSS_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "styles" / "app.csspy").write_text(APP_CSS_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "app_logic.py").write_text(FRONTEND_LOGIC_TEMPLATE, encoding="utf-8")
    (root / "backend" / "main.py").write_text(BACKEND_MAIN_TEMPLATE, encoding="utf-8")
    (root / "backend" / "services.py").write_text(BACKEND_SERVICES_TEMPLATE, encoding="utf-8")
    (root / "frontend" / "db" / "config.py").write_text(BACKEND_DB_TEMPLATE, encoding="utf-8")
    _write_placeholder_bmp(root / "frontend" / "assets" / "app_icon.bmp", left=(210, 95, 55), right=(88, 214, 200))
    _write_placeholder_bmp(root / "frontend" / "assets" / "showcase.bmp", left=(74, 111, 255), right=(255, 209, 102))

    vscode_dir = root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    (vscode_dir / "settings.json").write_text(
        json.dumps(
            {
                "files.associations": {"*.htmlpy": "html", "*.csspy": "css"},
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports.ruff": "explicit",
                    "source.fixAll.ruff": "explicit",
                },
                "[html]": {"editor.defaultFormatter": "vscode.html-language-features"},
                "[css]": {"editor.defaultFormatter": "vscode.css-language-features"},
                "[python]": {
                    "editor.defaultFormatter": "ms-python.black-formatter",
                    "editor.formatOnSave": True,
                },
                "black-formatter.importStrategy": "fromEnvironment",
                "ruff.importStrategy": "fromEnvironment",
                "files.exclude": {"**/__pycache__": True},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (vscode_dir / "launch.json").write_text(
        json.dumps(
            {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Run PAMM App",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/main.py",
                        "console": "integratedTerminal",
                        "justMyCode": True,
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _resolve_project_root(project_name: str, target_dir: str | None) -> Path:
    if target_dir:
        root = Path(target_dir).resolve()
        if root.exists() and not root.is_dir():
            raise ValueError(f"Target path exists as a file: {root}")
        return root

    base = (Path.cwd() / project_name).resolve()
    if not base.exists():
        return base
    if base.is_dir():
        return _next_available_directory(base)
    return _next_available_directory(base.with_name(f"{project_name}_project"))


def _next_available_directory(base: Path) -> Path:
    candidate = base
    index = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}_{index}")
        index += 1
    return candidate


def _prompt_autoreload() -> bool:
    answer = input("Enable development autoreload? [Y/n]: ").strip().lower()
    return answer not in {"n", "no"}


def _write_placeholder_bmp(path: Path, left: tuple[int, int, int], right: tuple[int, int, int]) -> None:
    width = 96
    height = 64
    row_size = ((24 * width + 31) // 32) * 4
    pixel_array_size = row_size * height
    file_size = 54 + pixel_array_size

    header = bytearray()
    header.extend(b"BM")
    header.extend(struct.pack("<I", file_size))
    header.extend(b"\x00\x00\x00\x00")
    header.extend(struct.pack("<I", 54))
    header.extend(struct.pack("<I", 40))
    header.extend(struct.pack("<i", width))
    header.extend(struct.pack("<i", height))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 24))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", pixel_array_size))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", 0))

    pixels = bytearray()
    for _y in range(height):
        row = bytearray()
        for x in range(width):
            color = left if x < width // 2 else right
            row.extend((color[2], color[1], color[0]))
        while len(row) < row_size:
            row.append(0)
        pixels.extend(row)

    path.write_bytes(bytes(header + pixels))


def main() -> None:
    parser = argparse.ArgumentParser(description="PAMM developer CLI")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new PAMM project.")
    create_parser.add_argument("name", help="Project name.")
    create_parser.add_argument("--dir", dest="target_dir", help="Optional project path.")
    create_parser.add_argument("--autoreload", choices=["yes", "no"], help="Force dev autoreload on or off.")

    run_parser = subparsers.add_parser("run", help="Run an app from a config file.")
    run_parser.add_argument("config", nargs="?", default="app.json", help="Path to the app config.")
    run_parser.add_argument("--dev", action="store_true", help="Run in development mode with autoreload.")

    dev_parser = subparsers.add_parser("dev", help="Run an app in development mode with autoreload.")
    dev_parser.add_argument("config", nargs="?", default="app.json", help="Path to the app config.")

    doctor_parser = subparsers.add_parser("doctor", help="Inspect PAMM installation and project health.")
    doctor_parser.add_argument("config", nargs="?", default=None, help="Optional app config path.")
    doctor_parser.add_argument("--fix", action="store_true", help="Try to apply safe local fixes.")

    format_parser = subparsers.add_parser("format", help="Format Python, htmlpy, and csspy files.")
    format_parser.add_argument("target", nargs="?", default=".", help="Project directory or file root.")

    setup_parser = subparsers.add_parser(
        "setup-dev", help="Write workspace settings and install recommended dev tools."
    )
    setup_parser.add_argument("target", nargs="?", default=".", help="Project directory.")
    setup_parser.add_argument("--no-extensions", action="store_true", help="Skip VS Code extension installation.")
    setup_parser.add_argument(
        "--install-python-tools",
        action="store_true",
        help="Install black and ruff into the active Python environment.",
    )

    parser.add_argument("config", nargs="?", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.command == "create":
        autoreload = _prompt_autoreload() if args.autoreload is None else args.autoreload == "yes"
        try:
            project_path = create_project(args.name, args.target_dir, autoreload=autoreload)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Created project at {project_path}")
        return

    if args.command == "run":
        run_from_config(args.config, dev=args.dev)
        return

    if args.command == "dev":
        run_from_config(args.config, dev=True)
        return

    if args.command == "doctor":
        raise SystemExit(run_doctor(args.config, fix=args.fix))

    if args.command == "format":
        raise SystemExit(format_project(args.target))

    if args.command == "setup-dev":
        raise SystemExit(
            setup_dev(
                args.target,
                install_extensions=not args.no_extensions,
                install_python_tools=args.install_python_tools,
            )
        )

    if args.config:
        run_from_config(args.config)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
