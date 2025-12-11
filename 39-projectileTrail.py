from collections import deque
from typing import Any, Sequence

import pygame

from REMOLib import *


def rgba(color: Sequence[int], alpha: int) -> tuple[int, int, int, int]:
    """Utility to ensure RGBA tuples use integer components and a specific alpha."""

    base = color[:3]
    clamped_alpha = max(0, min(255, int(alpha)))
    return tuple(int(round(component)) for component in base) + (clamped_alpha,)


class Projectile:
    """마우스 방향으로 날아가면서 빛나는 궤적을 남기는 투사체."""

    def __init__(self, origin: pygame.Vector2, direction: pygame.Vector2):
        self.pos = pygame.Vector2(origin)
        velocity = pygame.Vector2(direction)
        if velocity.length_squared() == 0:
            velocity = pygame.Vector2(1, 0)
        else:
            velocity = velocity.normalize()
        self.velocity = velocity * 18
        self.radius = 10
        self.trail = deque(maxlen=28)
        self.life_frames = 240

    def update(self) -> bool:
        """투사체를 이동시키고, 소멸 여부를 반환합니다."""

        self.trail.appendleft(self.pos.copy())
        self.pos += self.velocity
        self.life_frames -= 1

        extended_bounds = Rs.screenRect().inflate(200, 200)
        off_screen = not extended_bounds.collidepoint(self.pos.x, self.pos.y)
        return self.life_frames <= 0 or off_screen

    def draw(self) -> None:
        engine = Rs.render_engine
        layer = Rs.source_layer

        for index, point in enumerate(self.trail):
            alpha = max(0, 220 - index * 12)
            if alpha <= 0:
                continue
            radius = max(2, self.radius - index // 3)
            engine.render_circle(
                layer,
                rgba((255, 210, 120), alpha),
                (point.x, point.y),
                radius,
                antialias=True,
            )

        center = (self.pos.x, self.pos.y)
        engine.render_circle(layer, rgba(Cs.orange, 255), center, self.radius, antialias=True)
        engine.render_circle(layer, rgba(Cs.gold, 255), center, self.radius - 2, antialias=True)


class Player:
    """단순한 원형 플레이어 캐릭터."""

    def __init__(self):
        self.pos = pygame.Vector2(Rs.screenRect().center)
        self.radius = 18
        self.speed = 6

    def update(self) -> None:
        move = pygame.Vector2(0, 0)
        if Rs.userPressing(pygame.K_LEFT) or Rs.userPressing(pygame.K_a):
            move.x -= 1
        if Rs.userPressing(pygame.K_RIGHT) or Rs.userPressing(pygame.K_d):
            move.x += 1
        if Rs.userPressing(pygame.K_UP) or Rs.userPressing(pygame.K_w):
            move.y -= 1
        if Rs.userPressing(pygame.K_DOWN) or Rs.userPressing(pygame.K_s):
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize() * self.speed
            self.pos += move

        bounds = Rs.screenRect()
        self.pos.x = max(self.radius, min(bounds.width - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(bounds.height - self.radius, self.pos.y))

    def draw(self) -> None:
        engine = Rs.render_engine
        layer = Rs.source_layer
        center = (self.pos.x, self.pos.y)

        engine.render_circle(layer, rgba(Cs.white, 255), center, self.radius, antialias=True)
        engine.render_circle(layer, rgba(Cs.cyan, 255), center, self.radius - 3, antialias=True)

    @property
    def center(self) -> pygame.Vector2:
        return self.pos


class ProjectileTrailScene(Scene):
    def initOnce(self):
        self.player = Player()
        self.projectiles: list[Projectile] = []

        self.title = textObj(
            "39. 투사체 궤적 예제",
            pos=RPoint(40, 40),
            size=36,
            color=Cs.white,
        )
        self.instructions = [
            textObj(
                "WASD / 화살표 키로 플레이어를 이동합니다.",
                pos=RPoint(40, 100),
                size=24,
                color=Cs.light(Cs.white),
            ),
            textObj(
                "마우스로 조준하고 클릭하여 투사체를 발사하세요.",
                pos=RPoint(40, 136),
                size=24,
                color=Cs.light(Cs.white),
            ),
            textObj(
                "투사체는 이동 경로에 따라 부드러운 빛의 궤적을 남깁니다.",
                pos=RPoint(40, 172),
                size=24,
                color=Cs.light(Cs.white),
            ),
        ]

        self.background_surface, self.background_texture = self._generate_grid()

    def _generate_grid(self) -> tuple[pygame.Surface, Any]:
        surface = pygame.Surface(Rs.screen_size, pygame.SRCALPHA)
        surface.fill((*Cs.darkslategray, 255))
        spacing = 64
        dim_color = Cs.dim(Cs.darkslategray)
        for x in range(0, Rs.screen_size[0], spacing):
            pygame.draw.line(surface, dim_color, (x, 0), (x, Rs.screen_size[1]))
        for y in range(0, Rs.screen_size[1], spacing):
            pygame.draw.line(surface, dim_color, (0, y), (Rs.screen_size[0], y))
        texture = Rs.render_engine.surface_to_texture(surface)
        return surface, texture

    def init(self):
        return

    def _spawn_projectile(self) -> None:
        mouse = Rs.mousePos()
        direction = pygame.Vector2(mouse.x, mouse.y) - self.player.center
        self.projectiles.append(Projectile(self.player.center, direction))

    def update(self):
        self.player.update()

        if Rs.userJustLeftClicked():
            self._spawn_projectile()

        alive: list[Projectile] = []
        for projectile in self.projectiles:
            if not projectile.update():
                alive.append(projectile)
        self.projectiles = alive

    def _draw_aim_line(self) -> None:
        engine = Rs.render_engine
        layer = Rs.source_layer
        mouse = Rs.mousePos()
        start = (self.player.center.x, self.player.center.y)
        end = (mouse.x, mouse.y)
        engine.render_thick_line(
            layer,
            rgba(Cs.light(Cs.orange), 255),
            start,
            end,
            2,
            antialias=True,
        )

        engine.render_circle(layer, rgba(Cs.white, 60), end, 12, antialias=True)
        engine.render_thick_line(
            layer,
            rgba(Cs.white, 255),
            (end[0] - 10, end[1]),
            (end[0] + 10, end[1]),
            2,
            antialias=True,
        )
        engine.render_thick_line(
            layer,
            rgba(Cs.white, 255),
            (end[0], end[1] - 10),
            (end[0], end[1] + 10),
            2,
            antialias=True,
        )

    def draw(self):
        Rs.fillScreen(Cs.darkslategray)
        if self.background_texture.glo == 0:
            self.background_texture = Rs.render_engine.surface_to_texture(self.background_surface)
        Rs.render_engine.render(
            self.background_texture,
            Rs.source_layer,
            position=(0, 0),
        )

        self._draw_aim_line()

        for projectile in self.projectiles:
            projectile.draw()
        self.player.draw()

        self.title.draw()
        for info in self.instructions:
            info.draw()


class Scenes:
    main = ProjectileTrailScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="39. Projectile Trail",
    )
    window.setCurrentScene(Scenes.main)
    window.run()
