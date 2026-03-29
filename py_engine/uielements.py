from __future__ import annotations

from dataclasses import dataclass, field

from py_engine.style import parse_color, parse_float, parse_size

WINDOW_TAGS = {"mainwin", "cwin", "mwin", "popwin", "fullscreen"}
TEXT_TAGS = {"label", "button", "input", "textarea", "progress"}


@dataclass
class UIElement:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    children: list["UIElement"] = field(default_factory=list)
    style: dict[str, str] = field(default_factory=dict)
    state: set[str] = field(default_factory=set)
    x: int = 0
    y: int = 0
    width: int = 160
    height: int = 48
    abs_x: int = 0
    abs_y: int = 0
    visible: bool = True

    @property
    def element_id(self) -> str:
        return self.attrs.get("id", "")

    @property
    def on_click(self) -> str | None:
        return self.attrs.get("on_click")

    @property
    def is_clickable(self) -> bool:
        return self.tag in {"button", "cwin", "mwin", "popwin", "img"} and self.visible

    def apply_style(self, style: dict[str, str], parent_width: int, parent_height: int) -> None:
        self.style = style
        self.x = parse_size(style.get("x", self.attrs.get("x")), self.x)
        self.y = parse_size(style.get("y", self.attrs.get("y")), self.y)
        self.width = self._resolve_dimension(style.get("width", self.attrs.get("width")), self.width, parent_width)
        self.height = self._resolve_dimension(style.get("height", self.attrs.get("height")), self.height, parent_height)
        self.visible = style.get("display", "block").lower() != "none"

    def update_absolute_position(self, parent_x: int, parent_y: int) -> None:
        self.abs_x = parent_x + self.x
        self.abs_y = parent_y + self.y

    def hit_test(self, mouse_x: int, mouse_y: int) -> bool:
        return (
            self.visible
            and self.abs_x <= mouse_x <= self.abs_x + self.width
            and self.abs_y <= mouse_y <= self.abs_y + self.height
        )

    def render(self, app: "Application", parent_font_id: int) -> None:
        if not self.visible:
            return

        engine = app.engine
        window_id = app.window_id

        background = parse_color(self.style.get("background"), (0, 0, 0, 0))
        color = parse_color(self.style.get("color"), (255, 255, 255, 255))
        radius = parse_size(self.style.get("radius", self.style.get("border-radius")), 18)
        border = parse_size(self.style.get("border-width"), 0)
        border_color = parse_color(self.style.get("border-color"), color)
        opacity = parse_float(self.style.get("opacity"), 1.0)
        alpha = max(0, min(255, int(opacity * 255)))
        background = (background[0], background[1], background[2], min(background[3], alpha))
        color = (color[0], color[1], color[2], min(color[3], alpha))

        if self.tag in WINDOW_TAGS or self.tag in {
            "button",
            "input",
            "textarea",
            "select",
            "tabs",
            "table",
            "canvas",
            "progress",
        }:
            if "gradient-start" in self.style and "gradient-end" in self.style:
                engine.draw_gradient_rect(
                    window_id,
                    self.abs_x,
                    self.abs_y,
                    self.width,
                    self.height,
                    parse_color(self.style.get("gradient-start"), background),
                    parse_color(self.style.get("gradient-end"), background),
                    self.style.get("gradient-direction", "vertical").lower() != "horizontal",
                )
            else:
                engine.draw_rounded_rect(window_id, self.abs_x, self.abs_y, self.width, self.height, radius, background)

            if border > 0:
                engine.draw_rounded_rect(
                    window_id, self.abs_x, self.abs_y, self.width, self.height, radius, border_color, filled=False
                )

        font_size = parse_size(self.style.get("font-size"), 24)
        font_id = app.get_font(font_size)

        if self.tag in TEXT_TAGS or self.text:
            text = self.attrs.get("text", self.text).strip()
            if text:
                engine.draw_text(window_id, text, self.abs_x + 16, self.abs_y + 14, font_id or parent_font_id, color)

        if self.tag == "img":
            source = self.attrs.get("src")
            if source:
                image_id = app.media.load_image(source)
                if image_id >= 0:
                    engine.lib.render_draw_image(
                        window_id, image_id, self.abs_x, self.abs_y, self.width, self.height, 0
                    )

        if self.tag == "video":
            source = self.attrs.get("src")
            if source:
                video_id = app.media.load_video(source)
                if video_id >= 0:
                    if self.attrs.get("_video_started") != "true":
                        engine.lib.video_play(video_id)
                        self.attrs["_video_started"] = "true"
                    engine.lib.video_draw(window_id, video_id, self.abs_x, self.abs_y, self.width, self.height, 0)

        if self.tag == "audio":
            source = self.attrs.get("src")
            autoplay = self.attrs.get("autoplay", "false").lower() == "true"
            if source and autoplay:
                audio_id = app.media.load_audio(source)
                if audio_id >= 0 and self.attrs.get("_audio_started") != "true":
                    engine.lib.audio_play(audio_id)
                    self.attrs["_audio_started"] = "true"

        if self.tag == "progress":
            value = parse_float(self.attrs.get("value"), 0.0)
            max_value = parse_float(self.attrs.get("max"), 100.0)
            percent = 0.0 if max_value <= 0 else min(1.0, max(0.0, value / max_value))
            fill_color = parse_color(self.style.get("fill", "#57d6c8"), (87, 214, 200, 255))
            engine.draw_rounded_rect(
                window_id,
                self.abs_x + 4,
                self.abs_y + 4,
                int((self.width - 8) * percent),
                self.height - 8,
                max(0, radius - 4),
                fill_color,
            )

    @staticmethod
    def _resolve_dimension(value: str | None, fallback: int, parent_value: int) -> int:
        if not value:
            return fallback
        cleaned = value.strip().lower()
        if cleaned.endswith("%"):
            try:
                return int(parent_value * float(cleaned[:-1]) / 100.0)
            except ValueError:
                return fallback
        return parse_size(cleaned, fallback)
