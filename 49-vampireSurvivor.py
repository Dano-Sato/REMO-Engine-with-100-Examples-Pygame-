from __future__ import annotations

import math
import random

import pygame

from REMOLib import *


class UpgradeButton(rectObj):
    def __init__(self, title: str, body: str, on_click):
        super().__init__(pygame.Rect(0, 0, 340, 150), color=Cs.dark(Cs.indigo), edge=3, radius=16)
        self._base = Cs.dark(Cs.indigo)
        self._hover = Cs.light(self._base)
        self._on_click = on_click
        self.title = textObj(title, size=28, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.pos = RPoint(16, 14)
        self.body = longTextObj(body, pos=RPoint(16, 56), size=19, color=Cs.white, textWidth=306)
        self.body.setParent(self, depth=1)

    def set_upgrade(self, title: str, body: str, on_click):
        self.title.text = title
        self.body.text = body
        self._on_click = on_click

    def update(self):
        hovered = self.collideMouse()
        self.color = self._hover if hovered else self._base
        if hovered and Rs.userJustLeftClicked():
            self._on_click()


class SurvivorScene(Scene):
    def initOnce(self):
        self.random = random.Random()
        self._reset_all()

    def _reset_all(self):
        self.player = rectObj(pygame.Rect(0, 0, 30, 30), color=Cs.tiffanyBlue, edge=2)
        self.player.center = Rs.screenRect().center

        self.player_speed = 6.0
        self.player_max_hp = 8
        self.player_hp = self.player_max_hp
        self.player_damage = 1
        self.player_attack_cooldown = 24
        self.player_range = 420
        self.player_pickup_range = 70
        self.player_regen_rate = 0.0
        self.regen_meter = 0.0

        self.attack_timer = 0
        self.hit_cooldown = 0
        self.frame_count = 0

        self.enemies: list[dict] = []
        self.projectiles: list[dict] = []
        self.gems: list[dict] = []

        self.spawn_delay = 45
        self.spawn_meter = 0
        self.enemy_speed_bonus = 0.0
        self.enemy_hp_bonus = 0

        self.xp = 0
        self.level = 1
        self.need_xp = 8
        self.kill_count = 0

        self.paused_for_levelup = False
        self.game_over = False

        self.title = textObj("REMO Survivors", size=42, color=Cs.white)
        self.title.pos = RPoint(24, 18)

        self.info = textObj("", size=23, color=Cs.white)
        self.info.pos = RPoint(24, 74)

        self.tip = textObj("WASD/화살표 이동 · 자동 공격 · 레벨업 시 업그레이드 선택", size=20, color=Cs.white)
        self.tip.pos = RPoint(24, 108)

        self.levelup_panel = rectObj(pygame.Rect(0, 0, 1110, 250), color=Cs.dark(Cs.black), edge=3, radius=18)
        self.levelup_panel.center = RPoint(Rs.screenRect().centerx, Rs.screenRect().centery + 40)
        self.levelup_title = textObj("레벨 업! 업그레이드를 선택하세요", size=34, color=Cs.gold)
        self.levelup_title.setParent(self.levelup_panel, depth=1)
        self.levelup_title.pos = RPoint(24, 18)

        self.upgrade_buttons = [UpgradeButton("", "", lambda: None) for _ in range(3)]
        x_base = self.levelup_panel.x + 24
        y_base = self.levelup_panel.y + 80
        for i, button in enumerate(self.upgrade_buttons):
            button.pos = RPoint(x_base + 360 * i, y_base)

        self.gameover_panel = rectObj(pygame.Rect(0, 0, 680, 280), color=Cs.dark(Cs.black), edge=3, radius=16)
        self.gameover_panel.center = Rs.screenRect().center
        self.gameover_title = textObj("생존 실패", size=44, color=Cs.crimson)
        self.gameover_title.setParent(self.gameover_panel, depth=1)
        self.gameover_title.centerx = self.gameover_panel.offsetRect.centerx
        self.gameover_title.y = 26
        self.gameover_info = longTextObj("", pos=RPoint(36, 100), size=27, color=Cs.white, textWidth=610)
        self.gameover_info.setParent(self.gameover_panel, depth=1)

        self.restart_button = UpgradeButton("다시 시작", "클릭하면 처음부터 다시 도전합니다.", self._reset_all)
        self.restart_button.pos = RPoint(self.gameover_panel.x + 170, self.gameover_panel.y + 190)
        self.restart_button.rect.width = 340
        self.restart_button.rect.height = 74

        self.emitter = ParticleEmitter(RPoint(0, 0), max_particles=300, defaults=particleDefaultPreset.explosion_fireball())

    def init(self):
        return

    def _spawn_enemy(self):
        side = self.random.choice(["top", "bottom", "left", "right"])
        size = self.random.randint(18, 34)
        rect = pygame.Rect(0, 0, size, size)
        scr = Rs.screenRect()

        if side == "top":
            x = self.random.randint(0, scr.width)
            y = -size - 8
        elif side == "bottom":
            x = self.random.randint(0, scr.width)
            y = scr.height + 8
        elif side == "left":
            x = -size - 8
            y = self.random.randint(0, scr.height)
        else:
            x = scr.width + 8
            y = self.random.randint(0, scr.height)

        elite = self.random.random() < min(0.45, 0.06 + self.frame_count / 7200)
        hp = 2 + self.enemy_hp_bonus + (2 if elite else 0)
        speed = 1.6 + self.enemy_speed_bonus + (0.6 if elite else 0)

        enemy = {
            "obj": rectObj(rect, color=Cs.dark(Cs.crimson) if elite else Cs.crimson, edge=2),
            "hp": hp,
            "speed": speed,
            "elite": elite,
        }
        enemy["obj"].pos = RPoint(x, y)
        self.enemies.append(enemy)

    def _spawn_gem(self, pos: RPoint, amount: int):
        gem = rectObj(pygame.Rect(0, 0, 12, 12), color=Cs.cyan, radius=4)
        gem.center = pos
        self.gems.append({"obj": gem, "xp": amount})

    def _attack_nearest(self):
        if not self.enemies:
            return
        px, py = self.player.center.toTuple()
        target = None
        best_dist = self.player_range

        for enemy in self.enemies:
            ex, ey = enemy["obj"].center.toTuple()
            dist = math.hypot(ex - px, ey - py)
            if dist < best_dist:
                best_dist = dist
                target = enemy

        if target is None:
            return

        ex, ey = target["obj"].center.toTuple()
        dx, dy = ex - px, ey - py
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        vx = dx / dist * 11
        vy = dy / dist * 11
        bullet = rectObj(pygame.Rect(0, 0, 10, 10), color=Cs.gold, radius=4)
        bullet.center = self.player.center
        self.projectiles.append({"obj": bullet, "vel": (vx, vy), "life": 80})

    def _apply_upgrade(self, upgrade_type: str):
        if upgrade_type == "damage":
            self.player_damage += 1
        elif upgrade_type == "attack_speed":
            self.player_attack_cooldown = max(8, self.player_attack_cooldown - 3)
        elif upgrade_type == "movespeed":
            self.player_speed += 0.9
        elif upgrade_type == "range":
            self.player_range += 55
        elif upgrade_type == "pickup":
            self.player_pickup_range += 30
        elif upgrade_type == "regen":
            self.player_regen_rate += 0.03
        self.paused_for_levelup = False

    def _show_levelup_choices(self):
        choices = [
            ("공격력 강화", "+1 피해량", "damage"),
            ("연사 강화", "공격 간격 감소", "attack_speed"),
            ("이동 강화", "이동 속도 증가", "movespeed"),
            ("사거리 강화", "자동 공격 사거리 증가", "range"),
            ("자석 오라", "보석 흡수 반경 증가", "pickup"),
            ("재생 인자", "지속적으로 체력 회복", "regen"),
        ]
        picks = self.random.sample(choices, 3)
        for button, (title, body, key) in zip(self.upgrade_buttons, picks):
            button.set_upgrade(title, body, lambda kind=key: self._apply_upgrade(kind))

    def _gain_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.need_xp:
            self.xp -= self.need_xp
            self.level += 1
            self.need_xp = int(self.need_xp * 1.32) + 2
            self.paused_for_levelup = True
            self._show_levelup_choices()

    def _update_player(self):
        vel = RPoint(0, 0)
        if Rs.userPressing(pygame.K_LEFT) or Rs.userPressing(pygame.K_a):
            vel += RPoint(-1, 0)
        if Rs.userPressing(pygame.K_RIGHT) or Rs.userPressing(pygame.K_d):
            vel += RPoint(1, 0)
        if Rs.userPressing(pygame.K_UP) or Rs.userPressing(pygame.K_w):
            vel += RPoint(0, -1)
        if Rs.userPressing(pygame.K_DOWN) or Rs.userPressing(pygame.K_s):
            vel += RPoint(0, 1)

        if vel != RPoint(0, 0):
            length = math.hypot(vel.x, vel.y)
            self.player.pos += RPoint(vel.x / length * self.player_speed, vel.y / length * self.player_speed)

        scr = Rs.screenRect()
        self.player.x = max(0, min(scr.width - self.player.rect.w, self.player.x))
        self.player.y = max(0, min(scr.height - self.player.rect.h, self.player.y))

    def _update_enemies(self):
        px, py = self.player.center.toTuple()
        for enemy in list(self.enemies):
            ex, ey = enemy["obj"].center.toTuple()
            dx, dy = px - ex, py - ey
            dist = math.hypot(dx, dy)
            if dist > 0:
                enemy["obj"].pos += RPoint(dx / dist * enemy["speed"], dy / dist * enemy["speed"])

            if enemy["obj"].geometry.colliderect(self.player.geometry) and self.hit_cooldown <= 0:
                self.player_hp -= 1
                self.hit_cooldown = 30
                self.emitter.emit(20, position=self.player.center)
                if self.player_hp <= 0:
                    self.game_over = True

    def _update_projectiles(self):
        for bullet in list(self.projectiles):
            vx, vy = bullet["vel"]
            bullet["obj"].pos += RPoint(vx, vy)
            bullet["life"] -= 1

            hit_enemy = None
            for enemy in self.enemies:
                if bullet["obj"].geometry.colliderect(enemy["obj"].geometry):
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                hit_enemy["hp"] -= self.player_damage
                if hit_enemy["hp"] <= 0:
                    self.enemies.remove(hit_enemy)
                    self.kill_count += 1
                    gem_xp = 2 if hit_enemy["elite"] else 1
                    self._spawn_gem(hit_enemy["obj"].center, gem_xp)
                    self.emitter.emit(12, position=hit_enemy["obj"].center)
                if bullet in self.projectiles:
                    self.projectiles.remove(bullet)
                continue

            if bullet["life"] <= 0:
                self.projectiles.remove(bullet)

    def _update_gems(self):
        for gem in list(self.gems):
            gx, gy = gem["obj"].center.toTuple()
            px, py = self.player.center.toTuple()
            dx, dy = px - gx, py - gy
            dist = math.hypot(dx, dy)

            if dist < self.player_pickup_range and dist > 0:
                speed = 5 + (self.player_pickup_range - dist) * 0.12
                gem["obj"].pos += RPoint(dx / dist * speed, dy / dist * speed)

            if gem["obj"].geometry.colliderect(self.player.geometry):
                self._gain_xp(gem["xp"])
                self.gems.remove(gem)

    def _update_difficulty(self):
        if self.frame_count % 240 == 0:
            self.enemy_speed_bonus += 0.08
            self.enemy_hp_bonus += 1 if self.level >= 7 and self.frame_count % 480 == 0 else 0
            self.spawn_delay = max(10, self.spawn_delay - 1)

    def update(self):
        if self.game_over:
            self.restart_button.update()
            return

        if self.paused_for_levelup:
            for button in self.upgrade_buttons:
                button.update()
            return

        self.frame_count += 1
        self.spawn_meter += 1
        self.attack_timer += 1

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        self.regen_meter += self.player_regen_rate
        if self.regen_meter >= 1:
            healed = int(self.regen_meter)
            self.regen_meter -= healed
            self.player_hp = min(self.player_max_hp, self.player_hp + healed)

        self._update_player()

        if self.spawn_meter >= self.spawn_delay:
            self.spawn_meter = 0
            self._spawn_enemy()

        if self.attack_timer >= self.player_attack_cooldown:
            self.attack_timer = 0
            self._attack_nearest()

        self._update_enemies()
        self._update_projectiles()
        self._update_gems()
        self._update_difficulty()
        self.emitter.update()

        sec = self.frame_count // 60
        self.info.text = (
            f"HP {self.player_hp}/{self.player_max_hp}   LV {self.level}   XP {self.xp}/{self.need_xp}   "
            f"처치 {self.kill_count}   생존 {sec//60:02d}:{sec%60:02d}"
        )

    def _draw_background(self):
        Rs.fillScreen(Cs.dark(Cs.midnightblue))
        scr = Rs.screenRect()
        gap = 48
        for x in range(0, scr.width, gap):
            pygame.draw.line(Rs.screen, Cs.dark(Cs.slateblue), (x, 0), (x, scr.height), 1)
        for y in range(0, scr.height, gap):
            pygame.draw.line(Rs.screen, Cs.dark(Cs.slateblue), (0, y), (scr.width, y), 1)

    def draw(self):
        self._draw_background()

        self.title.draw()
        self.info.draw()
        self.tip.draw()

        for gem in self.gems:
            gem["obj"].draw()
        for bullet in self.projectiles:
            bullet["obj"].draw()
        for enemy in self.enemies:
            enemy["obj"].draw()

        if self.hit_cooldown > 0 and self.hit_cooldown % 6 < 3:
            blink = rectObj(self.player.rect, color=Cs.white)
            blink.pos = self.player.pos
            blink.draw()
        else:
            self.player.draw()

        self.emitter.draw()

        if self.paused_for_levelup:
            self.levelup_panel.draw()
            for button in self.upgrade_buttons:
                button.draw()

        if self.game_over:
            sec = self.frame_count // 60
            self.gameover_info.text = (
                f"생존 시간: {sec//60:02d}:{sec%60:02d}\n"
                f"최종 레벨: {self.level}\n"
                f"처치 수: {self.kill_count}"
            )
            self.gameover_panel.draw()
            self.restart_button.draw()


class Scenes:
    game = SurvivorScene()


if __name__ == "__main__":
    game = REMOGame(window_resolution=(1280, 960), screen_size=(1280, 960), fullscreen=False, caption="REMO Survivors")
    game.setCurrentScene(Scenes.game)
    game.run()
