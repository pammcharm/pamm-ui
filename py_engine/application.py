from __future__ import annotations

import sys
import time
from pathlib import Path

from py_engine.animation import AnimationManager
from py_engine.config import ProjectConfig
from py_engine.engine_bridge import EngineBridge
from py_engine.events import EventManager, InputEvent
from py_engine.layout import LayoutManager
from py_engine.media import MediaManager
from py_engine.parser import HTMLParser, PythonLogicLoader
from py_engine.style import StyleManager, parse_color


class Application:
    def __init__(self, dll_path: str | None = None) -> None:
        self.engine = EngineBridge(dll_path=dll_path)
        self.html_parser = HTMLParser()
        self.logic_loader = PythonLogicLoader()
        self.styles = StyleManager()
        self.layout = LayoutManager()
        self.events = EventManager()
        self.animations = AnimationManager()
        self.logic_module = None
        self.media = MediaManager(self.engine)
        self.main_window = None
        self.window_id = -1
        self.default_font_path = self._pick_font_path()
        self.hovered_element = None
        self.last_frame_time = time.perf_counter()
        self.project_root = Path.cwd()
        self.project_config: ProjectConfig | None = None
        self._watch_files: list[Path] = []
        self._watch_mtimes: dict[Path, float] = {}
        self._reloading = False

    def load_html(self, path: str) -> None:
        self.main_window = self.html_parser.parse_file(self.project_root / path)

    def load_css(self, path: str) -> None:
        css_path = self.project_root / path
        if css_path.exists():
            self.styles.load(css_path.read_text(encoding="utf-8"))

    def load_logic(self, path: str | None) -> None:
        logic_path = self.project_root / path if path else None
        if logic_path and logic_path.exists():
            self.logic_module = self.logic_loader.load_module(logic_path)

    def load_project(self, config_path: str | Path) -> ProjectConfig:
        config_source = Path(config_path).resolve()
        config = ProjectConfig.from_file(config_source)
        self.project_config = config
        self.project_root = (
            Path(config.working_directory).resolve() if config.working_directory else config_source.parent
        )
        project_root_str = str(self.project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
        if config.dll_path:
            self.engine = EngineBridge(dll_path=str((self.project_root / config.dll_path).resolve()))
            self.media = MediaManager(self.engine)
        self.load_html(config.html)
        for css_path in config.css:
            self.load_css(css_path)
        for logic_path in config.logic:
            self.load_logic(logic_path)
        self._setup_watch_files(config)
        return config

    def get_font(self, size: int) -> int:
        return self.media.load_font(self.default_font_path, size)

    def iter_elements(self):
        if not self.main_window:
            return []
        stack = [self.main_window.element]
        ordered = []
        while stack:
            element = stack.pop(0)
            ordered.append(element)
            stack[0:0] = element.children
        return ordered

    def call_handler(self, name: str, element) -> None:
        if self.logic_module and hasattr(self.logic_module, name):
            getattr(self.logic_module, name)(self, element)

    def start(self) -> None:
        if not self.main_window:
            raise RuntimeError("No htmlpy file has been loaded.")
        if self.engine.init() != 0:
            raise RuntimeError("Engine failed to initialize.")

        self.window_id = self.engine.create_window(
            self.main_window.width,
            self.main_window.height,
            self.main_window.title,
            borderless=self.main_window.borderless,
        )
        self.last_frame_time = time.perf_counter()

        if self.main_window.icon:
            icon_path = self.project_root / self.main_window.icon
            self.engine.set_icon(self.window_id, str(icon_path))

    def run(self) -> None:
        self.start()
        try:
            while True:
                if self.engine.poll_events():
                    break
                now = time.perf_counter()
                delta_time = now - self.last_frame_time
                self.last_frame_time = now
                self.animations.update(delta_time)
                self._maybe_reload_project()
                self._frame()
                time.sleep(1 / 60)
        finally:
            self.engine.shutdown()

    def _frame(self) -> None:
        if not self.main_window:
            return

        mouse_x, mouse_y = self.engine.mouse_position()
        event = InputEvent(
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            mouse_clicked=bool(self.engine.lib.input_is_mouse_clicked(1)),
            mouse_down=bool(self.engine.lib.input_is_mouse_down(1)),
        )

        self._apply_styles(self.main_window.element, 0, 0, self.main_window.width, self.main_window.height)
        self.events.dispatch(self, event)
        self._apply_styles(self.main_window.element, 0, 0, self.main_window.width, self.main_window.height)

        background = parse_color(
            self.main_window.element.attrs.get("background", self.main_window.element.style.get("background")),
            (16, 18, 24, 255),
        )
        self.engine.clear_window(self.window_id, background)
        self._render_tree(self.main_window.element, self.get_font(24))
        self.engine.present()

    def _apply_styles(self, element, parent_x: int, parent_y: int, parent_width: int, parent_height: int) -> None:
        state = set()
        if self.hovered_element is element:
            state.add("hover")
        style = self.styles.compute_style(element.tag, element.attrs, state)
        element.apply_style(style, parent_width, parent_height)
        element.update_absolute_position(parent_x, parent_y)
        self.layout.layout_children(element)
        for child in element.children:
            self._apply_styles(child, element.abs_x, element.abs_y, element.width, element.height)

    def _render_tree(self, element, parent_font_id: int) -> None:
        element.render(self, parent_font_id)
        for child in element.children:
            self._render_tree(child, parent_font_id)

    def _setup_watch_files(self, config: ProjectConfig) -> None:
        if not config.autoreload:
            self._watch_files = []
            self._watch_mtimes = {}
            return

        candidates: list[Path] = [self.project_root / config.html]
        candidates.extend(self.project_root / css_path for css_path in config.css)
        candidates.extend(self.project_root / logic_path for logic_path in config.logic)

        for extra in config.watch or []:
            target = self.project_root / extra
            if target.is_dir():
                candidates.extend(path for path in target.rglob("*") if path.is_file())
            elif target.exists():
                candidates.append(target)

        unique_files: list[Path] = []
        seen: set[Path] = set()
        for file_path in candidates:
            resolved = file_path.resolve()
            if resolved.exists() and resolved not in seen:
                seen.add(resolved)
                unique_files.append(resolved)

        self._watch_files = unique_files
        self._watch_mtimes = {path: path.stat().st_mtime for path in unique_files}

    def _maybe_reload_project(self) -> None:
        if not self.project_config or not self.project_config.autoreload or self._reloading:
            return

        changed = False
        for path in self._watch_files:
            if not path.exists():
                continue
            current_mtime = path.stat().st_mtime
            previous_mtime = self._watch_mtimes.get(path)
            if previous_mtime is None or current_mtime > previous_mtime:
                changed = True
                break

        if changed:
            self._reload_project_state()

    def _reload_project_state(self) -> None:
        if not self.project_config:
            return

        self._reloading = True
        try:
            self.styles = StyleManager()
            self.animations = AnimationManager()
            self.logic_module = None
            self.hovered_element = None
            self.media = MediaManager(self.engine)
            self.load_html(self.project_config.html)
            for css_path in self.project_config.css:
                self.load_css(css_path)
            for logic_path in self.project_config.logic:
                self.load_logic(logic_path)
            self._setup_watch_files(self.project_config)
        finally:
            self._reloading = False

    @staticmethod
    def _pick_font_path() -> str:
        candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        raise FileNotFoundError("No default Windows font was found.")
