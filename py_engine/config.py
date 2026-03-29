from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectConfig:
    app_name: str
    html: str
    css: list[str]
    logic: list[str]
    dll_path: str | None = None
    working_directory: str | None = None
    frontend_dir: str | None = None
    backend_dir: str | None = None
    dev_mode: bool = False
    autoreload: bool = False
    watch: list[str] | None = None

    @classmethod
    def from_file(cls, path: str | Path) -> "ProjectConfig":
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        css = data.get("css", [])
        logic = data.get("logic", [])
        if isinstance(css, str):
            css = [css]
        if isinstance(logic, str):
            logic = [logic]
        return cls(
            app_name=data.get("app_name", source.stem),
            html=data["html"],
            css=css,
            logic=logic,
            dll_path=data.get("dll_path"),
            working_directory=data.get("working_directory"),
            frontend_dir=data.get("frontend_dir"),
            backend_dir=data.get("backend_dir"),
            dev_mode=bool(data.get("dev_mode", False)),
            autoreload=bool(data.get("autoreload", False)),
            watch=data.get("watch", []),
        )
