from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputEvent:
    mouse_x: int
    mouse_y: int
    mouse_clicked: bool = False
    mouse_down: bool = False


class EventManager:
    def dispatch(self, app: "Application", event: InputEvent) -> None:
        hovered = None
        for element in app.iter_elements():
            if element.hit_test(event.mouse_x, event.mouse_y):
                hovered = element
        app.hovered_element = hovered

        if hovered and event.mouse_clicked and hovered.on_click:
            app.call_handler(hovered.on_click, hovered)
