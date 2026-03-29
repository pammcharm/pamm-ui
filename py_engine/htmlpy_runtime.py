from __future__ import annotations

from py_engine.application import Application


def run_htmlpy(html_path: str, css_paths: list[str], logic_path: str | None = None) -> None:
    app = Application()
    app.load_html(html_path)
    for css_path in css_paths:
        app.load_css(css_path)
    if logic_path:
        app.load_logic(logic_path)
    app.run()
