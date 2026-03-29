from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Animation:
    element_id: str
    property_name: str
    start_value: float
    end_value: float
    duration: float
    elapsed: float = 0.0


class AnimationManager:
    def __init__(self) -> None:
        self.animations: list[Animation] = []

    def add(self, animation: Animation) -> None:
        self.animations.append(animation)

    def update(self, delta_time: float) -> None:
        active: list[Animation] = []
        for animation in self.animations:
            animation.elapsed += delta_time
            if animation.elapsed < animation.duration:
                active.append(animation)
        self.animations = active
