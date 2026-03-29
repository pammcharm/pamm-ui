from __future__ import annotations

import re
from dataclasses import dataclass, field

NAMED_COLORS = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "red": (220, 68, 68, 255),
    "green": (70, 170, 90, 255),
    "blue": (76, 120, 220, 255),
    "gray": (140, 146, 160, 255),
    "transparent": (0, 0, 0, 0),
}


def parse_size(value: str | None, fallback: int) -> int:
    if not value:
        return fallback
    cleaned = value.strip().lower().replace("px", "")
    try:
        return int(float(cleaned))
    except ValueError:
        return fallback


def parse_float(value: str | None, fallback: float) -> float:
    if not value:
        return fallback
    try:
        return float(value.strip())
    except ValueError:
        return fallback


def parse_color(value: str | None, fallback: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if not value:
        return fallback
    value = value.strip().lower()
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]
    if value.startswith("#"):
        hex_value = value[1:]
        if len(hex_value) == 6:
            return (
                int(hex_value[0:2], 16),
                int(hex_value[2:4], 16),
                int(hex_value[4:6], 16),
                255,
            )
        if len(hex_value) == 8:
            return (
                int(hex_value[0:2], 16),
                int(hex_value[2:4], 16),
                int(hex_value[4:6], 16),
                int(hex_value[6:8], 16),
            )
    match = re.match(r"rgba?\(([^)]+)\)", value)
    if match:
        parts = [part.strip() for part in match.group(1).split(",")]
        if len(parts) >= 3:
            alpha = 255
            if len(parts) == 4:
                alpha = int(float(parts[3]) * 255) if "." in parts[3] else int(parts[3])
            return int(parts[0]), int(parts[1]), int(parts[2]), alpha
    return fallback


@dataclass
class StyleManager:
    rules: dict[str, dict[str, str]] = field(default_factory=dict)

    def load(self, css_text: str) -> None:
        self.rules.clear()
        for selector, body in re.findall(r"([^{]+)\{([^}]+)\}", css_text, flags=re.MULTILINE):
            selector = selector.strip()
            declarations: dict[str, str] = {}
            for line in body.split(";"):
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                declarations[key.strip().lower()] = value.strip()
            if selector:
                self.rules[selector] = declarations

    def compute_style(self, tag: str, attrs: dict[str, str], state: set[str] | None = None) -> dict[str, str]:
        computed: dict[str, str] = {}
        state = state or set()
        self._apply_selector(computed, tag)

        class_name = attrs.get("class")
        if class_name:
            self._apply_selector(computed, f".{class_name}")

        element_id = attrs.get("id")
        if element_id:
            self._apply_selector(computed, f"#{element_id}")

        for pseudo in ("hover", "active", "focus"):
            if pseudo in state:
                self._apply_selector(computed, f"{tag}:{pseudo}")
                if class_name:
                    self._apply_selector(computed, f".{class_name}:{pseudo}")
                if element_id:
                    self._apply_selector(computed, f"#{element_id}:{pseudo}")

        inline = attrs.get("style", "")
        for part in inline.split(";"):
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            computed[key.strip().lower()] = value.strip()

        return computed

    def _apply_selector(self, computed: dict[str, str], selector: str) -> None:
        if selector in self.rules:
            computed.update(self.rules[selector])
