from __future__ import annotations

import math
import random

import pygame

from REMOLib import *


class BuildButton(rectObj):
    def __init__(self, text: str, cost: int, hotkey: str, on_click):
        super().__init__(pygame.Rect(0, 0, 260, 72), color=Cs.dark(Cs.indigo), edge=2, radius=12)
        self._base_color = Cs.dark(Cs.indigo)
        self._hover_color = Cs.indigo
        self._on_click = on_click
        self.cost = cost
        self.hotkey = hotkey

        self.title = textObj(text, size=25, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.pos = RPoint(16, 10)

        self.detail = textObj(f"{cost}G · [{hotkey}]", size=20, color=Cs.gold)
        self.detail.setParent(self, depth=1)
        self.detail.pos = RPoint(16, 40)

    def update(self):
        hovered = self.collideMouse()
        self.color = self._hover_color if hovered else self._base_color
        if hovered and Rs.userJustLeftClicked():
            self._on_click()


class TowerDefenseScene(Scene):
    def initOnce(self):
        self.random = random.Random()

        self.tile_size = 72
        self.grid_cols = 12
        self.grid_rows = 8
        self.grid_origin = RPoint(60, 150)

        self.path_cells = [
            (0, 3), (1, 3), (2, 3), (3, 3),
            (3, 4), (3, 5),
            (4, 5), (5, 5), (6, 5),
            (6, 4), (6, 3),
            (7, 3), (8, 3), (9, 3), (10, 3), (11, 3),
        ]
        self.path_cell_set = set(self.path_cells)

        self.start_cell = self.path_cells[0]
        self.goal_cell = self.path_cells[-1]

        self.tile_nodes: dict[tuple[int, int], rectObj] = {}
        self._create_map_tiles()

        self.title = textObj("REMO Tower Defense", size=44, color=Cs.white)
        self.title.pos = RPoint(56, 24)

        self.info = textObj("", size=26, color=Cs.white)
        self.info.pos = RPoint(56, 84)

        self.guide = textObj("타일 클릭으로 설치 · Space로 웨이브 호출 · R로 재시작", size=22, color=Cs.white)
        self.guide.pos = RPoint(560, 36)

        self.buttons = [
            BuildButton("기본 포탑", 70, "1", lambda: self._set_build_mode("basic")),
            BuildButton("스나이퍼", 110, "2", lambda: self._set_build_mode("sniper")),
            BuildButton("슬로우 타워", 90, "3", lambda: self._set_build_mode("slow")),
        ]
        for idx, button in enumerate(self.buttons):
            button.pos = RPoint(980, 190 + idx * 92)

        self._reset_state()

    def _reset_state(self):
        self.hp = 20
        self.gold = 180
        self.wave = 0
        self.kills = 0

        self.towers: list[dict] = []
        self.enemies: list[dict] = []
        self.projectiles: list[dict] = []

        self.wave_active = False
        self.wave_spawn_count = 0
        self.wave_spawned = 0
        self.wave_spawn_interval = 28
        self.wave_spawn_timer = 0

        self.selected_tower = "basic"
        self.fast_forward = 1
        self.game_over = False
        self.victory = False

        self.banner = textObj("[1] 기본 포탑 선택", size=26, color=Cs.gold)
        self.banner.pos = RPoint(980, 480)

        self.result_panel = rectObj(pygame.Rect(0, 0, 640, 260), color=Cs.dark(Cs.black), edge=3, radius=16)
        self.result_panel.center = Rs.screenRect().center
        self.result_title = textObj("", size=44, color=Cs.white)
        self.result_title.setParent(self.result_panel, depth=1)
        self.result_title.pos = RPoint(34, 24)
        self.result_body = longTextObj("", pos=RPoint(34, 100), size=30, color=Cs.white, textWidth=580)
        self.result_body.setParent(self.result_panel, depth=1)

    def init(self):
        return

    def _create_map_tiles(self):
        for gy in range(self.grid_rows):
            for gx in range(self.grid_cols):
                rect = pygame.Rect(0, 0, self.tile_size - 2, self.tile_size - 2)
                if (gx, gy) in self.path_cell_set:
                    color = Cs.brown
                else:
                    color = Cs.dark(Cs.green)
                tile = rectObj(rect, color=color, edge=1, radius=8)
                tile.pos = self._cell_to_pos((gx, gy))
                self.tile_nodes[(gx, gy)] = tile

    def _cell_to_pos(self, cell: tuple[int, int]) -> RPoint:
        gx, gy = cell
        return RPoint(
            self.grid_origin.x + gx * self.tile_size,
            self.grid_origin.y + gy * self.tile_size,
        )

    def _cell_center(self, cell: tuple[int, int]) -> RPoint:
        return self._cell_to_pos(cell) + RPoint((self.tile_size - 2) // 2, (self.tile_size - 2) // 2)

    def _set_build_mode(self, tower_type: str):
        self.selected_tower = tower_type
        names = {"basic": "기본 포탑", "sniper": "스나이퍼", "slow": "슬로우 타워"}
        self.banner.text = f"[{tower_type[0].upper()}] {names[tower_type]} 선택"

    def _tower_template(self, tower_type: str):
        if tower_type == "basic":
            return {"cost": 70, "range": 150, "cooldown": 34, "damage": 2, "color": Cs.cyan, "slow": 0.0}
        if tower_type == "sniper":
            return {"cost": 110, "range": 270, "cooldown": 68, "damage": 6, "color": Cs.gold, "slow": 0.0}
        return {"cost": 90, "range": 130, "cooldown": 42, "damage": 1, "color": Cs.tiffanyBlue, "slow": 0.45}

    def _tower_exists(self, cell: tuple[int, int]) -> bool:
        return any(tower["cell"] == cell for tower in self.towers)

    def _try_place_tower(self, cell: tuple[int, int]):
        if cell in self.path_cell_set:
            self.banner.text = "길 위에는 설치할 수 없습니다."
            return
        if self._tower_exists(cell):
            self.banner.text = "이미 포탑이 있습니다."
            return

        template = self._tower_template(self.selected_tower)
        if self.gold < template["cost"]:
            self.banner.text = "골드가 부족합니다."
            return

        self.gold -= template["cost"]
        tower_obj = rectObj(pygame.Rect(0, 0, 40, 40), color=template["color"], edge=2, radius=8)
        tower_obj.center = self._cell_center(cell)

        tower = {
            "cell": cell,
            "obj": tower_obj,
            "range": template["range"],
            "cooldown": template["cooldown"],
            "cooldown_left": self.random.randint(0, template["cooldown"] // 2),
            "damage": template["damage"],
            "slow": template["slow"],
            "tower_type": self.selected_tower,
        }
        self.towers.append(tower)
        self.banner.text = "포탑 설치 완료!"

    def _start_wave(self):
        if self.wave_active or self.game_over:
            return
        self.wave += 1
        self.wave_active = True
        self.wave_spawn_count = 6 + self.wave * 3
        self.wave_spawned = 0
        self.wave_spawn_timer = 0
        self.banner.text = f"웨이브 {self.wave} 시작!"

    def _spawn_enemy(self):
        base_hp = 8 + self.wave * 3
        enemy_size = 30
        body = rectObj(pygame.Rect(0, 0, enemy_size, enemy_size), color=Cs.crimson, edge=2, radius=8)
        body.center = self._cell_center(self.start_cell)
        enemy = {
            "obj": body,
            "hp": base_hp,
            "max_hp": base_hp,
            "speed": 1.1 + self.wave * 0.07,
            "path_index": 0,
            "slow_timer": 0,
            "slow_factor": 1.0,
            "reward": 12 + self.wave,
            "damage": 1 if self.wave < 5 else 2,
        }
        self.enemies.append(enemy)

    def _update_wave(self):
        if not self.wave_active:
            return

        self.wave_spawn_timer += 1
        if self.wave_spawned < self.wave_spawn_count and self.wave_spawn_timer >= self.wave_spawn_interval:
            self.wave_spawn_timer = 0
            self.wave_spawned += 1
            self._spawn_enemy()

        if self.wave_spawned >= self.wave_spawn_count and not self.enemies:
            self.wave_active = False
            self.gold += 25 + self.wave * 4
            self.banner.text = f"웨이브 {self.wave} 클리어! 보너스 지급"
            if self.wave >= 12:
                self.victory = True
                self.game_over = True

    def _update_enemies(self):
        for enemy in list(self.enemies):
            if enemy["slow_timer"] > 0:
                enemy["slow_timer"] -= 1
            else:
                enemy["slow_factor"] = 1.0

            if enemy["path_index"] >= len(self.path_cells) - 1:
                self.hp -= enemy["damage"]
                self.enemies.remove(enemy)
                if self.hp <= 0:
                    self.hp = 0
                    self.game_over = True
                continue

            next_center = self._cell_center(self.path_cells[enemy["path_index"] + 1])
            ex, ey = enemy["obj"].center.toTuple()
            tx, ty = next_center.toTuple()
            dx, dy = tx - ex, ty - ey
            dist = math.hypot(dx, dy)

            speed = enemy["speed"] * enemy["slow_factor"] * self.fast_forward
            if dist <= speed:
                enemy["obj"].center = next_center
                enemy["path_index"] += 1
            elif dist > 0:
                enemy["obj"].pos += RPoint(dx / dist * speed, dy / dist * speed)

    def _create_projectile(self, tower: dict, target: dict):
        shot = rectObj(pygame.Rect(0, 0, 12, 12), color=Cs.white, radius=4)
        shot.center = tower["obj"].center
        self.projectiles.append(
            {
                "obj": shot,
                "target": target,
                "damage": tower["damage"],
                "speed": 8 + self.fast_forward,
                "slow": tower["slow"],
                "life": 75,
            }
        )

    def _update_towers(self):
        for tower in self.towers:
            if tower["cooldown_left"] > 0:
                tower["cooldown_left"] -= self.fast_forward
                continue

            target = None
            tx, ty = tower["obj"].center.toTuple()
            best_dist = tower["range"]
            for enemy in self.enemies:
                ex, ey = enemy["obj"].center.toTuple()
                dist = math.hypot(ex - tx, ey - ty)
                if dist <= best_dist:
                    best_dist = dist
                    target = enemy

            if target is not None:
                self._create_projectile(tower, target)
                tower["cooldown_left"] = tower["cooldown"]

    def _update_projectiles(self):
        for bullet in list(self.projectiles):
            bullet["life"] -= 1
            target = bullet["target"]

            if target not in self.enemies:
                self.projectiles.remove(bullet)
                continue

            bx, by = bullet["obj"].center.toTuple()
            tx, ty = target["obj"].center.toTuple()
            dx, dy = tx - bx, ty - by
            dist = math.hypot(dx, dy)

            if dist <= bullet["speed"] or bullet["obj"].geometry.colliderect(target["obj"].geometry):
                target["hp"] -= bullet["damage"]
                if bullet["slow"] > 0:
                    target["slow_factor"] = max(0.4, 1.0 - bullet["slow"])
                    target["slow_timer"] = 70

                if target["hp"] <= 0:
                    self.gold += target["reward"]
                    self.kills += 1
                    self.enemies.remove(target)

                self.projectiles.remove(bullet)
                continue

            if dist > 0:
                bullet["obj"].pos += RPoint(dx / dist * bullet["speed"], dy / dist * bullet["speed"])

            if bullet["life"] <= 0 and bullet in self.projectiles:
                self.projectiles.remove(bullet)

    def _update_hotkeys(self):
        if Rs.userJustPressed(pygame.K_1):
            self._set_build_mode("basic")
        if Rs.userJustPressed(pygame.K_2):
            self._set_build_mode("sniper")
        if Rs.userJustPressed(pygame.K_3):
            self._set_build_mode("slow")
        if Rs.userJustPressed(pygame.K_SPACE):
            self._start_wave()
        if Rs.userJustPressed(pygame.K_f):
            self.fast_forward = 2 if self.fast_forward == 1 else 1
            self.banner.text = "배속 x2" if self.fast_forward == 2 else "배속 x1"
        if Rs.userJustPressed(pygame.K_r):
            self._reset_state()

    def _handle_map_click(self):
        if not Rs.userJustLeftClicked() or self.game_over:
            return

        for cell, tile in self.tile_nodes.items():
            if tile.collideMouse():
                self._try_place_tower(cell)
                return

    def update(self):
        self._update_hotkeys()

        for button in self.buttons:
            button.update()

        self._handle_map_click()

        if self.game_over:
            return

        for _ in range(self.fast_forward):
            self._update_wave()
            self._update_enemies()
            self._update_towers()
            self._update_projectiles()

        self.info.text = (
            f"HP {self.hp}   GOLD {self.gold}   WAVE {self.wave}   KILL {self.kills}   SPEED x{self.fast_forward}"
        )

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.midnightblue))

        for cell, tile in self.tile_nodes.items():
            if cell in self.path_cell_set:
                tile.color = Cs.brown
            else:
                tile.color = Cs.dark(Cs.green)
            tile.draw()

        goal = rectObj(pygame.Rect(0, 0, 62, 62), color=Cs.red, edge=3, radius=12)
        goal.center = self._cell_center(self.goal_cell)
        goal.draw()

        start = rectObj(pygame.Rect(0, 0, 62, 62), color=Cs.dark(Cs.cyan), edge=3, radius=12)
        start.center = self._cell_center(self.start_cell)
        start.draw()

        for tower in self.towers:
            tower["obj"].draw()

        for enemy in self.enemies:
            enemy["obj"].draw()

        for bullet in self.projectiles:
            bullet["obj"].draw()

        self.title.draw()
        self.info.draw()
        self.guide.draw()
        self.banner.draw()

        for button in self.buttons:
            button.draw()

        if self.game_over:
            self.result_title.text = "방어 성공!" if self.victory else "방어 실패"
            result_color = Cs.aquamarine if self.victory else Cs.crimson
            self.result_title.color = result_color
            self.result_body.text = (
                f"도달 웨이브: {self.wave}\n"
                f"처치한 적: {self.kills}\n"
                "R 키로 다시 시작"
            )
            self.result_panel.draw()


class Scenes:
    game = TowerDefenseScene()


if __name__ == "__main__":
    game = REMOGame(window_resolution=(1400, 860), screen_size=(1400, 860), fullscreen=False, caption="REMO Tower Defense")
    game.setCurrentScene(Scenes.game)
    game.run()
