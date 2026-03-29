from __future__ import annotations

import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

from py_engine.uielements import UIElement
from py_engine.window import MainWindow

SUPPORTED_TAGS = {
    "mainwin",
    "cwin",
    "mwin",
    "popwin",
    "fullscreen",
    "multiwin",
    "label",
    "button",
    "input",
    "textarea",
    "select",
    "img",
    "video",
    "audio",
    "canvas",
    "table",
    "tabs",
    "progress",
}


class HTMLParser:
    def parse_file(self, path: str | Path) -> MainWindow:
        source = Path(path)
        root = ET.fromstring(source.read_text(encoding="utf-8"))
        if root.tag != "mainwin":
            raise ValueError("The root element of a .htmlpy file must be <mainwin>.")
        return MainWindow(
            element=self._build_element(root, source.parent),
            width=int(root.attrib.get("width", "1100")),
            height=int(root.attrib.get("height", "720")),
            title=root.attrib.get("title", "HTMLPY App"),
            borderless=root.attrib.get("borderless", "false").lower() == "true",
            icon=root.attrib.get("icon"),
            children=[],
        )

    def _build_element(self, node: ET.Element, base_dir: Path) -> UIElement:
        if node.tag not in SUPPORTED_TAGS:
            raise ValueError(f"Unsupported htmlpy tag: <{node.tag}>")
        element = UIElement(tag=node.tag, attrs=dict(node.attrib), text=(node.text or "").strip())
        element.children = self._build_children(node, base_dir)
        return element

    def _build_children(self, node: ET.Element, base_dir: Path) -> list[UIElement]:
        children: list[UIElement] = []
        for child in node:
            if child.tag == "include":
                include_path = child.attrib.get("src")
                if not include_path:
                    raise ValueError("<include> requires a src attribute.")
                include_source = (base_dir / include_path).resolve()
                wrapped = f"<fragment>{include_source.read_text(encoding='utf-8')}</fragment>"
                fragment = ET.fromstring(wrapped)
                children.extend(self._build_children(fragment, include_source.parent))
                continue
            children.append(self._build_element(child, base_dir))
        return children


class PythonLogicLoader:
    def load_module(self, path: str | Path):
        source = Path(path)
        spec = importlib.util.spec_from_file_location(source.stem, source)
        if not spec or not spec.loader:
            raise RuntimeError(f"Unable to load logic module from {source}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
