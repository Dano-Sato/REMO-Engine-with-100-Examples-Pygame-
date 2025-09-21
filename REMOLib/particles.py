"""Particle system utilities for REMO Engine examples."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, replace
from typing import Optional, Sequence, Tuple

import pygame

from .core import RPoint, REMOGame, graphicObj


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _to_vector2(value: RPoint | Sequence[float] | pygame.Vector2) -> pygame.Vector2:
    if isinstance(value, pygame.Vector2):
        return value.copy()
    if isinstance(value, RPoint):
        return pygame.Vector2(value.x, value.y)
    return pygame.Vector2(float(value[0]), float(value[1]))


@dataclass
class ParticleDefaults:
    """파티클 기본 설정을 묶어서 다루기 위한 데이터 클래스."""

    velocity_range: Tuple[Tuple[float, float], Tuple[float, float]] = ((-60.0, 60.0), (-60.0, 60.0))
    speed_range: Optional[Tuple[float, float]] = None
    direction_range: Tuple[float, float] = (0.0, 360.0)
    lifetime_range: Tuple[float, float] = (0.6, 1.2)
    size_range: Tuple[float, float] = (4.0, 10.0)
    color: Tuple[int, int, int] = (255, 255, 255)
    color_range: Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = None
    alpha_range: Tuple[int, int] = (200, 255)
    gravity: float = 0.0
    fade: bool = True
    shrink: bool = True
    position_jitter: Tuple[Tuple[float, float], Tuple[float, float]] = ((0.0, 0.0), (0.0, 0.0))


class Particle(graphicObj):
    """단일 파티클 오브젝트.

    REMO 엔진의 graphicObj를 상속하여 기존 렌더링 파이프라인과
    자연스럽게 연결되도록 설계되었습니다.
    """

    _surface_cache: dict[tuple[int, Tuple[int, int, int]], pygame.Surface] = {}
    _surface_cache_limit = 256

    def __init__(
        self,
        position: Sequence[float] | RPoint | pygame.Vector2,
        velocity: Sequence[float] | RPoint | pygame.Vector2,
        lifetime: float,
        *,
        size: float,
        color: Sequence[int],
        alpha: int = 255,
        gravity: float = 0.0,
        fade: bool = True,
        shrink: bool = True,
    ) -> None:
        if REMOGame._lastStartedWindow is None:
            raise RuntimeError("Particle requires an active REMOGame window.")

        self._center = _to_vector2(position)
        self.velocity = _to_vector2(velocity)
        self.lifetime = max(0.016, float(lifetime))
        self.age = 0.0
        self.gravity = float(gravity)
        self.fade = fade
        self.shrink = shrink

        rounded_size = max(1, int(round(size)))
        self.initial_size = rounded_size
        self.current_size = rounded_size

        color_tuple = tuple(int(_clamp(channel, 0, 255)) for channel in color)
        self.color: Tuple[int, int, int] = color_tuple  # type: ignore[assignment]
        self.initial_alpha = int(_clamp(alpha, 0, 255))

        super().__init__(pygame.Rect(0, 0, rounded_size, rounded_size))

        surface = self._get_surface(self.current_size, self.color)
        self.graphic_n = surface
        self.graphic = surface
        self.alpha = self.initial_alpha
        self._apply_position()

    def _apply_position(self) -> None:
        half_size = self.current_size / 2.0
        top_left = self._center - pygame.Vector2(half_size, half_size)
        self.pos = RPoint(int(round(top_left.x)), int(round(top_left.y)))

    @classmethod
    def _get_surface(cls, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
        cache_key = (size, color)
        surface = cls._surface_cache.get(cache_key)
        if surface is None:
            surface = REMOGame._lastStartedWindow.surface_pool.get_surface((size, size))
            surface.fill((0, 0, 0, 0))
            if size <= 2:
                surface.fill(color)
            else:
                radius = max(1, size // 2)
                center = (size // 2, size // 2)
                pygame.draw.circle(surface, color, center, radius)
            if len(cls._surface_cache) >= cls._surface_cache_limit:
                cls._surface_cache.pop(next(iter(cls._surface_cache)))
            cls._surface_cache[cache_key] = surface
        return surface

    def update(self, delta_time: float) -> bool:
        self.age += delta_time
        if self.age >= self.lifetime:
            return False

        self.velocity.y += self.gravity * delta_time
        self._center += self.velocity * delta_time

        life_ratio = 1.0 - (self.age / self.lifetime)
        life_ratio = _clamp(life_ratio, 0.0, 1.0)

        if self.fade:
            self.alpha = int(self.initial_alpha * life_ratio)

        if self.shrink:
            new_size = max(1, int(round(self.initial_size * life_ratio)))
            if new_size != self.current_size:
                self.current_size = new_size
                surface = self._get_surface(self.current_size, self.color)
                self.graphic_n = surface
                self.graphic = surface

        self._apply_position()
        return True


class ParticleEmitter:
    """파티클 생성과 관리를 담당하는 클래스."""

    def __init__(
        self,
        position: Sequence[float] | RPoint | pygame.Vector2,
        *,
        emission_rate: float = 0.0,
        max_particles: int = 256,
        defaults: Optional[ParticleDefaults] = None,
    ) -> None:
        self._position = _to_vector2(position)
        self.emission_rate = float(emission_rate)
        self.max_particles = max(0, int(max_particles)) or 1
        self.defaults = defaults or ParticleDefaults()
        self.active = True

        self.particles: list[Particle] = []
        self._emit_accumulator = 0.0
        self._last_update_time = time.time()

    @property
    def pos(self) -> RPoint:
        return RPoint(int(round(self._position.x)), int(round(self._position.y)))

    @pos.setter
    def pos(self, value: Sequence[float] | RPoint | pygame.Vector2) -> None:
        self._position = _to_vector2(value)

    def move(self, delta: Sequence[float] | RPoint | pygame.Vector2) -> None:
        self._position += _to_vector2(delta)

    def set_defaults(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.defaults, key):
                setattr(self.defaults, key, value)

    def emit(self, count: int, **overrides) -> None:
        if count <= 0 or not self.active:
            return

        settings = replace(self.defaults)
        for key, value in overrides.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        base_position = _to_vector2(overrides.get("position", self._position))
        jitter_x = settings.position_jitter[0]
        jitter_y = settings.position_jitter[1]

        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            spawn_pos = pygame.Vector2(base_position)
            if jitter_x[0] != 0.0 or jitter_x[1] != 0.0:
                spawn_pos.x += random.uniform(jitter_x[0], jitter_x[1])
            if jitter_y[0] != 0.0 or jitter_y[1] != 0.0:
                spawn_pos.y += random.uniform(jitter_y[0], jitter_y[1])

            if settings.speed_range:
                speed = random.uniform(*settings.speed_range)
                angle = math.radians(random.uniform(*settings.direction_range))
                velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            else:
                vx = random.uniform(*settings.velocity_range[0])
                vy = random.uniform(*settings.velocity_range[1])
                velocity = pygame.Vector2(vx, vy)

            lifetime = random.uniform(*settings.lifetime_range)
            size = random.uniform(*settings.size_range)

            if settings.color_range:
                color = tuple(
                    random.randint(channel_range[0], channel_range[1])
                    for channel_range in settings.color_range
                )
            else:
                color = settings.color

            alpha = random.randint(*settings.alpha_range)

            particle = Particle(
                spawn_pos,
                velocity,
                lifetime,
                size=size,
                color=color,
                alpha=alpha,
                gravity=settings.gravity,
                fade=settings.fade,
                shrink=settings.shrink,
            )
            self.particles.append(particle)

    def update(self, delta_time: Optional[float] = None) -> None:
        if delta_time is None:
            now = time.time()
            delta_time = now - self._last_update_time
            self._last_update_time = now
        else:
            self._last_update_time = time.time()

        if self.active and self.emission_rate > 0:
            self._emit_accumulator += delta_time * self.emission_rate
            spawn_count = int(self._emit_accumulator)
            if spawn_count > 0:
                self._emit_accumulator -= spawn_count
                self.emit(spawn_count)

        alive_particles = []
        for particle in self.particles:
            if particle.update(delta_time):
                alive_particles.append(particle)
        self.particles = alive_particles

    def draw(self) -> None:
        for particle in self.particles:
            particle.draw()

    def clear(self) -> None:
        self.particles.clear()

    def stop(self) -> None:
        self.active = False

    def start(self) -> None:
        self.active = True
