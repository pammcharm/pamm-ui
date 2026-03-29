from __future__ import annotations

import argparse

from py_engine.application import Application


def run_from_config(config_path: str = "app.json", dev: bool | None = None) -> None:
    app = Application()
    config = app.load_project(config_path)
    if dev is not None:
        config.dev_mode = dev
        if dev:
            config.autoreload = True
            app._setup_watch_files(config)
    app.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an HTMLPY/CSSPY app project.")
    parser.add_argument("config", nargs="?", default="app.json", help="Path to the app config file.")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with autoreload.")
    args = parser.parse_args()
    run_from_config(args.config, dev=args.dev)


if __name__ == "__main__":
    main()
