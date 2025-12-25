from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass
import math
import random

import pygame

from REMOLib.core import *


@dataclass
class Unit:
    name: str
    symbol: str
    team: str
    color: tuple[int, int, int]
    hp: int
    max_hp: int
    attack: int = 0

    def take_damage(self, amount: int) -> int:
        self.hp = max(0, self.hp - amount)
        return self.hp


@dataclass
class CardData:
    name: str
    cost: int
    description: str
    color: tuple[int, int, int]
    target_mode: str
    effect: str
    damage: int = 0
    range: int = 1
    block: int = 0


class HexTile(graphicObj):
    HIGHLIGHT_COLORS: dict[str, tuple[int, int, int]] = {
        "selected": Cs.light(Cs.gold),
        "move": Cs.light(Cs.deepskyblue),
        "attack": Cs.light(Cs.firebrick),
        "range": Cs.light(Cs.mediumorchid),
    }

    def __init__(
        self,
        q: int,
        r: int,
        radius: int,
        *,
        terrain_name: str,
        terrain_color: tuple[int, int, int],
    ) -> None:
        width = int(math.sqrt(3) * radius)
        height = int(2 * radius)
        super().__init__(pygame.Rect(0, 0, width, height))
        self.q = q
        self.r = r
        self.radius = radius
        self.terrain_name = terrain_name
        self.terrain_color = terrain_color
        self.occupant: Unit | None = None
        self.highlight_type: str | None = None
        self._hovered = False
        self._needs_redraw = True
        self._points = self._compute_polygon_points(width, height)
        self._mask = pygame.mask.from_surface(self.graphic)

        self.label = textObj("", size=28, color=Cs.white)
        self.label.setParent(self, depth=1)
        self.label.center = self.offsetRect.center

        self.hp_text = textObj("", size=18, color=Cs.light(Cs.lightgoldenrodyellow))
        self.hp_text.setParent(self, depth=1)
        self.hp_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 10)

        self._redraw()

    def _compute_polygon_points(self, width: int, height: int) -> list[tuple[int, int]]:
        cx = width / 2
        cy = height / 2
        points: list[tuple[int, int]] = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = cx + self.radius * math.cos(angle)
            y = cy + self.radius * math.sin(angle)
            points.append((int(x), int(y)))
        return points

    def collidepoint(self, p) -> bool:  # type: ignore[override]
        if type(p)==RPoint:
            p = p.toTuple()
        if not super().collidepoint(p):
            return False
        local_x = int(p[0] - self.geometry.x)
        local_y = int(p[1] - self.geometry.y)
        if local_x < 0 or local_y < 0:
            return False
        if local_x >= self.graphic.get_width() or local_y >= self.graphic.get_height():
            return False
        return bool(self._mask.get_at((local_x, local_y)))

    def set_highlight(self, highlight: str | None) -> None:
        if self.highlight_type != highlight:
            self.highlight_type = highlight
            self._needs_redraw = True

    def set_occupant(self, unit: Unit | None) -> None:
        self.occupant = unit
        self._update_unit_labels()
        self._needs_redraw = True

    def _update_unit_labels(self) -> None:
        if self.occupant:
            self.label.text = self.occupant.symbol
            self.label.center = self.offsetRect.center
            self.label.alpha = 255
            self.hp_text.text = f"{self.occupant.hp}/{self.occupant.max_hp}"
            self.hp_text.alpha = 255
            self.hp_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 20)
            if self.occupant.team == "player":
                self.label.color = Cs.white
            else:
                self.label.color = Cs.light(Cs.yellow)
        else:
            self.label.text = ""
            self.label.alpha = 0
            self.hp_text.text = ""
            self.hp_text.alpha = 0

    def status_summary(self) -> str:
        lines = [f"{self.terrain_name} ({self.q:+d}, {self.r:+d})"]
        if self.occupant:
            team_label = "아군" if self.occupant.team == "player" else "적"
            lines.append(f"{team_label}: {self.occupant.name}")
            lines.append(f"체력 {self.occupant.hp}/{self.occupant.max_hp}")
        else:
            lines.append("점령자 없음")
        if self.highlight_type:
            info = {
                "selected": "현재 위치",
                "move": "이동 가능",
                "attack": "공격 대상",
                "range": "사거리 내 대상",
            }.get(self.highlight_type)
            if info:
                lines.append(info)
        return "\n".join(lines)

    def _redraw(self) -> None:
        surface = self.graphic_n
        surface.fill((0, 0, 0, 0))

        base_color = self.terrain_color
        if self._hovered:
            base_color = Cs.light(base_color)

        pygame.draw.polygon(surface, Cs.apply(base_color, 0.8), self._points)
        pygame.draw.polygon(surface, base_color, self._points, width=4)

        if self.highlight_type:
            highlight_color = self.HIGHLIGHT_COLORS.get(self.highlight_type, Cs.white)
            pygame.draw.polygon(surface, highlight_color, self._points, width=6)

        if self.occupant:
            center = (surface.get_width() // 2, surface.get_height() // 2)
            circle_radius = int(self.radius * 0.45)
            pygame.draw.circle(surface, Cs.apply(self.occupant.color, 0.8), center, circle_radius)
            pygame.draw.circle(surface, Cs.dark(self.occupant.color), center, circle_radius, width=3)

        self.graphic = surface
        self._mask = pygame.mask.from_surface(surface)
        self._needs_redraw = False

    def update(self) -> None:
        hovered = self.collideMouse()
        if hovered != self._hovered:
            self._hovered = hovered
            self._needs_redraw = True
        if self._needs_redraw:
            self._redraw()


class HexGrid:
    TERRAIN_TYPES = [
        ("채석 황무지", Cs.dark(Cs.sienna)),
        ("수정 분지", Cs.dark(Cs.darkcyan)),
        ("광활한 초원", Cs.dark(Cs.darkolivegreen)),
        ("균열 협곡", Cs.dark(Cs.firebrick)),
        ("풍화 구릉", Cs.dark(Cs.peru)),
    ]

    def __init__(self, radius: int, hex_radius: int, origin: RPoint) -> None:
        self.radius = radius
        self.hex_radius = hex_radius
        self.origin = origin
        self.tiles: dict[tuple[int, int], HexTile] = {}
        for q in range(-radius, radius + 1):
            for r in range(max(-radius, -q - radius), min(radius, -q + radius) + 1):
                terrain_name, terrain_color = random.choice(self.TERRAIN_TYPES)
                tile = HexTile(q, r, hex_radius, terrain_name=terrain_name, terrain_color=terrain_color)
                offset = self.axial_to_pixel(q, r)
                tile.center = (
                    int(self.origin.x + offset.x),
                    int(self.origin.y + offset.y),
                )
                self.tiles[(q, r)] = tile

    def axial_to_pixel(self, q: int, r: int) -> RPoint:
        size = self.hex_radius
        x = size * math.sqrt(3) * (q + r / 2)
        y = size * 1.5 * r
        return RPoint(x, y)

    def get_tile(self, coord: tuple[int, int]) -> HexTile | None:
        return self.tiles.get(coord)

    def neighbors(self, coord: tuple[int, int]) -> list[tuple[int, int]]:
        q, r = coord
        deltas = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        result: list[tuple[int, int]] = []
        for dq, dr in deltas:
            candidate = (q + dq, r + dr)
            if candidate in self.tiles:
                result.append(candidate)
        return result

    def clear_highlights(self) -> None:
        for tile in self.tiles.values():
            tile.set_highlight(None)

    def clear_units(self) -> None:
        for tile in self.tiles.values():
            tile.set_occupant(None)

    def update(self) -> None:
        for tile in self.tiles.values():
            tile.update()

    def draw(self) -> None:
        for tile in sorted(self.tiles.values(), key=lambda t: (t.r, t.q)):
            tile.draw()

    @staticmethod
    def distance(a: tuple[int, int], b: tuple[int, int]) -> int:
        aq, ar = a
        bq, br = b
        return int((abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) / 2)

    def tiles_in_range(self, center: tuple[int, int], radius: int) -> list[tuple[int, int]]:
        cq, cr = center
        coords: list[tuple[int, int]] = []
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                coord = (cq + dq, cr + dr)
                if coord in self.tiles:
                    coords.append(coord)
        return coords

    def tile_under_point(self, point: tuple[int, int]) -> HexTile | None:
        for tile in self.tiles.values():
            if tile.collidepoint(point):
                return tile
        return None


class ActionCard(rectObj):
    def __init__(self, card: CardData, on_select) -> None:
        super().__init__(pygame.Rect(0, 0, 210, 300), color=card.color, edge=6, radius=24)
        self.card_data = card
        self._on_select = on_select
        self.playable = True
        self._selected = False
        self._base_color = card.color
        self._hover_color = Cs.light(card.color)
        self._selected_color = Cs.light(self._hover_color)

        self.cost_badge = rectObj(pygame.Rect(0, 0, 58, 58), radius=20, edge=3, color=Cs.dark(Cs.black))
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 16)

        self.cost_text = textObj(str(card.cost), size=26, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.title_text = textObj(card.name, size=26, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 84)

        self.desc_text = longTextObj(
            card.description,
            pos=RPoint(0, 0),
            size=20,
            color=Cs.light(Cs.lightgoldenrodyellow),
            textWidth=self.rect.w - 40,
        )
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.title_text.rect.bottom + 12

    def set_playable(self, playable: bool) -> None:
        if self.playable == playable:
            return
        self.playable = playable
        alpha = 255 if playable else 150
        self.alpha = alpha
        self.cost_badge.alpha = alpha
        self.cost_text.alpha = alpha
        self.title_text.alpha = alpha
        self.desc_text.alpha = alpha

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self._update_color(force=True)

    def _update_color(self, *, force: bool = False) -> None:
        hovered = self.collideMouse()
        if self._selected:
            target = self._selected_color
        elif hovered and self.playable:
            target = self._hover_color
        else:
            target = self._base_color
        if force or self.color != target:
            self.color = target

    def update(self) -> bool:
        self._update_color()
        hovered = self.collideMouse()
        clicked = False
        if hovered and self.playable and Rs.userJustLeftClicked():
            self._on_select(self)
            clicked = True
        return clicked


class HexTacticsScene(Scene):
    HAND_SIZE = 4
    LOG_LIMIT = 7

    def initOnce(self) -> None:
        self.grid = HexGrid(radius=2, hex_radius=70, origin=RPoint(960, 470))
        self.hand_layout = cardLayout(RPoint(360, 820), spacing=20, maxWidth=1200, isVertical=False)
        self.card_panel = rectObj(
            pygame.Rect(0, 0, self.hand_layout.maxWidth, 260).inflate(60, 50),
            color=Cs.dark(Cs.darkslategray),
            edge=4,
            radius=28,
        )
        self.card_panel.setParent(self.hand_layout, depth=-1)

        self.end_turn_button = textButton(
            "턴 종료",
            pygame.Rect(0, 0, 200, 60),
            color=Cs.dark(Cs.steelblue),
            radius=18,
        )
        self.end_turn_button.pos = RPoint(1560, 830)
        self.end_turn_button.connect(self.end_player_turn)

        self.turn_text = textObj("", size=32, color=Cs.white)
        self.turn_text.topleft = RPoint(120, 60)

        self.energy_text = textObj("", size=28, color=Cs.light(Cs.cyan))
        self.energy_text.topleft = RPoint(120, 110)

        self.hp_text = textObj("", size=28, color=Cs.light(Cs.lightcoral))
        self.hp_text.topleft = RPoint(120, 150)

        self.block_text = textObj("", size=24, color=Cs.light(Cs.khaki))
        self.block_text.topleft = RPoint(120, 190)

        self.objective_text = textObj("", size=24, color=Cs.light(Cs.lightgoldenrodyellow))
        self.objective_text.topleft = RPoint(120, 230)

        self.log_panel = rectObj(
            pygame.Rect(0, 0, 420, 360),
            color=Cs.dark(Cs.midnightblue),
            edge=4,
            radius=26,
        )
        self.log_panel.topright = RPoint(1780, 120)
        self.log_text = longTextObj(
            "",
            pos=RPoint(24, 24),
            size=22,
            color=Cs.white,
            textWidth=self.log_panel.rect.w - 48,
        )
        self.log_text.setParent(self.log_panel, depth=1)

        self.hover_info_panel = rectObj(
            pygame.Rect(0, 0, 420, 260),
            color=Cs.dark(Cs.darkslategray),
            edge=4,
            radius=26,
        )
        self.hover_info_panel.topleft = RPoint(120, 320)
        self.hover_info_text = longTextObj(
            "",
            pos=RPoint(24, 24),
            size=22,
            color=Cs.light(Cs.lightgoldenrodyellow),
            textWidth=self.hover_info_panel.rect.w - 48,
        )
        self.hover_info_text.setParent(self.hover_info_panel, depth=1)

        self.overlay_panel = rectObj(
            pygame.Rect(0, 0, 620, 240),
            color=Cs.apply(Cs.black, 0.85),
            edge=4,
            radius=36,
        )
        self.overlay_panel.alpha = 225
        self.overlay_text = textObj("", size=48, color=Cs.white)
        self.overlay_text.setParent(self.overlay_panel, depth=1)
        self.overlay_text.center = self.overlay_panel.offsetRect.center
        self.overlay_hint = textObj("R 키로 다시 시작", size=28, color=Cs.light(Cs.lightgoldenrodyellow))
        self.overlay_hint.setParent(self.overlay_panel, depth=1)
        self.overlay_hint.midbottom = RPoint(self.overlay_panel.offsetRect.midbottom) - RPoint(0, 32)

        self.reset_game()

    def reset_game(self) -> None:
        self.turn = 0
        self.max_energy = 3
        self.energy = self.max_energy
        self.player_block = 0
        self.goal_turns = 8
        self.defeated_enemies = 0
        self.game_over = False
        self.victory = False
        self.selected_card: ActionCard | None = None
        self.available_targets: set[tuple[int, int]] = set()
        self.log_messages: list[str] = []

        self.grid.clear_units()

        self.player_unit = Unit(
            name="정찰대장",
            symbol="P",
            team="player",
            color=Cs.dark(Cs.deepskyblue),
            hp=12,
            max_hp=12,
            attack=2,
        )
        self.player_coord = (0, 0)
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile.set_occupant(self.player_unit)
            player_tile.set_highlight("selected")

        self.enemies: dict[tuple[int, int], Unit] = {}
        for coord in [(-2, 1), (2, -1), (0, 2)]:
            tile = self.grid.get_tile(coord)
            if tile:
                enemy = self._make_enemy()
                tile.set_occupant(enemy)
                self.enemies[coord] = enemy

        self.hand_cards: list[ActionCard] = []
        self.hand_layout.clearChilds()

        self.deck = self._build_deck()
        random.shuffle(self.deck)
        self.draw_pile = self.deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile: list[CardData] = []

        self.start_new_turn()
        self.log("정찰 분대가 새로운 구역을 수색합니다.")
        self.log("카드를 선택해 명령을 내리세요.")

    def _build_deck(self) -> list[CardData]:
        return [
            CardData(
                "전술 이동",
                cost=1,
                description="인접한 육각형으로 이동합니다.",
                color=Cs.dark(Cs.steelblue),
                target_mode="adjacent-empty",
                effect="move",
            ),
            CardData(
                "전술 이동",
                cost=1,
                description="인접한 육각형으로 이동합니다.",
                color=Cs.dark(Cs.steelblue),
                target_mode="adjacent-empty",
                effect="move",
            ),
            CardData(
                "근접 타격",
                cost=1,
                description="인접한 적에게 2 피해를 가합니다.",
                color=Cs.dark(Cs.firebrick),
                target_mode="adjacent-enemy",
                effect="strike",
                damage=2,
            ),
            CardData(
                "근접 타격",
                cost=1,
                description="인접한 적에게 2 피해를 가합니다.",
                color=Cs.dark(Cs.firebrick),
                target_mode="adjacent-enemy",
                effect="strike",
                damage=2,
            ),
            CardData(
                "화염 포격",
                cost=2,
                description="사거리 2의 적에게 3 피해.",
                color=Cs.dark(Cs.purple),
                target_mode="range-enemy",
                effect="fire",
                damage=3,
                range=2,
            ),
            CardData(
                "방어 진영",
                cost=1,
                description="방어도를 3 얻습니다.",
                color=Cs.dark(Cs.darkslategray),
                target_mode="self",
                effect="guard",
                block=3,
            ),
            CardData(
                "매복 사격",
                cost=2,
                description="사거리 3에서 적을 저격해 2 피해를 줍니다.",
                color=Cs.dark(Cs.darkgoldenrod),
                target_mode="range-enemy",
                effect="strike",
                damage=2,
                range=3,
            ),
            CardData(
                "재정비",
                cost=0,
                description="버린 패를 섞고 카드를 한 장 더 뽑습니다.",
                color=Cs.dark(Cs.teal),
                target_mode="instant",
                effect="refresh",
            ),
        ]

    def _make_enemy(self) -> Unit:
        names = ["급습 병", "척후병", "돌격수", "수호 병"]
        colors = [Cs.dark(Cs.tomato), Cs.dark(Cs.orange), Cs.dark(Cs.gold), Cs.dark(Cs.red)]
        hp = random.randint(3, 4)
        attack = random.randint(1, 3)
        return Unit(
            name=random.choice(names),
            symbol="E",
            team="enemy",
            color=random.choice(colors),
            hp=hp,
            max_hp=hp,
            attack=attack,
        )

    def start_new_turn(self) -> None:
        self.turn += 1
        self.energy = self.max_energy
        self.player_block = 0
        self.grid.clear_highlights()
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile.set_highlight("selected")
        self.selected_card = None
        self.available_targets.clear()
        self.draw_cards(self.HAND_SIZE - len(self.hand_cards))
        self.refresh_hand_playability()
        self.update_status_labels()
        self.log(f"{self.turn} 턴 시작: 에너지 {self.energy} 확보")

    def draw_cards(self, count: int) -> None:
        for _ in range(count):
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self.draw_pile = self.discard_pile
                random.shuffle(self.draw_pile)
                self.discard_pile = []
                self.log("버린 패를 섞어 새 덱을 구성했습니다.")
            card_data = self.draw_pile.pop()
            card = ActionCard(card_data, self.on_card_selected)
            card.setParent(self.hand_layout)
            self.hand_cards.append(card)
        self.hand_layout.adjustLayout()

    def on_card_selected(self, card: ActionCard) -> None:
        if self.game_over:
            return
        if not card.playable:
            self.log("에너지가 부족하거나 대상이 없습니다.")
            return
        if self.selected_card is card:
            self.cancel_selection()
            return
        if card.card_data.target_mode in {"self", "instant"}:
            self.execute_card(card, self.player_coord)
            return
        self.selected_card = card
        for other in self.hand_cards:
            other.set_selected(other is card)
        self.prepare_targets(card.card_data)

    def prepare_targets(self, card: CardData) -> None:
        self.available_targets.clear()
        self.grid.clear_highlights()
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile.set_highlight("selected")
        if card.target_mode == "adjacent-empty":
            for coord in self.grid.neighbors(self.player_coord):
                tile = self.grid.get_tile(coord)
                if tile and tile.occupant is None:
                    tile.set_highlight("move")
                    self.available_targets.add(coord)
        elif card.target_mode == "adjacent-enemy":
            for coord in self.grid.neighbors(self.player_coord):
                if coord in self.enemies:
                    tile = self.grid.get_tile(coord)
                    if tile:
                        tile.set_highlight("attack")
                        self.available_targets.add(coord)
        elif card.target_mode == "range-enemy":
            for coord in self.grid.tiles_in_range(self.player_coord, card.range):
                if coord in self.enemies:
                    tile = self.grid.get_tile(coord)
                    if tile:
                        tile.set_highlight("range")
                        self.available_targets.add(coord)

    def cancel_selection(self) -> None:
        if not self.selected_card:
            return
        self.selected_card.set_selected(False)
        self.selected_card = None
        self.available_targets.clear()
        self.grid.clear_highlights()
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile.set_highlight("selected")

    def execute_card(self, card_widget: ActionCard, target: tuple[int, int]) -> None:
        card = card_widget.card_data
        if card.cost > self.energy:
            self.log("에너지가 부족합니다.")
            return
        if (
            card.target_mode not in {"self", "instant"}
            and target not in self.available_targets
        ):
            self.log("대상이 올바르지 않습니다.")
            return

        if card.effect == "move":
            self.move_player(target)
        elif card.effect in {"strike", "fire"}:
            self.player_attack(target, damage=card.damage)
        elif card.effect == "guard":
            self.player_block += card.block
            self.log(f"방어도를 {card.block} 얻었습니다. (총 {self.player_block})")
        elif card.effect == "refresh":
            self.discard_pile.extend(self.draw_pile)
            self.draw_pile = []
            random.shuffle(self.discard_pile)
            self.log("분대가 재정비합니다. 카드를 1장 보충합니다.")
            self.draw_cards(1)
        else:
            self.log("아직 구현되지 않은 카드입니다.")

        if card.effect != "refresh":
            self.energy -= card.cost
            self.log(f"{card.name} 사용 (-{card.cost} 에너지)")

        self.discard_card(card_widget)
        self.selected_card = None
        self.available_targets.clear()
        self.grid.clear_highlights()
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile.set_highlight("selected")

        self.refresh_hand_playability()
        self.update_status_labels()
        if self.energy < 0:
            self.energy = 0
        self.update_status_labels()

    def move_player(self, dest: tuple[int, int]) -> None:
        if dest == self.player_coord:
            return
        dest_tile = self.grid.get_tile(dest)
        current_tile = self.grid.get_tile(self.player_coord)
        if not dest_tile or dest_tile.occupant is not None:
            self.log("이동할 수 없습니다.")
            return
        if current_tile:
            current_tile.set_occupant(None)
        dest_tile.set_occupant(self.player_unit)
        self.player_coord = dest
        self.log(f"{self.player_unit.name}이(가) {dest} 위치로 이동.")

    def player_attack(self, coord: tuple[int, int], damage: int) -> None:
        enemy = self.enemies.get(coord)
        if not enemy:
            self.log("대상이 없습니다.")
            return
        remaining = enemy.take_damage(damage)
        tile = self.grid.get_tile(coord)
        if tile:
            tile._update_unit_labels()
        self.log(f"{enemy.name}에게 {damage} 피해 (남은 {remaining}).")
        if remaining <= 0:
            self.log(f"{enemy.name} 격파!")
            if tile:
                tile.set_occupant(None)
            self.enemies.pop(coord, None)
            self.defeated_enemies += 1

    def discard_card(self, card_widget: ActionCard) -> None:
        if card_widget in self.hand_cards:
            self.hand_cards.remove(card_widget)
        card_widget.setParent(None)
        self.discard_pile.append(card_widget.card_data)
        self.hand_layout.adjustLayout()

    def refresh_hand_playability(self) -> None:
        for card in self.hand_cards:
            playable = self.can_play_card(card.card_data)
            card.set_playable(playable)
            card.set_selected(False)
        if self.selected_card and not self.selected_card.playable:
            self.cancel_selection()

    def can_play_card(self, card: CardData) -> bool:
        if self.game_over or card.cost > self.energy:
            return False
        if card.target_mode in {"self", "instant"}:
            return True
        if card.target_mode == "adjacent-empty":
            return any(
                self.grid.get_tile(coord) and self.grid.get_tile(coord).occupant is None
                for coord in self.grid.neighbors(self.player_coord)
            )
        if card.target_mode == "adjacent-enemy":
            return any(coord in self.enemies for coord in self.grid.neighbors(self.player_coord))
        if card.target_mode == "range-enemy":
            return any(
                coord in self.enemies
                for coord in self.grid.tiles_in_range(self.player_coord, card.range)
            )
        return False

    def end_player_turn(self) -> None:
        if self.game_over:
            return
        if self.hand_cards:
            for card in list(self.hand_cards):
                self.discard_card(card)
        self.selected_card = None
        self.available_targets.clear()
        self.grid.clear_highlights()
        self.log("턴을 종료합니다.")
        self.enemy_phase()
        if not self.game_over:
            self.start_new_turn()

    def enemy_phase(self) -> None:
        self.log("적의 행동 단계")
        for coord, enemy in list(self.enemies.items()):
            tile = self.grid.get_tile(coord)
            if not tile:
                continue
            distance = self.grid.distance(coord, self.player_coord)
            if distance <= 1:
                self.enemy_attack(enemy)
                continue
            destination = self.choose_enemy_move(coord)
            if destination and destination not in self.enemies and destination != self.player_coord:
                dest_tile = self.grid.get_tile(destination)
                if dest_tile and dest_tile.occupant is None:
                    tile.set_occupant(None)
                    dest_tile.set_occupant(enemy)
                    self.enemies.pop(coord, None)
                    self.enemies[destination] = enemy
                    self.log(f"{enemy.name}이(가) {destination} 위치로 전진.")
        self.spawn_enemy()
        self.update_status_labels()

    def enemy_attack(self, enemy: Unit) -> None:
        damage = enemy.attack
        if self.player_block > 0:
            absorbed = min(self.player_block, damage)
            self.player_block -= absorbed
            damage -= absorbed
            if absorbed:
                self.log(f"방어도가 {absorbed} 피해를 흡수했습니다.")
        if damage > 0:
            self.player_unit.take_damage(damage)
            self.log(f"{enemy.name}에게 {damage} 피해를 받았습니다. (체력 {self.player_unit.hp})")
        player_tile = self.grid.get_tile(self.player_coord)
        if player_tile:
            player_tile._update_unit_labels()
        if self.player_unit.hp <= 0:
            self.player_unit.hp = 0
            self.game_over = True
            self.victory = False
            self.overlay_text.text = "패배 - 분대 전멸"
            self.overlay_hint.text = "R 키로 다시 시작"
            self.log("분대가 괴멸했습니다.")

    def spawn_enemy(self) -> None:
        if self.game_over:
            return
        empty_tiles = [
            coord
            for coord, tile in self.grid.tiles.items()
            if tile.occupant is None and self.grid.distance(coord, self.player_coord) >= 2
        ]
        if not empty_tiles:
            return
        if random.random() < 0.55:
            coord = random.choice(empty_tiles)
            enemy = self._make_enemy()
            tile = self.grid.get_tile(coord)
            if tile:
                tile.set_occupant(enemy)
                self.enemies[coord] = enemy
                self.log(f"새로운 적 {enemy.name} 등장 ({coord}).")

    def choose_enemy_move(self, coord: tuple[int, int]) -> tuple[int, int] | None:
        current_distance = self.grid.distance(coord, self.player_coord)
        candidates = self.grid.neighbors(coord)
        random.shuffle(candidates)
        best_coord = None
        best_distance = current_distance
        for candidate in candidates:
            if candidate == self.player_coord or candidate in self.enemies:
                continue
            tile = self.grid.get_tile(candidate)
            if not tile or tile.occupant is not None:
                continue
            distance = self.grid.distance(candidate, self.player_coord)
            if distance < best_distance:
                best_distance = distance
                best_coord = candidate
        return best_coord

    def update_status_labels(self) -> None:
        self.turn_text.text = f"턴 {self.turn}"
        self.energy_text.text = f"에너지 {self.energy}/{self.max_energy}"
        self.hp_text.text = f"체력 {self.player_unit.hp}/{self.player_unit.max_hp}"
        self.block_text.text = f"방어도 {self.player_block}"
        self.objective_text.text = f"격파한 적 {self.defeated_enemies}명"

    def log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > self.LOG_LIMIT:
            self.log_messages.pop(0)
        self.log_text.text = "\n".join(self.log_messages)

    def update(self) -> None:
        if Rs.userJustPressed(pygame.K_r):
            self.reset_game()
            return

        self.hand_layout.adjustLayout()
        click_consumed = False
        for card in list(self.hand_cards):
            if card.update():
                click_consumed = True
        self.end_turn_button.update()
        if self.end_turn_button.collideMouse() and Rs.userJustLeftClicked():
            click_consumed = True

        self.grid.update()

        hover_tile = self.grid.tile_under_point(Rs.mousePos().toTuple())
        info_lines: list[str] = []
        if self.selected_card:
            info_lines.append(f"[{self.selected_card.card_data.name}] 대상 선택 중")
        if hover_tile:
            info_lines.append(hover_tile.status_summary())
        else:
            info_lines.append("카드를 선택하거나 육각형을 클릭해 명령하세요.")
        self.hover_info_text.text = "\n\n".join(info_lines)

        if not click_consumed and Rs.userJustLeftClicked() and hover_tile:
            if self.selected_card:
                self.execute_card(self.selected_card, (hover_tile.q, hover_tile.r))
        if Rs.userJustRightClicked():
            self.cancel_selection()

        if not self.enemies and not self.game_over and self.turn >= self.goal_turns:
            self.game_over = True
            self.victory = True
            self.overlay_text.text = "승리 - 경로 확보"
            self.overlay_hint.text = "R 키로 다시 시작"
            self.log("분대가 지정 구역을 확보했습니다!")

    def draw(self) -> None:
        self.grid.draw()
        if not self.game_over:
            self.hand_layout.draw()
            self.end_turn_button.draw()
        self.turn_text.draw()
        self.energy_text.draw()
        self.hp_text.draw()
        self.block_text.draw()
        self.objective_text.draw()
        self.log_panel.draw()
        self.hover_info_panel.draw()
        if self.game_over:
            self.overlay_panel.center = RPoint(960, 540)
            self.overlay_panel.draw()


class Scenes:
    mainScene = HexTacticsScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="Hex Grid Card Tactics")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

