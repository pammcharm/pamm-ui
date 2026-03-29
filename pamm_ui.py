from __future__ import annotations

from py_engine import Application, ProjectConfig, create_project, run_from_config
from py_engine.cli import main

__all__ = [
    "Application",
    "ProjectConfig",
    "create_project",
    "main",
    "run_from_config",
]


if __name__ == "__main__":
    main()
