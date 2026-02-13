from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from REMOLib.core import *


@dataclass
class PhysicsBall:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    mass: float
    color: tuple[int, int, int]
    restitution: float = 0.85
    visual: rectObj | None = None
    shadow: rectObj | None = None


class PhysicsSandboxScene(Scene):
    def initOnce(self):
        self.random = random.Random()
        self.gravity = pygame.Vector2(0, 900)
        self.balls: list[PhysicsBall] = []
        self.fixed_dt = 1.0 / 60.0
        self.spawn_cooldown = 0.0
        self.paused = False

        self.bounds = pygame.Rect(40, 120, 2480, 1280)
        self.world_bg = rectObj(self.bounds, color=(30, 38, 62), edge=0, radius=16)
        self.world_border = rectObj(self.bounds, color=(94, 130, 214), edge=4, radius=16)

        # Broad-phase collision optimization(공간 분할):
        # 공 100개 이상일 때 O(n^2) 전체쌍 검사 대신 인접 셀만 검사.
        self.grid_cell_size = 96
        self.last_pair_checks = 0

        self.title = textObj("REMO 2D Physics Sandbox", size=44, color=Cs.white)
        self.title.pos = RPoint(50, 24)

        self.help_text = longTextObj(
            "좌클릭: 공 생성 | 우클릭: 충격파 | SPACE: 일시정지 | C: 전체 삭제 | R: 랜덤 초기화",
            pos=RPoint(50, 80),
            size=26,
            color=Cs.light(Cs.skyblue),
            textWidth=2300,
        )

        self.status_text = textObj("", size=24, color=Cs.white)
        self.status_text.pos = RPoint(50, 1420)

        self._seed_world()

    def _seed_world(self):
        self.balls.clear()
        center_x = self.bounds.centerx
        for index in range(18):
            x = center_x + self.random.randint(-520, 520)
            y = self.bounds.y + 20 + index * 30
            radius = self.random.randint(16, 32)
            mass = radius * radius * 0.08
            velocity = pygame.Vector2(self.random.uniform(-120, 120), self.random.uniform(-80, 120))
            color = (self.random.randint(70, 255), self.random.randint(70, 255), self.random.randint(70, 255))
            self.balls.append(self._create_ball(pygame.Vector2(x, y), velocity, radius, mass, color))

    def _create_ball(
        self,
        position: pygame.Vector2,
        velocity: pygame.Vector2,
        radius: int,
        mass: float,
        color: tuple[int, int, int],
    ) -> PhysicsBall:
        diameter = radius * 2
        shadow = rectObj(pygame.Rect(0, 0, diameter + 4, diameter + 4), color=Cs.dark(color), edge=0, radius=radius + 2)
        visual = rectObj(pygame.Rect(0, 0, diameter, diameter), color=color, edge=0, radius=radius)
        return PhysicsBall(position, velocity, radius, mass, color, visual=visual, shadow=shadow)

    def _spawn_ball(self, position: pygame.Vector2):
        radius = self.random.randint(14, 28)
        mass = radius * radius * 0.08
        velocity = pygame.Vector2(self.random.uniform(-280, 280), self.random.uniform(-240, -60))
        color = (self.random.randint(90, 255), self.random.randint(90, 255), self.random.randint(90, 255))
        self.balls.append(self._create_ball(position, velocity, radius, mass, color))

    def _apply_blast_impulse(self, origin: pygame.Vector2):
        for ball in self.balls:
            offset = ball.pos - origin
            distance = max(1.0, offset.length())
            if distance > 360:
                continue
            direction = offset.normalize() if distance > 0 else pygame.Vector2(1, 0)
            strength = (360 - distance) * 4.2
            ball.vel += direction * (strength / max(1.0, ball.mass))

    def _integrate(self, dt: float):
        damping = 0.998
        for ball in self.balls:
            ball.vel += self.gravity * dt
            ball.vel *= damping
            ball.pos += ball.vel * dt
            self._solve_wall_collision(ball)

        self._solve_ball_collisions_broadphase()

    def _solve_ball_collisions_broadphase(self):
        if len(self.balls) < 2:
            self.last_pair_checks = 0
            return

        cell_size = self.grid_cell_size
        spatial_grid: dict[tuple[int, int], list[int]] = {}

        for index, ball in enumerate(self.balls):
            min_cx = int((ball.pos.x - ball.radius - self.bounds.left) // cell_size)
            max_cx = int((ball.pos.x + ball.radius - self.bounds.left) // cell_size)
            min_cy = int((ball.pos.y - ball.radius - self.bounds.top) // cell_size)
            max_cy = int((ball.pos.y + ball.radius - self.bounds.top) // cell_size)

            for cx in range(min_cx, max_cx + 1):
                for cy in range(min_cy, max_cy + 1):
                    key = (cx, cy)
                    if key not in spatial_grid:
                        spatial_grid[key] = []
                    spatial_grid[key].append(index)

        checked_pairs: set[tuple[int, int]] = set()
        pair_checks = 0

        for indices in spatial_grid.values():
            count = len(indices)
            if count < 2:
                continue
            for i in range(count):
                a_index = indices[i]
                for j in range(i + 1, count):
                    b_index = indices[j]
                    pair = (a_index, b_index) if a_index < b_index else (b_index, a_index)
                    if pair in checked_pairs:
                        continue
                    checked_pairs.add(pair)
                    pair_checks += 1
                    self._solve_ball_collision(self.balls[pair[0]], self.balls[pair[1]])

        self.last_pair_checks = pair_checks

    def _solve_wall_collision(self, ball: PhysicsBall):
        left = self.bounds.left + ball.radius
        right = self.bounds.right - ball.radius
        top = self.bounds.top + ball.radius
        bottom = self.bounds.bottom - ball.radius

        if ball.pos.x < left:
            ball.pos.x = left
            ball.vel.x *= -ball.restitution
        elif ball.pos.x > right:
            ball.pos.x = right
            ball.vel.x *= -ball.restitution

        if ball.pos.y < top:
            ball.pos.y = top
            ball.vel.y *= -ball.restitution
        elif ball.pos.y > bottom:
            ball.pos.y = bottom
            ball.vel.y *= -ball.restitution
            ball.vel.x *= 0.96

    def _solve_ball_collision(self, a: PhysicsBall, b: PhysicsBall):
        delta = b.pos - a.pos
        dist_sq = delta.length_squared()
        min_distance = a.radius + b.radius
        if dist_sq >= min_distance * min_distance:
            return

        distance = math.sqrt(max(0.0001, dist_sq))
        normal = delta / distance if distance > 0 else pygame.Vector2(1, 0)
        penetration = min_distance - distance

        total_mass = a.mass + b.mass
        if total_mass <= 0:
            return

        correction = normal * penetration
        a.pos -= correction * (b.mass / total_mass)
        b.pos += correction * (a.mass / total_mass)

        relative_velocity = b.vel - a.vel
        separating_speed = relative_velocity.dot(normal)
        if separating_speed > 0:
            return

        restitution = min(a.restitution, b.restitution)
        impulse_size = -(1 + restitution) * separating_speed
        impulse_size /= (1 / a.mass) + (1 / b.mass)

        impulse = normal * impulse_size
        a.vel -= impulse / a.mass
        b.vel += impulse / b.mass

    def update(self):
        if Rs.userJustPressed(pygame.K_SPACE):
            self.paused = not self.paused
        if Rs.userJustPressed(pygame.K_c):
            self.balls.clear()
        if Rs.userJustPressed(pygame.K_r):
            self._seed_world()

        mouse = pygame.Vector2(Rs.mousePos().toTuple())

        if Rs.userJustRightClicked():
            self._apply_blast_impulse(mouse)

        self.spawn_cooldown = max(0.0, self.spawn_cooldown - self.fixed_dt)
        if Rs.userJustLeftClicked() and self.spawn_cooldown <= 0.0:
            if self.bounds.collidepoint(mouse.x, mouse.y):
                self._spawn_ball(mouse)
                self.spawn_cooldown = 0.06

        if not self.paused:
            for _ in range(2):
                self._integrate(self.fixed_dt * 0.5)

        paused_text = "일시정지" if self.paused else "실행중"
        self.status_text.text = (
            f"상태: {paused_text} | 공 개수: {len(self.balls)} | 중력: {int(self.gravity.y)}"
            f" | 충돌쌍 검사: {self.last_pair_checks}"
        )

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.midnightblue))
        self.world_bg.draw()
        self.world_border.draw()

        for ball in self.balls:
            center = RPoint(int(ball.pos.x), int(ball.pos.y))
            if ball.shadow:
                ball.shadow.center = center
                ball.shadow.draw()
            if ball.visual:
                ball.visual.center = center
                ball.visual.draw()

        self.title.draw()
        self.help_text.draw()
        self.status_text.draw()


class Scenes:
    mainScene = PhysicsSandboxScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(2560, 1440), fullscreen=False, caption="48-2D Physics Sandbox")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
