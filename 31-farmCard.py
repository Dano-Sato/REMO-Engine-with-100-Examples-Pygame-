from REMOLib import *
import random


class FieldTile(rectObj):
    """농장 밭 하나를 표현하는 카드형 타일."""

    STAGE_INFO = [
        ("빈 밭", Cs.dark(Cs.darkolivegreen)),
        ("씨앗", Cs.dark(Cs.peru)),
        ("새싹", Cs.dark(Cs.seagreen)),
        ("성숙", Cs.dark(Cs.darkgoldenrod)),
    ]

    CROPS = ["당근", "감자", "상추", "토마토", "호박"]

    def __init__(self, index: int):
        super().__init__(pygame.Rect(0, 0, 220, 220), color=self.STAGE_INFO[0][1], edge=6, radius=26)
        self.index = index
        self.stage = 0
        self.crop_name: str | None = None
        self.watered_today = False
        self.days_grown = 0

        self._base_color = self.STAGE_INFO[0][1]
        self._hover_color = Cs.light(self._base_color)

        self.title = textObj(f"{index + 1}번 밭", size=26, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 16)

        self.stage_text = textObj("", size=28, color=Cs.white)
        self.stage_text.setParent(self, depth=1)
        self.stage_text.center = self.offsetRect.center

        self.detail_text = textObj("", size=20, color=Cs.light(Cs.lightgoldenrodyellow))
        self.detail_text.setParent(self, depth=1)
        self.detail_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)

        self._refresh_visuals()

    @property
    def display_name(self) -> str:
        return f"{self.index + 1}번 밭"

    def is_empty(self) -> bool:
        return self.stage == 0

    def is_growing(self) -> bool:
        return self.stage in (1, 2)

    def is_ready(self) -> bool:
        return self.stage == 3

    def plant(self, crop_name: str | None = None) -> None:
        self.crop_name = crop_name or random.choice(self.CROPS)
        self.stage = 1
        self.days_grown = 0
        self.watered_today = False
        self._refresh_visuals()

    def advance(self, amount: int = 1) -> None:
        if self.stage in (1, 2):
            before = self.stage
            self.stage = min(3, self.stage + amount)
            if before != self.stage:
                self.days_grown += 1
            self._refresh_visuals()

    def advance_day(self) -> bool:
        matured = False
        if self.stage in (1, 2):
            prev_stage = self.stage
            self.stage = min(3, self.stage + 1)
            matured = self.stage == 3 and prev_stage != 3
            self.days_grown += 1
        self.watered_today = False
        self._refresh_visuals()
        return matured

    def water(self) -> bool:
        if self.stage in (1, 2) and not self.watered_today:
            self.watered_today = True
            self.advance(1)
            return True
        return False

    def fertilize(self) -> bool:
        if self.stage in (1, 2):
            prev_stage = self.stage
            self.stage = min(3, self.stage + 2)
            self.days_grown += 1
            self._refresh_visuals()
            return self.stage != prev_stage
        return False

    def harvest(self) -> str | None:
        if self.stage == 3 and self.crop_name:
            crop = self.crop_name
            self.stage = 0
            self.crop_name = None
            self.days_grown = 0
            self.watered_today = False
            self._refresh_visuals()
            return crop
        return None

    def update(self) -> None:
        hovered = self.collideMouse()
        target = self._hover_color if hovered else self._base_color
        if self.color != target:
            self.color = target
        return

    def _refresh_visuals(self) -> None:
        label, base_color = self.STAGE_INFO[self.stage]
        self._base_color = base_color
        self._hover_color = Cs.light(base_color)
        if self.color != self._base_color:
            self.color = self._base_color

        if self.stage == 0:
            self.stage_text.text = "비어 있음"
            self.detail_text.text = "씨앗을 심어보세요."
        elif self.stage == 1:
            self.stage_text.text = f"{self.crop_name} 씨앗"
            self.detail_text.text = "물을 주면 빨리 자라요."
        elif self.stage == 2:
            self.stage_text.text = f"{self.crop_name} 성장 중"
            self.detail_text.text = "조금 더 보살펴주세요."
        else:
            self.stage_text.text = f"{self.crop_name} 수확 가능!"
            self.detail_text.text = "수확 카드로 창고에 담으세요."


class FarmActionCard(rectObj):
    """농장 관리 행동을 표현하는 카드."""

    def __init__(
        self,
        name: str,
        cost: int,
        description: str,
        *,
        color: tuple[int, int, int] = Cs.dark(Cs.darkslategray),
        can_play: callable,
        on_play: callable,
    ) -> None:
        super().__init__(pygame.Rect(0, 0, 200, 260), color=color, edge=6, radius=24)
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
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 92)

        self.desc_text = longTextObj(description, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=150)
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


class FarmScene(Scene):
    MAX_LOG = 6

    def initOnce(self) -> None:
        self.day = 1
        self.max_energy = 4
        self.energy = self.max_energy
        self.seeds = 5
        self.storage = 0
        self.coins = 3
        self.log_messages: list[str] = []

        self.field_panel = rectObj(
            pygame.Rect(0, 0, 1320, 380), color=Cs.dark(Cs.darkolivegreen), edge=6, radius=32
        )
        self.field_panel.centerx = 1920 // 2 + 280
        self.field_panel.y = 150

        self.card_panel = rectObj(
            pygame.Rect(0, 0, 1320, 280), color=Cs.dark(Cs.slategray), edge=6, radius=30
        )
        self.card_panel.centerx = 1920 // 2 + 280
        self.card_panel.y = 720

        self.status_layout = layoutObj(pos=RPoint(120, 60), spacing=12, isVertical=True)
        self.day_text = textObj("", size=34, color=Cs.white)
        self.energy_text = textObj("", size=26, color=Cs.light(Cs.lightgoldenrodyellow))
        self.seed_text = textObj("", size=26, color=Cs.light(Cs.palegreen))
        self.storage_text = textObj("", size=26, color=Cs.light(Cs.orange))
        self.coin_text = textObj("", size=26, color=Cs.light(Cs.skyblue))
        for label in (
            self.day_text,
            self.energy_text,
            self.seed_text,
            self.storage_text,
            self.coin_text,
        ):
            label.setParent(self.status_layout)
        self.status_layout.adjustLayout()

        self.field_layout = layoutObj(pos=RPoint(self.field_panel.rect.x + 80, self.field_panel.rect.y + 80), spacing=60, isVertical=False)
        self.fields: list[FieldTile] = []
        for i in range(4):
            field = FieldTile(i)
            field.setParent(self.field_layout)
            self.fields.append(field)
        self.field_layout.adjustLayout()

        self.log_box_bg = rectObj(pygame.Rect(0, 0, 520, 420), color=Cs.dark(Cs.black), edge=4, radius=24)
        self.log_box_bg.pos = RPoint(40, 520)
        self.log_box = longTextObj("", pos=self.log_box_bg.pos + RPoint(24, 24), size=22, color=Cs.white, textWidth=472)

        self.card_layout = cardLayout(RPoint(self.card_panel.rect.x + 80, self.card_panel.rect.y + 40), spacing=40, maxWidth=1160, isVertical=False)
        self.action_cards: list[FarmActionCard] = []

        self.end_day_button = monoTextButton("다음 날", pos=(1560, 80), size=32, color=Cs.orange)
        self.end_day_button.connect(self._start_next_day)

        self._create_cards()
        self._refresh_status()
        self._log("농장이 깨어났습니다. 첫째 날을 시작해보세요!")

    def init(self) -> None:
        return

    def _create_cards(self) -> None:
        def add_card(**kwargs):
            card = FarmActionCard(**kwargs)
            card.setParent(self.card_layout)
            self.action_cards.append(card)

        add_card(
            name="씨앗 심기",
            cost=1,
            description="빈 밭에 씨앗을 심습니다. 씨앗이 필요합니다.",
            color=Cs.dark(Cs.sienna),
            can_play=lambda: self.energy >= 1 and self.seeds > 0 and any(field.is_empty() for field in self.fields),
            on_play=self._play_plant,
        )

        add_card(
            name="물 주기",
            cost=1,
            description="성장 중인 밭에 물을 주어 성장을 돕습니다.",
            color=Cs.dark(Cs.teal),
            can_play=lambda: self.energy >= 1 and any(field.is_growing() and not field.watered_today for field in self.fields),
            on_play=self._play_water,
        )

        add_card(
            name="퇴비 뿌리기",
            cost=2,
            description="가장 느리게 자라는 작물의 성장을 크게 돕습니다.",
            color=Cs.dark(Cs.firebrick),
            can_play=lambda: self.energy >= 2 and any(field.is_growing() for field in self.fields),
            on_play=self._play_fertilize,
        )

        add_card(
            name="수확",
            cost=1,
            description="수확 가능한 모든 작물을 수확하여 창고에 보관합니다.",
            color=Cs.dark(Cs.olivedrab),
            can_play=lambda: self.energy >= 1 and any(field.is_ready() for field in self.fields),
            on_play=self._play_harvest,
        )

        add_card(
            name="시장 거래",
            cost=1,
            description="창고의 작물을 팔아 씨앗을 구입합니다.",
            color=Cs.dark(Cs.midnightblue),
            can_play=lambda: self.energy >= 1 and (self.storage > 0 or self.coins >= 3),
            on_play=self._play_trade,
        )

        self.card_layout.adjustLayout()

    def _refresh_status(self) -> None:
        self.day_text.text = f"{self.day}일차"
        self.energy_text.text = f"에너지: {self.energy}/{self.max_energy}"
        self.seed_text.text = f"씨앗: {self.seeds}"
        self.storage_text.text = f"창고 수확물: {self.storage}"
        self.coin_text.text = f"동전: {self.coins}"

    def _log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > self.MAX_LOG:
            self.log_messages = self.log_messages[-self.MAX_LOG :]
        self.log_box.text = "\n".join(self.log_messages)

    def _consume_energy(self, cost: int) -> bool:
        if self.energy < cost:
            self._log("에너지가 부족합니다.")
            return False
        self.energy -= cost
        self._refresh_status()
        return True

    def _play_plant(self) -> None:
        if self.seeds <= 0:
            self._log("씨앗이 부족합니다.")
            return
        empty_field = next((field for field in self.fields if field.is_empty()), None)
        if empty_field is None:
            self._log("씨앗을 심을 빈 밭이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        crop = random.choice(FieldTile.CROPS)
        empty_field.plant(crop)
        self.seeds -= 1
        self._refresh_status()
        self._log(f"{empty_field.display_name}에 {crop} 씨앗을 심었습니다.")

    def _play_water(self) -> None:
        water_targets = [field for field in self.fields if field.is_growing() and not field.watered_today]
        if not water_targets:
            self._log("물을 줄 수 있는 밭이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        watered = 0
        for field in water_targets:
            if field.water():
                watered += 1
        if watered:
            self._log(f"{watered}개의 밭에 물을 주었습니다.")
        else:
            self._log("이미 오늘은 충분히 물을 주었습니다.")

    def _play_fertilize(self) -> None:
        targets = [field for field in self.fields if field.is_growing()]
        if not targets:
            self._log("성장 중인 작물이 없습니다.")
            return
        if not self._consume_energy(2):
            return
        slowest = sorted(targets, key=lambda f: (f.stage, f.days_grown))[0]
        if slowest.fertilize():
            self._log(f"{slowest.display_name}에 퇴비를 뿌려 성장이 빨라졌습니다!")
        else:
            self._log("퇴비가 큰 효과를 내지 못했습니다.")

    def _play_harvest(self) -> None:
        ready_fields = [field for field in self.fields if field.is_ready()]
        if not ready_fields:
            self._log("수확할 작물이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        harvested_crops = []
        for field in ready_fields:
            crop = field.harvest()
            if crop:
                harvested_crops.append(crop)
        if harvested_crops:
            self.storage += len(harvested_crops)
            self.coins += len(harvested_crops) * 3
            self._refresh_status()
            crops_str = ", ".join(harvested_crops)
            self._log(f"{len(harvested_crops)}개의 작물을 수확했습니다: {crops_str}")
        else:
            self._log("수확에 실패했습니다.")

    def _play_trade(self) -> None:
        if self.storage <= 0 and self.coins < 3:
            self._log("거래할 수 있는 자원이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        gained_seeds = 0
        sold_goods = 0
        if self.storage > 0:
            sold_goods = min(self.storage, 3)
            self.storage -= sold_goods
            self.coins += sold_goods * 2
        if self.coins >= 3:
            trade_count = self.coins // 3
            spend = min(trade_count, 2)
            if spend > 0:
                self.coins -= spend * 3
                gained_seeds = spend * 2
                self.seeds += gained_seeds
        self._refresh_status()
        summary_parts = []
        if sold_goods:
            summary_parts.append(f"수확물 {sold_goods}개 판매")
        if gained_seeds:
            summary_parts.append(f"씨앗 {gained_seeds}개 구매")
        if not summary_parts:
            summary_parts.append("시장 상황이 좋지 않아 거래가 성사되지 않았습니다.")
        self._log(" · ".join(summary_parts))

    def _start_next_day(self) -> None:
        self.day += 1
        self.energy = self.max_energy
        matured_count = 0
        for field in self.fields:
            if field.advance_day():
                matured_count += 1
        self._refresh_status()
        if matured_count:
            self._log(f"새로운 하루가 밝았습니다! {matured_count}개의 밭이 수확 준비를 마쳤습니다.")
        else:
            self._log("새로운 하루가 시작되었지만 아직은 기다림이 필요합니다.")

    def update(self) -> None:
        if Rs.userJustPressed(pygame.K_SPACE):
            self._start_next_day()
        self.status_layout.update()
        self.field_layout.update()
        self.card_layout.adjustLayout()
        self.card_layout.update()
        self.end_day_button.update()
        return

    def draw(self) -> None:
        self.field_panel.draw()
        self.card_panel.draw()
        self.status_layout.draw()
        self.field_layout.draw()
        self.log_box_bg.draw()
        self.log_box.draw()
        self.card_layout.draw()
        self.end_day_button.draw()
        return


class Scenes:
    mainScene = FarmScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="농장 카드 매니저")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
