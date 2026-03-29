from __future__ import annotations


class MediaManager:
    def __init__(self, engine: "EngineBridge") -> None:
        self.engine = engine
        self.images: dict[str, int] = {}
        self.audio: dict[str, int] = {}
        self.videos: dict[str, int] = {}
        self.fonts: dict[tuple[str, int], int] = {}

    def load_image(self, path: str) -> int:
        if path not in self.images:
            self.images[path] = self.engine.load_image(path)
        return self.images[path]

    def load_audio(self, path: str) -> int:
        if path not in self.audio:
            self.audio[path] = self.engine.load_audio(path)
        return self.audio[path]

    def load_video(self, path: str) -> int:
        if path not in self.videos:
            self.videos[path] = self.engine.load_video(path)
        return self.videos[path]

    def load_font(self, path: str, size: int) -> int:
        key = (path, size)
        if key not in self.fonts:
            self.fonts[key] = self.engine.load_font(path, size)
        return self.fonts[key]
