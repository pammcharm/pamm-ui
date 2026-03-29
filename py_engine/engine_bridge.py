import ctypes
import os
from pathlib import Path


class EngineBridge:
    def __init__(self, dll_path: str | None = None) -> None:
        self.dll_path = self._resolve_dll_path(dll_path)
        runtime_dir = Path(r"C:\msys64\ucrt64\bin")
        if runtime_dir.exists():
            os.add_dll_directory(str(runtime_dir))
        self.lib = ctypes.CDLL(str(self.dll_path))
        self._bind()

    @staticmethod
    def _resolve_dll_path(dll_path: str | None) -> Path:
        if dll_path:
            candidate = Path(dll_path).resolve()
            if candidate.exists():
                return candidate
            raise FileNotFoundError(f"PAMM engine DLL was not found at {candidate}")

        package_dir = Path(__file__).resolve().parent
        repo_root = package_dir.parent
        candidates = [
            package_dir / "main_engine.dll",
            repo_root / "c_engine" / "main_engine.dll",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        searched = ", ".join(str(path) for path in candidates)
        raise FileNotFoundError(f"PAMM engine DLL was not found. Searched: {searched}")

    def _bind(self) -> None:
        self.lib.engine_init.restype = ctypes.c_int
        self.lib.engine_shutdown.restype = None
        self.lib.engine_run_loop.restype = None
        self.lib.engine_run_loop_step.restype = None
        self.lib.engine_get_delta_time.restype = ctypes.c_double

        self.lib.window_create_ex.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        self.lib.window_create_ex.restype = ctypes.c_int
        self.lib.window_move.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.window_resize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.window_focus.argtypes = [ctypes.c_int]
        self.lib.window_close.argtypes = [ctypes.c_int]
        self.lib.window_set_screen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.window_set_title.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.lib.window_set_icon.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.lib.window_set_icon.restype = ctypes.c_int
        self.lib.window_show.argtypes = [ctypes.c_int]
        self.lib.window_hide.argtypes = [ctypes.c_int]
        self.lib.window_minimize.argtypes = [ctypes.c_int]
        self.lib.window_maximize.argtypes = [ctypes.c_int]
        self.lib.window_restore.argtypes = [ctypes.c_int]

        self.lib.layer_add.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.layer_add.restype = ctypes.c_int
        self.lib.layer_set_z_order.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

        self.lib.load_font.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.load_font.restype = ctypes.c_int
        self.lib.image_load.argtypes = [ctypes.c_char_p]
        self.lib.image_load.restype = ctypes.c_int
        self.lib.audio_load.argtypes = [ctypes.c_char_p]
        self.lib.audio_load.restype = ctypes.c_int
        self.lib.video_load.argtypes = [ctypes.c_char_p]
        self.lib.video_load.restype = ctypes.c_int

        self.lib.render_draw_pixel.argtypes = [ctypes.c_int] * 8
        self.lib.render_draw_line.argtypes = [ctypes.c_int] * 9
        self.lib.render_draw_rect.argtypes = [ctypes.c_int] * 11
        self.lib.render_draw_circle.argtypes = [ctypes.c_int] * 10
        self.lib.render_draw_rounded_rect.argtypes = [ctypes.c_int] * 12
        self.lib.render_draw_gradient_rect.argtypes = [ctypes.c_int] * 15
        self.lib.render_draw_text.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.lib.render_draw_image.argtypes = [ctypes.c_int] * 6
        self.lib.video_draw.argtypes = [ctypes.c_int] * 7
        self.lib.render_present.restype = None
        self.lib.clear_window.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

        self.lib.engine_poll_events.restype = ctypes.c_int
        self.lib.input_get_mouse_position.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.lib.input_get_focused_window.restype = ctypes.c_int
        self.lib.input_is_key_pressed.argtypes = [ctypes.c_int]
        self.lib.input_is_key_pressed.restype = ctypes.c_int
        self.lib.input_is_mouse_clicked.argtypes = [ctypes.c_int]
        self.lib.input_is_mouse_clicked.restype = ctypes.c_int
        self.lib.input_is_mouse_down.argtypes = [ctypes.c_int]
        self.lib.input_is_mouse_down.restype = ctypes.c_int

        self.lib.animate_property.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
        ]
        self.lib.animate_property.restype = ctypes.c_int
        self.lib.update_animations.argtypes = [ctypes.c_double]

        self.lib.audio_play.argtypes = [ctypes.c_int]
        self.lib.audio_pause.argtypes = [ctypes.c_int]
        self.lib.audio_stop.argtypes = [ctypes.c_int]
        self.lib.audio_set_volume.argtypes = [ctypes.c_int, ctypes.c_double]
        self.lib.audio_set_loop.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.video_play.argtypes = [ctypes.c_int]
        self.lib.video_pause.argtypes = [ctypes.c_int]
        self.lib.video_stop.argtypes = [ctypes.c_int]

    def init(self) -> int:
        return self.lib.engine_init()

    def shutdown(self) -> None:
        self.lib.engine_shutdown()

    def create_window(
        self, width: int, height: int, title: str = "Pamm Engine", screen_id: int = 0, borderless: bool = True
    ) -> int:
        return self.lib.window_create_ex(width, height, title.encode("utf-8"), screen_id, 1 if borderless else 0)

    def poll_events(self) -> int:
        return self.lib.engine_poll_events()

    def clear_window(self, window_id: int, color: tuple[int, int, int, int]) -> None:
        self.lib.clear_window(window_id, color[0], color[1], color[2], color[3])

    def set_title(self, window_id: int, title: str) -> None:
        self.lib.window_set_title(window_id, title.encode("utf-8"))

    def set_icon(self, window_id: int, icon_path: str) -> int:
        return self.lib.window_set_icon(window_id, icon_path.encode("utf-8"))

    def load_font(self, path: str, size: int) -> int:
        return self.lib.load_font(path.encode("utf-8"), size)

    def load_image(self, path: str) -> int:
        return self.lib.image_load(path.encode("utf-8"))

    def load_audio(self, path: str) -> int:
        return self.lib.audio_load(path.encode("utf-8"))

    def load_video(self, path: str) -> int:
        return self.lib.video_load(path.encode("utf-8"))

    def draw_text(
        self,
        window_id: int,
        text: str,
        x: int,
        y: int,
        font_id: int,
        color: tuple[int, int, int, int],
        layer_id: int = 0,
    ) -> None:
        self.lib.render_draw_text(
            window_id, text.encode("utf-8"), x, y, font_id, color[0], color[1], color[2], color[3], layer_id
        )

    def draw_rect(
        self,
        window_id: int,
        x: int,
        y: int,
        width: int,
        height: int,
        color: tuple[int, int, int, int],
        filled: bool = True,
        layer_id: int = 0,
    ) -> None:
        self.lib.render_draw_rect(
            window_id,
            x,
            y,
            width,
            height,
            color[0],
            color[1],
            color[2],
            color[3],
            1 if filled else 0,
            layer_id,
        )

    def draw_rounded_rect(
        self,
        window_id: int,
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int,
        color: tuple[int, int, int, int],
        filled: bool = True,
        layer_id: int = 0,
    ) -> None:
        self.lib.render_draw_rounded_rect(
            window_id,
            x,
            y,
            width,
            height,
            radius,
            color[0],
            color[1],
            color[2],
            color[3],
            1 if filled else 0,
            layer_id,
        )

    def draw_gradient_rect(
        self,
        window_id: int,
        x: int,
        y: int,
        width: int,
        height: int,
        start_color: tuple[int, int, int, int],
        end_color: tuple[int, int, int, int],
        vertical: bool = True,
        layer_id: int = 0,
    ) -> None:
        self.lib.render_draw_gradient_rect(
            window_id,
            x,
            y,
            width,
            height,
            start_color[0],
            start_color[1],
            start_color[2],
            start_color[3],
            end_color[0],
            end_color[1],
            end_color[2],
            end_color[3],
            1 if vertical else 0,
            layer_id,
        )

    def mouse_position(self) -> tuple[int, int]:
        x = ctypes.c_int()
        y = ctypes.c_int()
        self.lib.input_get_mouse_position(ctypes.byref(x), ctypes.byref(y))
        return x.value, y.value

    def present(self) -> None:
        self.lib.render_present()


if __name__ == "__main__":
    engine = EngineBridge()
    engine.init()
    window_id = engine.create_window(960, 640, "Engine Bridge Test")
    engine.lib.clear_window(window_id, 24, 26, 32, 255)
    engine.present()
