from __future__ import annotations

from dataclasses import dataclass, field

from py_engine.uielements import UIElement


@dataclass
class MainWindow:
    element: UIElement
    width: int
    height: int
    title: str
    borderless: bool = False
    icon: str | None = None
    children: list[UIElement] = field(default_factory=list)


@dataclass
class ChildWindow:
    element: UIElement


@dataclass
class ModalWindow:
    element: UIElement


@dataclass
class PopupWindow:
    element: UIElement


@dataclass
class FullscreenWindow:
    element: UIElement


@dataclass
class MultiWindowManager:
    windows: list[MainWindow] = field(default_factory=list)

    def add(self, window: MainWindow) -> None:
        self.windows.append(window)
