from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from REMOLib.core import *


@dataclass
class BilliardBall:
    name: str
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    mass: float
    color: tuple[int, int, int]
    number: int
    is_cue: bool = False
    visual: rectObj | None = None
    shadow: rectObj | None = None
    number_label: textObj | None = None
    alive: bool = True


class BilliardsScene(Scene):
    def initOnce(self):
        self.fixed_dt = 1.0 / 120.0
        self.substeps = 2
        self.ball_restitution = 0.97
        self.cushion_restitution = 0.9
        self.friction = 0.992
        self.min_speed = 5.0
        self.max_shot_power = 5600.0

        self.table_outer = pygame.Rect(130, 90, 2300, 1260)
        self.table_inner = pygame.Rect(220, 180, 2120, 1080)

        self.outer_frame = rectObj(self.table_outer, color=(88, 52, 32), edge=0, radius=28)
        self.inner_shadow = rectObj(self.table_inner.inflate(24, 24), color=(30, 80, 45), edge=0, radius=24)
        self.table_felt = rectObj(self.table_inner, color=(38, 140, 82), edge=0, radius=18)

        self.ball_radius = 24
        pocket_r = 42
        left, right = self.table_inner.left, self.table_inner.right
        top, bottom = self.table_inner.top, self.table_inner.bottom
        mid_x = self.table_inner.centerx

        self.pockets: list[tuple[pygame.Vector2, float, rectObj]] = []
        for px, py in [
            (left, top),
            (mid_x, top - 4),
            (right, top),
            (left, bottom),
            (mid_x, bottom + 4),
            (right, bottom),
        ]:
            pocket_vis = rectObj(pygame.Rect(0, 0, pocket_r * 2, pocket_r * 2), color=(14, 18, 14), edge=0, radius=pocket_r)
            pocket_vis.center = RPoint(px, py)
            self.pockets.append((pygame.Vector2(px, py), pocket_r, pocket_vis))

        self.title = textObj("REMO Billiards", pos=RPoint(80, 20), size=52, color=Cs.white)
        self.guide = textObj("마우스로 조준하고 드래그 후 발사 | R: 재시작", pos=RPoint(80, 84), size=30, color=Cs.grey75)
        self.state_text = textObj("", pos=RPoint(80, 1300), size=34, color=Cs.white)

        self.power_bar_bg = rectObj(pygame.Rect(80, 1360, 460, 26), color=(26, 26, 26), edge=0, radius=8)
        self.power_bar_fill = rectObj(pygame.Rect(84, 1364, 452, 18), color=(250, 208, 74), edge=0, radius=6)
        self.power_ratio = 0.0

        self.dragging = False
        self.drag_start = pygame.Vector2(0, 0)
        self.drag_now = pygame.Vector2(0, 0)
        self.game_over = False

        self._reset_rack()

    def _make_ball(self, name: str, pos: pygame.Vector2, color: tuple[int, int, int], number: int, is_cue: bool = False) -> BilliardBall:
        diameter = int(self.ball_radius * 2)
        shadow = rectObj(pygame.Rect(0, 0, diameter + 6, diameter + 6), color=(10, 20, 10), edge=0, radius=self.ball_radius + 3)
        visual = rectObj(pygame.Rect(0, 0, diameter, diameter), color=color, edge=0, radius=self.ball_radius)
        label = textObj(str(number), size=24, color=Cs.white)
        return BilliardBall(
            name=name,
            pos=pygame.Vector2(pos),
            vel=pygame.Vector2(0, 0),
            radius=self.ball_radius,
            mass=self.ball_radius * self.ball_radius,
            color=color,
            number=number,
            is_cue=is_cue,
            visual=visual,
            shadow=shadow,
            number_label=label,
        )

    def _reset_rack(self):
        self.balls: list[BilliardBall] = []
        self.pocketed_count = 0

        cue_start = pygame.Vector2(self.table_inner.left + 370, self.table_inner.centery)
        self.cue_ball = self._make_ball("cue", cue_start, (248, 248, 248), 0, is_cue=True)
        self.balls.append(self.cue_ball)

        rack_origin = pygame.Vector2(self.table_inner.right - 470, self.table_inner.centery)
        spacing = self.ball_radius * 2 + 2
        rack_colors = [
            (236, 68, 68),
            (65, 132, 255),
            (243, 178, 59),
            (160, 86, 228),
            (64, 193, 175),
            (240, 88, 138),
        ]

        number = 1
        row_count = 3
        for row in range(row_count):
            for col in range(row + 1):
                x = rack_origin.x + row * spacing * 0.9
                y = rack_origin.y + (col - row * 0.5) * spacing
                color = rack_colors[(number - 1) % len(rack_colors)]
                self.balls.append(self._make_ball(f"target-{number}", pygame.Vector2(x, y), color, number))
                number += 1

        self.game_over = False
        self.dragging = False

    def _any_ball_moving(self) -> bool:
        for ball in self.balls:
            if ball.alive and ball.vel.length_squared() > 4:
                return True
        return False

    def _integrate(self, dt: float):
        active_balls = [b for b in self.balls if b.alive]

        for ball in active_balls:
            ball.pos += ball.vel * dt
            ball.vel *= self.friction
            if ball.vel.length() < self.min_speed:
                ball.vel.update(0, 0)
            self._solve_wall_collision(ball)

        for i in range(len(active_balls)):
            for j in range(i + 1, len(active_balls)):
                self._solve_ball_collision(active_balls[i], active_balls[j])

        self._check_pockets()

    def _solve_wall_collision(self, ball: BilliardBall):
        left = self.table_inner.left + ball.radius
        right = self.table_inner.right - ball.radius
        top = self.table_inner.top + ball.radius
        bottom = self.table_inner.bottom - ball.radius

        if ball.pos.x < left:
            ball.pos.x = left
            ball.vel.x *= -self.cushion_restitution
        elif ball.pos.x > right:
            ball.pos.x = right
            ball.vel.x *= -self.cushion_restitution

        if ball.pos.y < top:
            ball.pos.y = top
            ball.vel.y *= -self.cushion_restitution
        elif ball.pos.y > bottom:
            ball.pos.y = bottom
            ball.vel.y *= -self.cushion_restitution

    def _solve_ball_collision(self, a: BilliardBall, b: BilliardBall):
        delta = b.pos - a.pos
        min_distance = a.radius + b.radius
        dist_sq = delta.length_squared()

        if dist_sq >= min_distance * min_distance:
            return

        distance = math.sqrt(max(dist_sq, 0.0001))
        normal = delta / distance if distance > 0 else pygame.Vector2(1, 0)
        penetration = min_distance - distance

        a.pos -= normal * (penetration * 0.5)
        b.pos += normal * (penetration * 0.5)

        relative_velocity = b.vel - a.vel
        separating_speed = relative_velocity.dot(normal)
        if separating_speed > 0:
            return

        impulse_size = -(1 + self.ball_restitution) * separating_speed
        impulse_size /= (1 / a.mass) + (1 / b.mass)
        impulse = normal * impulse_size

        a.vel -= impulse / a.mass
        b.vel += impulse / b.mass

    def _check_pockets(self):
        for ball in self.balls:
            if not ball.alive:
                continue
            for pocket_pos, pocket_r, _ in self.pockets:
                if ball.pos.distance_to(pocket_pos) <= pocket_r - 4:
                    if ball.is_cue:
                        ball.pos = pygame.Vector2(self.table_inner.left + 370, self.table_inner.centery)
                        ball.vel.update(0, 0)
                    else:
                        ball.alive = False
                        ball.vel.update(0, 0)
                        self.pocketed_count += 1
                    break

        target_alive = [b for b in self.balls if (not b.is_cue) and b.alive]
        if not target_alive:
            self.game_over = True

    def _shoot_from_drag(self):
        if self.game_over:
            return
        drag_vector = self.drag_start - self.drag_now
        if drag_vector.length_squared() < 4:
            return

        strength = min(drag_vector.length() * 9.0, self.max_shot_power)
        direction = drag_vector.normalize()
        self.cue_ball.vel += direction * strength

    def _set_power_ratio(self, ratio: float):
        ratio = max(0.0, min(1.0, ratio))
        if abs(self.power_ratio - ratio) < 1e-5:
            return
        self.power_ratio = ratio
        if ratio <= 0:
            self.power_bar_fill.alpha = 0
            return

        self.power_bar_fill.alpha = 255
        width = max(8, int(452 * ratio))
        self.power_bar_fill = rectObj(pygame.Rect(84, 1364, width, 18), color=(250, 208, 74), edge=0, radius=6)

    def update(self):
        if Rs.userJustPressed(pygame.K_r):
            self._reset_rack()

        mouse = pygame.Vector2(Rs.mousePos().toTuple())
        balls_moving = self._any_ball_moving()

        if not balls_moving and not self.game_over:
            if Rs.userJustLeftClicked():
                if mouse.distance_to(self.cue_ball.pos) < 180:
                    self.dragging = True
                    self.drag_start = pygame.Vector2(self.cue_ball.pos)
                    self.drag_now = pygame.Vector2(mouse)

            if self.dragging and Rs.userIsLeftClicking():
                self.drag_now = pygame.Vector2(mouse)

            if self.dragging and Rs.userJustReleasedMouseLeft():
                self.drag_now = pygame.Vector2(mouse)
                self._shoot_from_drag()
                self.dragging = False

        dt = self.fixed_dt / self.substeps
        for _ in range(self.substeps):
            self._integrate(dt)

        remaining = len([b for b in self.balls if (not b.is_cue) and b.alive])
        if self.game_over:
            self.state_text.text = "클리어! R 키로 다시 플레이하세요."
        elif balls_moving:
            self.state_text.text = f"진행중... 남은 공 {remaining}개"
        else:
            self.state_text.text = f"조준 가능 | 포켓 성공 {self.pocketed_count}개 | 남은 공 {remaining}개"

        if self.dragging:
            pull = min((self.drag_start - self.drag_now).length(), self.max_shot_power / 5.0)
            self._set_power_ratio(pull / (self.max_shot_power / 5.0))
        else:
            self._set_power_ratio(0.0)

    def draw(self):
        Rs.fillScreen((18, 21, 26))
        self.outer_frame.draw()
        self.inner_shadow.draw()
        self.table_felt.draw()

        for _, _, pocket_vis in self.pockets:
            pocket_vis.draw()

        for ball in self.balls:
            if not ball.alive:
                continue

            center = RPoint(int(ball.pos.x), int(ball.pos.y))
            if ball.shadow:
                ball.shadow.center = center + RPoint(2, 3)
                ball.shadow.draw()
            if ball.visual:
                ball.visual.center = center
                ball.visual.draw()
            if ball.number_label and not ball.is_cue:
                ball.number_label.center = center
                ball.number_label.draw()

        can_aim = (not self._any_ball_moving()) and (not self.game_over)
        if can_aim:
            mouse = pygame.Vector2(Rs.mousePos().toTuple())
            direction = self.cue_ball.pos - mouse
            if direction.length_squared() > 1:
                length = min(direction.length(), 260)
                line_dir = direction.normalize()
                line_end = self.cue_ball.pos - line_dir * length
                Rs.render_engine.render_thick_line(
                    Rs.source_layer,
                    (240, 240, 240, 230),
                    (self.cue_ball.pos.x, self.cue_ball.pos.y),
                    (line_end.x, line_end.y),
                    8,
                    capped=True,
                    antialias=True,
                )

        self.power_bar_bg.draw()
        self.power_bar_fill.draw()
        self.title.draw()
        self.guide.draw()
        self.state_text.draw()


class Scenes:
    mainScene = BilliardsScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1600, 900),
        screen_size=(2560, 1440),
        fullscreen=False,
        caption="51-REMO Billiards",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
