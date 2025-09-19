from REMOLib import *
import random


class WildernessTile(rectObj):
    """생존 지도의 한 구역을 나타내는 카드형 타일."""

    TERRAIN_TYPES = [
        ("바위 능선", Cs.dark(Cs.slategray)),
        ("침엽수림", Cs.dark(Cs.darkgreen)),
        ("갈대 습지", Cs.dark(Cs.teal)),
        ("완만한 초지", Cs.dark(Cs.darkolivegreen)),
        ("붉은 협곡", Cs.dark(Cs.firebrick)),
    ]

    RESOURCES = [
        ("식량", Cs.dark(Cs.sienna)),
        ("식수", Cs.dark(Cs.cadetblue)),
        ("자재", Cs.dark(Cs.peru)),
    ]

    DANGER_LEVELS = [
        (0, "안전함"),
        (1, "불안정함"),
        (2, "위험함"),
        (3, "극도로 위험함"),
    ]

    FEATURES = [
        None,
        None,
        "버려진 보급품",
        "낡은 전망대",
        "모닥불 자리",
        "방수 지형",
    ]

    def __init__(self, row: int, col: int, tile_size: tuple[int, int]):
        super().__init__(pygame.Rect(0, 0, tile_size[0], tile_size[1]), color=Cs.dark(Cs.dimgray), edge=4, radius=26)
        self.row = row
        self.col = col
        self._tile_size = tile_size
        self._fog_color = Cs.dark(Cs.dimgray)

        terrain_name, terrain_color = random.choice(self.TERRAIN_TYPES)
        self.terrain_name = terrain_name
        self._terrain_color = terrain_color

        resource_name, resource_color = random.choice(self.RESOURCES)
        self.resource_type = resource_name
        self._resource_color = resource_color
        self.resource_amount = random.choice([0, 1, 1, 2, 2, 3])

        danger_level, danger_desc = random.choice(self.DANGER_LEVELS)
        self.danger_level = danger_level
        self.danger_desc = danger_desc

        self.feature = random.choice(self.FEATURES)

        self.discovered = False
        self._selected = False

        self.index_label = textObj(f"{row + 1}-{col + 1}", size=20, color=Cs.light(Cs.lightgoldenrodyellow))
        self.index_label.setParent(self, depth=1)
        self.index_label.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 12)

        self.title_text = textObj("미확인 구역", size=26, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.centerx = self.offsetRect.centerx
        self.title_text.y = self.index_label.rect.bottom + 10

        self.detail_text = longTextObj(
            "탐험 카드로 정보를 수집하세요.",
            pos=RPoint(0, 0),
            size=20,
            color=Cs.light(Cs.lightsteelblue),
            textWidth=self._tile_size[0] - 40,
        )
        self.detail_text.setParent(self, depth=1)
        self.detail_text.centerx = self.offsetRect.centerx
        self.detail_text.y = self.title_text.rect.bottom + 12

        self._update_visuals()

    @property
    def display_name(self) -> str:
        return f"{self.row + 1}-{self.col + 1} 구역"

    def has_resource(self) -> bool:
        return self.resource_amount > 0

    def is_dangerous(self) -> bool:
        return self.danger_level > 0

    def set_selected(self, selected: bool) -> None:
        if self._selected != selected:
            self._selected = selected

    def discover(self) -> dict[str, object]:
        first_time = not self.discovered
        if first_time:
            self.discovered = True
            self._update_visuals()
        return {
            "first": first_time,
            "terrain": self.terrain_name,
            "resource_type": self.resource_type if self.resource_amount else None,
            "resource_amount": self.resource_amount,
            "danger_level": self.danger_level,
            "danger_desc": self.danger_desc,
            "feature": self.feature,
        }

    def gather(self) -> str | None:
        if not self.discovered or self.resource_amount <= 0:
            return None
        self.resource_amount -= 1
        self._update_visuals()
        return self.resource_type

    def reduce_danger(self) -> bool:
        if not self.discovered or self.danger_level <= 0:
            return False
        self.danger_level -= 1
        if self.danger_level < 0:
            self.danger_level = 0
        self._update_visuals()
        return True

    def status_summary(self) -> str:
        if not self.discovered:
            return "아직 조사되지 않았습니다."
        resource_info = "자원 없음" if self.resource_amount <= 0 else f"{self.resource_type} {self.resource_amount}개 남음"
        danger_info = f"위험도: {self.danger_desc}"
        lines = [resource_info, danger_info]
        if self.feature:
            lines.append(f"특징: {self.feature}")
        return "\n".join(lines)

    def _update_visuals(self) -> None:
        base_color = self._terrain_color if self.discovered else self._fog_color
        if self.color != base_color:
            self.color = base_color
        if self.discovered:
            self.title_text.text = self.terrain_name
            resource_text = "자원이 거의 없습니다." if self.resource_amount <= 0 else f"{self.resource_type} 확보 가능: {self.resource_amount}"
            danger_text = f"위험도: {self.danger_desc}"
            detail_lines = [resource_text, danger_text]
            if self.feature:
                detail_lines.append(f"특징: {self.feature}")
            self.detail_text.text = "\n".join(detail_lines)
            self.detail_text.color = Cs.light(self._resource_color)
        else:
            self.title_text.text = "미확인 구역"
            self.detail_text.text = "탐험 카드로 정보를 수집하세요."
            self.detail_text.color = Cs.light(Cs.lightsteelblue)

    def update(self) -> None:
        base_color = self._terrain_color if self.discovered else self._fog_color
        if self._selected:
            base_color = Cs.light(base_color)
        if self.collideMouse():
            base_color = Cs.light(base_color)
        if self.color != base_color:
            self.color = base_color
        return


class SurvivalActionCard(rectObj):
    """행동을 카드 형태로 표현하는 UI 구성요소."""

    def __init__(
        self,
        name: str,
        cost: int,
        description: str,
        *,
        color: tuple[int, int, int],
        can_play: callable,
        on_play: callable,
    ) -> None:
        super().__init__(pygame.Rect(0, 0, 210, 280), color=color, edge=6, radius=24)
        self.name = name
        self.cost = cost
        self.description = description
        self._can_play = can_play
        self._on_play = on_play

        self._base_color = color
        self._hover_color = Cs.light(color)

        self.cost_badge = rectObj(pygame.Rect(0, 0, 60, 60), radius=18, edge=4, color=Cs.dark(Cs.black))
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 18)

        self.cost_text = textObj(str(cost), size=28, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.title_text = textObj(name, size=26, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 94)

        self.desc_text = longTextObj(description, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=160)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.title_text.rect.bottom + 12

    def update(self) -> None:
        available = self._can_play()
        hovered = self.collideMouse()
        target_color = self._hover_color if hovered and available else self._base_color
        if self.color != target_color:
            self.color = target_color

        alpha = 255 if available else 150
        if self.alpha != alpha:
            self.alpha = alpha
            self.cost_badge.alpha = alpha
            self.cost_text.alpha = alpha
            self.title_text.alpha = alpha
            self.desc_text.alpha = alpha

        if hovered and available and Rs.userJustLeftClicked():
            self._on_play()
        return


class SurvivalScene(Scene):
    MAX_LOG = 7
    GOAL_DAYS = 7

    def initOnce(self) -> None:
        self.day = 1
        self.max_energy = 5
        self.energy = self.max_energy
        self.health = 8
        self.hunger = 2
        self.thirst = 2
        self.morale = 6
        self.food = 2
        self.water = 2
        self.materials = 1
        self.weather = random.choice(["맑음", "흐림", "바람", "비구름"])
        self.game_over = False

        self.selected_tile: WildernessTile | None = None
        self.log_messages: list[str] = []

        self.grid_panel = rectObj(
            pygame.Rect(0, 0, 1180, 760), color=Cs.dark(Cs.darkslategray), edge=6, radius=36
        )
        self.grid_panel.x = 80
        self.grid_panel.y = 140

        self.grid_layout = gridObj(
            pos=RPoint(self.grid_panel.rect.x + 40, self.grid_panel.rect.y + 40),
            tileSize=(220, 200),
            grid=(4, 3),
            spacing=(28, 28),
            color=Cs.dark(Cs.dimgray),
        )

        self.tiles: list[WildernessTile] = []
        for row in range(3):
            for col in range(4):
                tile = WildernessTile(row, col, (220, 200))
                self.grid_layout[row][col] = tile
                self.tiles.append(tile)
        self.grid_layout.adjustLayout()

        self.game_over_text = longTextObj(
            "",
            pos=RPoint(0, 0),
            size=36,
            color=Cs.light(Cs.orange),
            textWidth=720,
        )
        self.game_over_text.setParent(self.grid_panel, depth=1)
        self.game_over_text.center = RPoint(self.grid_panel.offsetRect.center)
        self.game_over_text.alpha = 0

        self.card_panel = rectObj(
            pygame.Rect(0, 0, 1320, 280), color=Cs.dark(Cs.slategray), edge=6, radius=30
        )
        self.card_panel.centerx = 1920 // 2
        self.card_panel.y = 780

        self.card_layout = cardLayout(
            RPoint(self.card_panel.rect.x + 60, self.card_panel.rect.y + 40),
            spacing=40,
            maxWidth=1200,
            isVertical=False,
        )

        self.status_layout = layoutObj(pos=RPoint(1340, 60), spacing=16, isVertical=True)
        self.day_text = textObj("", size=34, color=Cs.white)
        self.energy_text = textObj("", size=26, color=Cs.light(Cs.skyblue))
        self.health_text = textObj("", size=26, color=Cs.light(Cs.lightcoral))
        self.hunger_text = textObj("", size=26, color=Cs.light(Cs.khaki))
        self.morale_text = textObj("", size=26, color=Cs.light(Cs.mediumorchid))
        self.inventory_text = textObj("", size=26, color=Cs.light(Cs.lightsteelblue))
        for label in (
            self.day_text,
            self.energy_text,
            self.health_text,
            self.hunger_text,
            self.morale_text,
            self.inventory_text,
        ):
            label.setParent(self.status_layout)
        self.status_layout.adjustLayout()

        self.tip_text = longTextObj(
            "좌측 그리드에서 구역을 선택한 뒤 카드를 눌러 행동하세요. \n스페이스바로 하루를 마칠 수 있습니다.",
            pos=RPoint(80, 60),
            size=24,
            color=Cs.light(Cs.lightsteelblue),
            textWidth=900,
        )

        self.selection_panel = rectObj(
            pygame.Rect(0, 0, 520, 300), color=Cs.dark(Cs.black), edge=4, radius=28
        )
        self.selection_panel.x = 1340
        self.selection_panel.y = 180

        self.selection_title = textObj("선택된 구역 없음", size=30, color=Cs.white)
        self.selection_title.setParent(self.selection_panel, depth=1)
        self.selection_title.midtop = RPoint(self.selection_panel.offsetRect.midtop) + RPoint(0, 24)

        self.selection_detail = longTextObj(
            "그리드의 구역을 클릭하면 자세한 정보가 표시됩니다.",
            pos=RPoint(0, 0),
            size=22,
            color=Cs.light(Cs.lightgoldenrodyellow),
            textWidth=420,
        )
        self.selection_detail.setParent(self.selection_panel, depth=1)
        self.selection_detail.centerx = self.selection_panel.offsetRect.centerx
        self.selection_detail.y = self.selection_title.rect.bottom + 20

        self.log_panel_bg = rectObj(
            pygame.Rect(0, 0, 520, 320), color=Cs.dark(Cs.black), edge=4, radius=26
        )
        self.log_panel_bg.x = 1340
        self.log_panel_bg.y = 520

        self.log_box = longTextObj("", pos=self.log_panel_bg.pos + RPoint(24, 24), size=22, color=Cs.white, textWidth=472)

        self.end_day_button = monoTextButton("하루 마감", pos=(1560, 80), size=32, color=Cs.orange)
        self.end_day_button.connect(self._start_next_day)

        self._create_cards()
        self._refresh_status()
        self._log("구조 신호를 보내기 위한 생존 여정이 시작되었습니다.")

    def init(self) -> None:
        return

    def _create_cards(self) -> None:
        self.action_cards: list[SurvivalActionCard] = []

        def add_card(**kwargs):
            card = SurvivalActionCard(**kwargs)
            card.setParent(self.card_layout)
            self.action_cards.append(card)

        add_card(
            name="탐험",
            cost=2,
            description="선택한 구역을 조사해 지형과 위험을 파악합니다.",
            color=Cs.dark(Cs.steelblue),
            can_play=lambda: not self.game_over
            and self.energy >= 2
            and self.selected_tile is not None
            and not self.selected_tile.discovered,
            on_play=self._play_explore,
        )

        add_card(
            name="채집",
            cost=1,
            description="드러난 구역에서 자원을 수집합니다.",
            color=Cs.dark(Cs.seagreen),
            can_play=lambda: not self.game_over
            and self.energy >= 1
            and self.selected_tile is not None
            and self.selected_tile.discovered
            and self.selected_tile.has_resource(),
            on_play=self._play_gather,
        )

        add_card(
            name="위험 대응",
            cost=1,
            description="자재를 소비해 선택 구역의 위험도를 낮춥니다.",
            color=Cs.dark(Cs.maroon),
            can_play=lambda: not self.game_over
            and self.energy >= 1
            and self.materials > 0
            and self.selected_tile is not None
            and self.selected_tile.discovered
            and self.selected_tile.is_dangerous(),
            on_play=self._play_secure,
        )

        add_card(
            name="휴식",
            cost=1,
            description="캠프를 정비해 체력과 사기를 회복합니다.",
            color=Cs.dark(Cs.saddlebrown),
            can_play=lambda: not self.game_over and self.energy >= 1,
            on_play=self._play_rest,
        )

        self.card_layout.adjustLayout()

    def _refresh_status(self) -> None:
        self.day_text.text = f"{self.day}일차 · {self.weather}"
        self.energy_text.text = f"행동력: {self.energy}/{self.max_energy}"
        self.health_text.text = f"체력: {self.health}/10"
        self.hunger_text.text = f"허기: {self.hunger}/10 · 갈증: {self.thirst}/10"
        self.morale_text.text = f"사기: {self.morale}/10"
        self.inventory_text.text = f"식량 {self.food} · 식수 {self.water} · 자재 {self.materials}"

    def _refresh_selection_details(self) -> None:
        if self.selected_tile is None:
            self.selection_title.text = "선택된 구역 없음"
            self.selection_detail.text = "그리드의 구역을 클릭하면 자세한 정보가 표시됩니다."
            return
        self.selection_title.text = f"{self.selected_tile.display_name}"
        self.selection_detail.text = self.selected_tile.status_summary()

    def _log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > self.MAX_LOG:
            self.log_messages = self.log_messages[-self.MAX_LOG :]
        self.log_box.text = "\n".join(self.log_messages)

    def _consume_energy(self, cost: int) -> bool:
        if self.energy < cost:
            self._log("남은 행동력이 부족합니다.")
            return False
        self.energy -= cost
        self._refresh_status()
        return True

    def _select_tile_under_cursor(self) -> None:
        if self.game_over or not Rs.userJustLeftClicked():
            return
        for tile in self.tiles:
            if tile.collideMouse():
                self.selected_tile = tile
                self._refresh_selection_details()
                if tile.discovered:
                    self._log(f"{tile.display_name}을(를) 살펴봅니다. {tile.terrain_name} 지형입니다.")
                else:
                    self._log(f"{tile.display_name}을(를) 목표로 삼았습니다. 탐험이 필요합니다.")
                break

    def _play_explore(self) -> None:
        if self.selected_tile is None:
            self._log("탐험할 구역을 먼저 선택하세요.")
            return
        if not self._consume_energy(2):
            return
        result = self.selected_tile.discover()
        terrain = result["terrain"]
        summary_parts = [f"{self.selected_tile.display_name} 탐험 완료: {terrain}"]
        resource_type = result.get("resource_type")
        if resource_type:
            summary_parts.append(f"{resource_type} 흔적 발견")
        else:
            summary_parts.append("자원 부족")
        summary_parts.append(f"위험도 {result['danger_desc']}")
        self._log(" · ".join(summary_parts))

        feature = result.get("feature")
        if feature == "버려진 보급품":
            loot_type = random.choice(["식량", "식수", "자재"])
            if loot_type == "식량":
                self.food += 1
            elif loot_type == "식수":
                self.water += 1
            else:
                self.materials += 1
            self._log(f"버려진 보급품에서 {loot_type}을(를) 발견했습니다!")
        elif feature == "낡은 전망대":
            self.morale = min(10, self.morale + 1)
            self._log("전망대에서 주변을 파악하며 사기를 다졌습니다.")
        elif feature == "모닥불 자리":
            self.selected_tile.danger_level = max(0, self.selected_tile.danger_level - 1)
            self.selected_tile._update_visuals()
            self._log("안전한 모닥불 자리 덕분에 위험이 조금 줄었습니다.")
        elif feature == "방수 지형":
            self.thirst = max(0, self.thirst - 1)
            self._log("지하수가 고여 있어 갈증이 조금 해소되었습니다.")

        danger_level = result["danger_level"]
        if danger_level >= 1:
            injury_chance = {1: 0.35, 2: 0.55, 3: 0.75}[danger_level]
            if random.random() < injury_chance:
                damage = 1 if danger_level == 1 else random.randint(1, danger_level)
                self.health = max(0, self.health - damage)
                self.morale = max(0, self.morale - 1)
                self._log(f"탐험 중 위협을 만나 체력 {damage} 감소, 사기 -1")
        self._refresh_selection_details()
        self._refresh_status()
        self._check_survival_status()

    def _play_gather(self) -> None:
        tile = self.selected_tile
        if tile is None:
            self._log("자원을 모을 구역을 선택하세요.")
            return
        if not self._consume_energy(1):
            return
        resource = tile.gather()
        if resource is None:
            self._log("이 구역에서 얻을 수 있는 자원이 더 없습니다.")
            return
        if resource == "식량":
            self.food += 1
        elif resource == "식수":
            self.water += 1
        else:
            self.materials += 1
        self._log(f"{tile.display_name}에서 {resource}을(를) 확보했습니다.")

        if tile.danger_level > 0 and random.random() < 0.25:
            self.health = max(0, self.health - 1)
            self._log("수집 과정에서 작은 부상을 입었습니다. 체력 -1")
        self._refresh_selection_details()
        self._refresh_status()
        self._check_survival_status()

    def _play_secure(self) -> None:
        tile = self.selected_tile
        if tile is None:
            self._log("위험을 낮출 구역을 선택하세요.")
            return
        if not self._consume_energy(1):
            return
        if self.materials <= 0:
            self._log("자재가 부족하여 방어막을 구축할 수 없습니다.")
            return
        if not tile.reduce_danger():
            self._log("이 구역은 이미 안전합니다.")
            return
        self.materials -= 1
        self.morale = min(10, self.morale + 1)
        self._log(f"{tile.display_name}의 위협을 낮췄습니다. 사기 +1")
        self._refresh_selection_details()
        self._refresh_status()

    def _play_rest(self) -> None:
        if not self._consume_energy(1):
            return
        healed = 1
        morale_gain = 1
        self.health = min(10, self.health + healed)
        self.morale = min(10, self.morale + morale_gain)

        if self.food > 0:
            self.food -= 1
            self.hunger = max(0, self.hunger - 3)
            food_message = "식량을 소비하여 허기를 달랬습니다."
        else:
            self.hunger = min(10, self.hunger + 1)
            food_message = "식량이 부족해 허기가 심해졌습니다."

        if self.water > 0:
            self.water -= 1
            self.thirst = max(0, self.thirst - 3)
            water_message = "식수를 마셔 갈증이 가셨습니다."
        else:
            self.thirst = min(10, self.thirst + 1)
            water_message = "식수가 부족해 갈증이 심해졌습니다."

        self._log(f"캠프에서 휴식을 취했습니다. 체력 +{healed}, 사기 +{morale_gain}")
        self._log(f"{food_message} {water_message}")
        self._refresh_status()
        self._check_survival_status()

    def _start_next_day(self) -> None:
        if self.game_over:
            return
        self.day += 1
        self.energy = self.max_energy
        self.weather = random.choice(["맑음", "흐림", "강풍", "장맛비"])

        if self.food > 0:
            self.food -= 1
            self.hunger = max(0, self.hunger - 2)
            food_status = "저녁 식사로 허기를 달랬습니다."
        else:
            self.hunger = min(10, self.hunger + 2)
            food_status = "식량이 부족해 허기가 심해졌습니다."

        if self.water > 0:
            self.water -= 1
            self.thirst = max(0, self.thirst - 2)
            water_status = "식수를 확보해 갈증이 완화되었습니다."
        else:
            self.thirst = min(10, self.thirst + 2)
            water_status = "식수가 없어 갈증이 심해졌습니다."

        if self.hunger >= 8:
            self.health = max(0, self.health - 1)
            self._log("허기가 심해 체력이 감소했습니다.")
        if self.thirst >= 8:
            self.health = max(0, self.health - 1)
            self._log("갈증이 심해 체력이 감소했습니다.")
        if self.hunger >= 9 or self.thirst >= 9:
            self.morale = max(0, self.morale - 1)

        night_event = random.random()
        if night_event < 0.2 and any(tile.danger_level > 0 for tile in self.tiles):
            threatened_tiles = [tile for tile in self.tiles if tile.danger_level > 0]
            target = random.choice(threatened_tiles)
            self.health = max(0, self.health - 1)
            self._log(f"밤사이 {target.display_name}에서 위협이 들이닥쳐 체력 -1")
        elif night_event > 0.85:
            self.morale = min(10, self.morale + 1)
            self._log("밤하늘의 별자리가 사기를 북돋웠습니다. 사기 +1")

        self._log(f"새로운 하루가 시작되었습니다. {food_status} {water_status}")
        self._refresh_status()
        self._refresh_selection_details()
        self._check_survival_status()

        if self.day > self.GOAL_DAYS and not self.game_over:
            self._set_game_over("7일을 버텨 구조 신호를 수신했습니다! 생존 성공!")

    def _set_game_over(self, message: str) -> None:
        if self.game_over:
            return
        self.game_over = True
        self.game_over_text.text = message
        self.game_over_text.alpha = 255
        self._log(message)

    def _check_survival_status(self) -> None:
        if self.health <= 0:
            self._set_game_over("부상을 회복하지 못해 캠프가 붕괴했습니다.")
        elif self.hunger >= 10:
            self._set_game_over("극심한 허기로 더는 버틸 수 없습니다.")
        elif self.thirst >= 10:
            self._set_game_over("탈수로 눈앞이 아득해졌습니다.")

    def update(self) -> None:
        if Rs.userJustPressed(pygame.K_SPACE):
            self._start_next_day()

        for tile in self.tiles:
            tile.set_selected(tile is self.selected_tile)
        self._select_tile_under_cursor()

        self.grid_layout.update()
        self.card_layout.adjustLayout()
        self.card_layout.update()
        self.status_layout.update()
        self.end_day_button.update()
        return

    def draw(self) -> None:
        self.grid_panel.draw()
        self.grid_layout.draw()
        self.game_over_text.draw()
        self.card_panel.draw()
        self.card_layout.draw()
        self.status_layout.draw()
        self.tip_text.draw()
        self.selection_panel.draw()
        self.selection_title.draw()
        self.selection_detail.draw()
        self.log_panel_bg.draw()
        self.log_box.draw()
        self.end_day_button.draw()
        return


class Scenes:
    mainScene = SurvivalScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1920, 1080),
        screen_size=(1920, 1080),
        fullscreen=False,
        caption="카드&그리드 생존 시뮬레이션",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
