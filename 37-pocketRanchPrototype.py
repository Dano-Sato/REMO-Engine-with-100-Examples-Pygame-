from REMOLib import *
import random


CROPS = [
    {"name": "루미나 당근", "flavor": "달콤", "tags": {"root", "sun"}},
    {"name": "별빛 상추", "flavor": "시원", "tags": {"leaf", "water"}},
    {"name": "분홍 토마토", "flavor": "산뜻", "tags": {"fruit", "sun"}},
    {"name": "은빛 감자", "flavor": "포근", "tags": {"root", "tonic"}},
    {"name": "무지개 고추", "flavor": "매콤", "tags": {"fruit", "sun"}},
]

COMPANION_LIBRARY = [
    {
        "name": "물방울 너구리",
        "trait": "water",
        "description": "물과 관련된 케어에 큰 보너스를 줍니다.",
        "color": Cs.dark(Cs.teal),
    },
    {
        "name": "햇살 토끼",
        "trait": "sun",
        "description": "햇살 케어와 하루 성장 보너스를 강화합니다.",
        "color": Cs.dark(Cs.orange),
    },
    {
        "name": "감미 까마귀",
        "trait": "muse",
        "description": "향기로운 영양제와 수확 품질을 높여줍니다.",
        "color": Cs.dark(Cs.plum),
    },
    {
        "name": "바람여우",
        "trait": "swift",
        "description": "여러 밭을 동시에 돌보는 행동에 도움을 줍니다.",
        "color": Cs.dark(Cs.skyblue),
    },
]

QUALITY_LABELS = ["보통", "고급", "특급", "전설"]

WEATHERS = [
    {
        "name": "햇살 포근",
        "description": "밭마다 기본 성장 +4. 햇살 케어 추가 성장 +6.",
        "daily_bonus": 4,
        "sun_bonus": 6,
        "water_bonus": 0,
        "dry_penalty": 0,
        "companion_favor": 2,
        "vitality_bonus": 1,
    },
    {
        "name": "이슬비",
        "description": "물을 주면 +8 성장. 하루가 끝나면 기본 성장 +6.",
        "daily_bonus": 6,
        "sun_bonus": 0,
        "water_bonus": 8,
        "dry_penalty": 0,
        "companion_favor": 1,
        "vitality_bonus": 2,
    },
    {
        "name": "건조한 모래바람",
        "description": "물을 주지 않은 밭은 -10 성장. 햇살 케어 보너스 +4.",
        "daily_bonus": 0,
        "sun_bonus": 4,
        "water_bonus": 0,
        "dry_penalty": 10,
        "companion_favor": 0,
        "vitality_bonus": 0,
    },
    {
        "name": "별빛 소나타",
        "description": "친구 친밀도 +6. 모든 케어가 추가 활력을 부여합니다.",
        "daily_bonus": 3,
        "sun_bonus": 3,
        "water_bonus": 4,
        "dry_penalty": 0,
        "companion_favor": 6,
        "vitality_bonus": 3,
    },
]


class PocketPlot(rectObj):
    """포켓 목장의 밭 하나를 표현하는 카드형 타일."""

    STAGE_INFO = [
        ("비어 있음", Cs.dark(Cs.dimgray)),
        ("씨앗 뿌림", Cs.dark(Cs.sienna)),
        ("새싹", Cs.dark(Cs.seagreen)),
        ("꽃봉오리", Cs.dark(Cs.forestgreen)),
        ("수확 준비", Cs.dark(Cs.darkgoldenrod)),
    ]

    STAGE_THRESHOLDS = [0, 30, 70, 120, 180]

    CARE_TAGS = ("water", "sun", "tonic")

    COMPANION_BONUS = {
        "water": {"water": 10, "sun": 4, "tonic": 4},
        "sun": {"sun": 12, "water": 5, "tonic": 6},
        "muse": {"tonic": 12, "water": 3, "sun": 4},
        "swift": {"water": 6, "sun": 6, "tonic": 6},
    }

    COMPANION_TAG_TEXT = {
        "water": "물결",
        "sun": "햇살",
        "muse": "선율",
        "swift": "바람",
    }

    def __init__(self, index: int):
        super().__init__(pygame.Rect(0, 0, 240, 260), color=self.STAGE_INFO[0][1], edge=6, radius=28)
        self.index = index
        self.stage = 0
        self.crop: dict | None = None
        self.seed_grade: str | None = None
        self.growth_points = 0
        self.vitality_points = 0
        self.affinity = 0
        self.companion: dict | None = None
        self.care_marks = {tag: False for tag in self.CARE_TAGS}

        self._base_color = self.STAGE_INFO[0][1]
        self._hover_color = Cs.light(self._base_color)

        self.title = textObj(f"{index + 1}번 포켓밭", size=26, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 18)

        self.stage_text = textObj("", size=28, color=Cs.white)
        self.stage_text.setParent(self, depth=1)
        self.stage_text.center = self.offsetRect.center

        self.crop_text = textObj("", size=22, color=Cs.light(Cs.lightgoldenrodyellow))
        self.crop_text.setParent(self, depth=1)
        self.crop_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)

        self.progress_bg = rectObj(pygame.Rect(0, 0, 180, 18), color=Cs.dark(Cs.black), edge=2, radius=10)
        self.progress_bg.setParent(self, depth=1)
        self.progress_bg.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 48)

        self.progress_fill = rectObj(pygame.Rect(0, 0, 176, 12), color=Cs.light(Cs.limegreen), edge=0, radius=8)
        self.progress_fill.setParent(self.progress_bg, depth=1)
        self.progress_fill.midleft = RPoint(self.progress_bg.offsetRect.midleft) + RPoint(2, 0)

        self.progress_text = textObj("", size=18, color=Cs.white)
        self.progress_text.setParent(self, depth=1)
        self.progress_text.midbottom = self.progress_bg.midtop - RPoint(0, 6)

        self.companion_badge = rectObj(pygame.Rect(0, 0, 112, 64), color=Cs.dark(Cs.gray), edge=4, radius=16)
        self.companion_badge.setParent(self, depth=1)
        self.companion_badge.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 60)
        self.companion_badge.alpha = 120

        self.companion_text = longTextObj("", pos=RPoint(0, 0), size=18, color=Cs.white, textWidth=92)
        self.companion_text.setParent(self.companion_badge, depth=1)
        self.companion_text.center = self.companion_badge.offsetRect.center

        self._refresh_visuals()

    @property
    def display_name(self) -> str:
        return f"{self.index + 1}번 밭"

    def is_empty(self) -> bool:
        return self.stage == 0

    def is_care_target(self) -> bool:
        return 0 < self.stage < 4

    def is_ready(self) -> bool:
        return self.stage == 4

    def has_companion(self) -> bool:
        return self.companion is not None

    def plant(self, crop: dict, grade: str) -> None:
        self.crop = crop
        self.seed_grade = grade
        self.stage = 1
        self.growth_points = 20 if grade == "희귀" else 0
        self.vitality_points = 12 if grade == "희귀" else 0
        self.affinity = max(self.affinity, 4)
        self.care_marks = {tag: False for tag in self.CARE_TAGS}
        self._refresh_visuals()

    def apply_care(self, amount: int, tag: str, *, flavor_bonus: int = 0) -> dict:
        if not self.is_care_target():
            return {"applied": False}
        prev_stage = self.stage
        bonus = self._companion_bonus(tag)
        self.growth_points += amount + bonus
        self.vitality_points += max(0, amount // 2) + flavor_bonus + max(0, bonus // 2)
        if self.companion:
            if tag in self.COMPANION_BONUS.get(self.companion["trait"], {}):
                self.affinity = min(120, self.affinity + 12)
            else:
                self.affinity = min(120, self.affinity + 4)
        matured = self._check_growth()
        self.care_marks[tag] = True
        self._refresh_visuals()
        return {
            "applied": True,
            "bonus": bonus,
            "stage_changed": self.stage != prev_stage,
            "matured": matured,
        }

    def advance_day(self, weather: dict) -> bool:
        matured = False
        if self.is_care_target():
            if not self.care_marks["water"] and weather["dry_penalty"]:
                self.growth_points = max(
                    self.STAGE_THRESHOLDS[self.stage] - 5,
                    self.growth_points - weather["dry_penalty"],
                )
                self.vitality_points = max(0, self.vitality_points - 6)
            self.growth_points += weather["daily_bonus"]
            self.vitality_points += weather["vitality_bonus"]
            if self.companion:
                trait = self.companion["trait"]
                if trait == "sun":
                    self.growth_points += weather.get("sun_bonus", 0)
                if trait == "swift":
                    self.vitality_points += 2
                self.affinity = min(120, self.affinity + weather.get("companion_favor", 0))
            prev_stage = self.stage
            matured = self._check_growth() and self.stage == 4 and prev_stage != 4
        self.care_marks = {tag: False for tag in self.CARE_TAGS}
        self._refresh_visuals()
        return matured

    def harvest(self) -> dict | None:
        if not self.is_ready() or self.crop is None:
            return None
        base_quality = 1 if self.seed_grade == "희귀" else 0
        quality_score = base_quality + self.vitality_points // 30
        if self.affinity >= 60:
            quality_score += 1
        if self.companion and self.companion["trait"] == "muse":
            quality_score += 1
        quality_score = max(0, min(3, quality_score))
        reward = {
            "crop": self.crop["name"],
            "quality": quality_score,
            "flavor": self.crop["flavor"],
        }
        self.stage = 0
        self.crop = None
        self.seed_grade = None
        self.growth_points = 0
        self.vitality_points = 0
        self.affinity = max(0, self.affinity // 2)
        self.care_marks = {tag: False for tag in self.CARE_TAGS}
        self._refresh_visuals()
        return reward

    def assign_companion(self, companion: dict) -> None:
        self.companion = companion
        self.affinity = max(self.affinity, 10)
        self.companion_badge.alpha = 255
        self.companion_badge.color = companion.get("color", Cs.dark(Cs.gray))
        trait_text = self.COMPANION_TAG_TEXT.get(companion["trait"], "친구")
        self.companion_text.text = f"{companion['name']}\n<{trait_text}>"
        self.companion_text.center = self.companion_badge.offsetRect.center

        self._refresh_visuals()

    def _companion_bonus(self, tag: str) -> int:
        if not self.companion:
            return 0
        return self.COMPANION_BONUS.get(self.companion["trait"], {}).get(tag, 0)

    def _check_growth(self) -> bool:
        matured = False
        while self.stage < 4 and self.growth_points >= self.STAGE_THRESHOLDS[self.stage + 1]:
            self.stage += 1
            matured = self.stage == 4
        return matured

    def _refresh_visuals(self) -> None:
        label, base_color = self.STAGE_INFO[self.stage]
        self._base_color = base_color
        self._hover_color = Cs.light(base_color)
        if self.color != base_color:
            self.color = base_color
        if self.stage == 0:
            self.stage_text.text = "텅 비어 있음"
            self.crop_text.text = "씨앗을 심어보세요."
            self.stage_text.center = self.offsetRect.center

        elif self.stage == 1:
            self.stage_text.text = f"{self.crop['name']} 씨앗"
            self.stage_text.center = self.offsetRect.center

            grade = self.seed_grade or "일반"
            self.crop_text.text = f"{grade} 씨앗 / 성장 준비 중"
        elif self.stage == 2:
            self.stage_text.text = f"{self.crop['name']} 새싹"
            
            self.crop_text.text = "물과 햇살이 필요해요."
        elif self.stage == 3:
            self.stage_text.text = f"{self.crop['name']} 꽃봉오리"
            self.crop_text.text = "향기로운 영양제를 좋아합니다."
        else:
            quality_hint = "향기롭다" if self.affinity >= 40 else "수확 가능"
            self.stage_text.text = f"{self.crop['name']}"
            self.crop_text.text = f"{quality_hint}! 수확 카드를 사용하세요."
        if self.is_care_target():
            lower = self.STAGE_THRESHOLDS[self.stage]
            upper = self.STAGE_THRESHOLDS[self.stage + 1]
            span = max(1, upper - lower)
            ratio = (self.growth_points - lower) / span
            ratio = max(0.0, min(1.0, ratio))
            fill_width = int(176 * ratio)
            self.progress_fill.width = max(8, fill_width)
            self.progress_bg.alpha = 220
            self.progress_fill.alpha = 240
            self.progress_text.text = f"성장 {int(ratio * 100)}%"
        elif self.stage == 4:
            self.progress_bg.alpha = 220
            self.progress_fill.width = 176
            self.progress_fill.alpha = 255
            self.progress_text.text = "완전 성숙"
        else:
            self.progress_bg.alpha = 0
            self.progress_fill.alpha = 0
            self.progress_text.text = ""
        if not self.companion:
            self.companion_badge.alpha = 120
            self.companion_text.text = "동행 친구 없음"
            self.companion_text.center = self.companion_badge.offsetRect.center
        
        self.adjust_ui()

        return
    
    def adjust_ui(self):
        self.stage_text.center = self.offsetRect.center + RPoint(0,20)
        self.companion_text.center = self.companion_badge.offsetRect.center
        self.crop_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)


    def update(self) -> None:
        hovered = self.collideMouse()
        target = self._hover_color if hovered else self._base_color
        if self.color != target:
            self.color = target
        return


class CareCard(rectObj):
    """농장 케어 행동을 표현하는 카드."""

    def __init__(
        self,
        name: str,
        cost: int,
        description: str,
        *,
        color: tuple[int, int, int] = Cs.dark(Cs.darkslategray),
        tags: tuple[str, ...] = (),
        can_play: callable,
        on_play: callable,
    ) -> None:
        super().__init__(pygame.Rect(0, 0, 210, 280), color=color, edge=6, radius=26)
        self.name = name
        self.cost = cost
        self.description = description
        self.tags = tags
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
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 96)

        self.desc_text = longTextObj(description, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=160)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.title_text.rect.bottom + 12

        tag_text = ", ".join(tags) if tags else ""
        self.tag_text = textObj(tag_text, size=20, color=Cs.light(Cs.lightcyan))
        self.tag_text.setParent(self, depth=1)
        self.tag_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 16)

    def update(self) -> None:
        available = self._can_play()
        hovered = self.collideMouse()
        target_color = self._hover_color if hovered and available else self._base_color
        if self.color != target_color:
            self.color = target_color

        alpha = 255 if available else 150
        if self.alpha != alpha:
            self.alpha = alpha

        if hovered and available and Rs.userJustLeftClicked():
            self._on_play()
        return


class PocketRanchScene(Scene):
    MAX_LOG = 7

    def initOnce(self) -> None:
        self.day = 1
        self.max_energy = 5
        self.energy = self.max_energy
        self.seeds = 5
        self.rare_seeds = 1
        self.coins = 6
        self.reputation = 0
        self.weather = random.choice(WEATHERS)
        self.weather_modifiers = dict(self.weather)
        self.waiting_companions = [
            dict(comp)
            for comp in random.sample(COMPANION_LIBRARY, min(2, len(COMPANION_LIBRARY)))
        ]
        self.energy_unlocks: set[int] = set()
        self.storage_counts = [0, 0, 0, 0]
        self.log_messages: list[str] = []

        self.field_panel = rectObj(
            pygame.Rect(0, 0, 1320, 520), color=Cs.dark(Cs.darkolivegreen), edge=6, radius=32
        )
        self.field_panel.centerx = 1920 // 2 + 280
        self.field_panel.y = 120

        self.card_panel = rectObj(
            pygame.Rect(0, 0, 1320, 300), color=Cs.dark(Cs.slategray), edge=6, radius=30
        )
        self.card_panel.centerx = 1920 // 2 + 280
        self.card_panel.y = 700

        self.status_layout = layoutObj(pos=RPoint(120, 60), spacing=12, isVertical=True)
        self.day_text = textObj("", size=34, color=Cs.white)
        self.weather_line = textObj("", size=24, color=Cs.light(Cs.lightcyan))
        self.energy_text = textObj("", size=26, color=Cs.light(Cs.lightgoldenrodyellow))
        self.seed_text = textObj("", size=24, color=Cs.light(Cs.palegreen))
        self.inventory_text = textObj("", size=24, color=Cs.light(Cs.orange))
        self.coin_text = textObj("", size=24, color=Cs.light(Cs.skyblue))
        self.reputation_text = textObj("", size=24, color=Cs.light(Cs.plum))
        self.companion_queue_text = textObj("", size=22, color=Cs.light(Cs.lightsteelblue))
        for label in (
            self.day_text,
            self.weather_line,
            self.energy_text,
            self.seed_text,
            self.inventory_text,
            self.coin_text,
            self.reputation_text,
            self.companion_queue_text,
        ):
            label.setParent(self.status_layout)
        self.status_layout.adjustLayout()

        self.weather_box = rectObj(
            pygame.Rect(0, 0, 520, 200), color=Cs.dark(Cs.midnightblue), edge=4, radius=28
        )
        self.weather_box.pos = RPoint(40, 350)
        self.weather_title = textObj("", size=30, color=Cs.white)
        self.weather_title.setParent(self.weather_box, depth=1)
        self.weather_title.pos = RPoint(20, 24)
        self.weather_desc = longTextObj("", pos=RPoint(0, 0), size=20, color=Cs.light(Cs.lightcyan), textWidth=440)
        self.weather_desc.setParent(self.weather_box, depth=1)
        self.weather_desc.pos = self.weather_title.pos + RPoint(0,42)

        self.tip_panel = rectObj(
            pygame.Rect(0, 0, 520, 200), color=Cs.dark(Cs.darkslategray), edge=4, radius=28
        )
        self.tip_panel.pos = RPoint(40, 500)
        self.tip_text = longTextObj(
            "포켓 목장 운영법:\n- 씨앗, 물, 햇살, 영양제를 조합하여 성장 단계를 올려보세요.\n"
            "- 친구의 특성에 맞는 케어를 하면 친밀도가 올라 품질이 향상됩니다.\n"
            "- SPACE 또는 [다음 날] 버튼으로 하루를 마감할 수 있습니다.",
            pos=self.tip_panel.pos + RPoint(24, 24),
            size=20,
            color=Cs.white,
            textWidth=472,
        )

        self.log_box_bg = rectObj(
            pygame.Rect(0, 0, 520, 220), color=Cs.dark(Cs.black), edge=4, radius=24
        )
        self.log_box_bg.pos = RPoint(40, 720)
        self.log_box = longTextObj("", pos=self.log_box_bg.pos + RPoint(24, 24), size=22, color=Cs.white, textWidth=472)

        self.field_rows: list[layoutObj] = []
        self.fields: list[PocketPlot] = []
        for row in range(2):
            row_layout = layoutObj(
                pos=RPoint(self.field_panel.rect.x + 80, self.field_panel.rect.y + 30 + row * 270),
                spacing=60,
                isVertical=False,
            )
            self.field_rows.append(row_layout)
        for index in range(6):
            plot = PocketPlot(index)
            plot.setParent(self.field_rows[index // 3])
            self.fields.append(plot)
        for row_layout in self.field_rows:
            row_layout.adjustLayout()

        self.card_layout = cardLayout(
            RPoint(self.card_panel.rect.x + 80, self.card_panel.rect.y + 40),
            spacing=36,
            maxWidth=1160,
            isVertical=False,
        )
        self.action_cards: list[CareCard] = []

        self.end_day_button = monoTextButton("다음 날", pos=(1560, 80), size=32, color=Cs.orange)
        self.end_day_button.connect(self._start_next_day)

        self._create_cards()
        self._set_weather(self.weather)
        self._refresh_status()
        self._log("포켓 목장에 오신 것을 환영합니다! 첫날이 시작되었어요.")

    def init(self) -> None:
        return

    def _create_cards(self) -> None:
        def add_card(**kwargs):
            card = CareCard(**kwargs)
            card.setParent(self.card_layout)
            self.action_cards.append(card)

        add_card(
            name="씨앗 뿌리기",
            cost=1,
            description="빈 밭에 씨앗을 심습니다. 희귀 씨앗이 있다면 우선 사용합니다.",
            color=Cs.dark(Cs.sienna),
            tags=("plant",),
            can_play=lambda: self.energy >= 1
            and any(field.is_empty() for field in self.fields)
            and (self.seeds > 0 or self.rare_seeds > 0),
            on_play=self._play_plant,
        )

        add_card(
            name="포켓 친구 부르기",
            cost=1,
            description="대기 중인 친구를 선택한 밭에 배치합니다.",
            color=Cs.dark(Cs.blueviolet),
            tags=("friend",),
            can_play=lambda: self.energy >= 1
            and bool(self.waiting_companions)
            and any(not field.has_companion() for field in self.fields),
            on_play=self._play_call_companion,
        )

        add_card(
            name="물과 선율",
            cost=1,
            description="선택된 밭 여러 곳에 시원한 물과 노래를 선사합니다.",
            color=Cs.dark(Cs.teal),
            tags=("water",),
            can_play=lambda: self.energy >= 1
            and any(field.is_care_target() and not field.care_marks["water"] for field in self.fields),
            on_play=self._play_water,
        )

        add_card(
            name="햇살 모으기",
            cost=1,
            description="꽃봉오리 위주로 햇살을 모아 빠르게 성장을 돕습니다.",
            color=Cs.dark(Cs.goldenrod),
            tags=("sun",),
            can_play=lambda: self.energy >= 1
            and any(field.is_care_target() and field.stage >= 2 and not field.care_marks["sun"] for field in self.fields),
            on_play=self._play_sun,
        )

        add_card(
            name="향기로운 영양제",
            cost=2,
            description="특수 영양제를 뿌려 활력과 성장을 동시에 올립니다.",
            color=Cs.dark(Cs.seagreen),
            tags=("tonic",),
            can_play=lambda: self.energy >= 2
            and any(field.is_care_target() and field.stage >= 2 and not field.care_marks["tonic"] for field in self.fields),
            on_play=self._play_tonic,
        )

        add_card(
            name="수확 & 포장",
            cost=1,
            description="수확 가능한 작물을 모두 포장하여 시장에 보냅니다.",
            color=Cs.dark(Cs.olivedrab),
            tags=("harvest",),
            can_play=lambda: self.energy >= 1 and any(field.is_ready() for field in self.fields),
            on_play=self._play_harvest,
        )

        add_card(
            name="연구 노트",
            cost=1,
            description="고급 수확물이나 동전을 연구해 더 많은 씨앗을 얻습니다.",
            color=Cs.dark(Cs.rebeccapurple),
            tags=("study",),
            can_play=lambda: self.energy >= 1
            and (
                self.storage_counts[2] > 0
                or self.storage_counts[3] > 0
                or self.coins >= 4
            ),
            on_play=self._play_research,
        )

        self.card_layout.adjustLayout()

    def _set_weather(self, weather: dict) -> None:
        self.weather = weather
        self.weather_modifiers = dict(weather)
        self.weather_title.text = weather["name"]
        self.weather_desc.text = weather["description"]
        self.weather_line.text = f"오늘 날씨: {weather['name']}"

    def _refresh_status(self) -> None:
        self.energy = min(self.energy, self.max_energy)
        total_storage = sum(self.storage_counts)
        self.day_text.text = f"{self.day}일차"
        self.energy_text.text = f"에너지: {self.energy}/{self.max_energy}"
        self.seed_text.text = f"씨앗: 일반 {self.seeds} / 희귀 {self.rare_seeds}"
        self.inventory_text.text = (
            f"수확물: {total_storage}상자 (고급 {self.storage_counts[1]}, "
            f"특급 {self.storage_counts[2]}, 전설 {self.storage_counts[3]})"
        )
        self.coin_text.text = f"시장 동전: {self.coins}"
        self.reputation_text.text = f"평판: {self.reputation}"
        if self.waiting_companions:
            names = ", ".join(friend["name"] for friend in self.waiting_companions)
        else:
            names = "없음"
        self.companion_queue_text.text = f"대기 친구: {names}"

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
        empty_fields = [field for field in self.fields if field.is_empty()]
        if not empty_fields:
            self._log("씨앗을 심을 빈 밭이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        use_rare = self.rare_seeds > 0 and (self.seeds == 0 or random.random() < 0.35)
        if use_rare:
            self.rare_seeds -= 1
            grade = "희귀"
        else:
            if self.seeds <= 0:
                self._log("씨앗이 부족합니다.")
                self.energy += 1
                self._refresh_status()
                return
            self.seeds -= 1
            grade = "일반"
        crop = random.choice(CROPS)
        target = min(empty_fields, key=lambda f: f.affinity)
        target.plant(crop, grade)
        if target.has_companion():
            target.affinity = min(120, target.affinity + 6)
        self._refresh_status()
        self._log(f"{target.display_name}에 {grade} {crop['name']} 씨앗을 심었습니다.")

    def _play_call_companion(self) -> None:
        if not self.waiting_companions:
            self._log("대기 중인 포켓 친구가 없습니다.")
            return
        open_fields = [field for field in self.fields if not field.has_companion()]
        if not open_fields:
            self._log("모든 밭이 이미 친구와 함께합니다.")
            return
        if not self._consume_energy(1):
            return
        companion = dict(self.waiting_companions.pop(0))
        target = sorted(open_fields, key=lambda f: (f.is_empty(), f.index))[0]
        target.assign_companion(companion)
        if target.is_care_target():
            target.affinity = min(120, target.affinity + 8)
        self._maybe_add_companion()
        self._refresh_status()
        self._log(f"{target.display_name}에 {companion['name']}이(가) 합류했습니다!")

    def _play_water(self) -> None:
        targets = [field for field in self.fields if field.is_care_target() and not field.care_marks["water"]]
        if not targets:
            self._log("물을 줄 만한 밭이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        limit = 2
        if any(field.has_companion() and field.companion["trait"] == "swift" for field in self.fields):
            limit += 1
        growth_amount = 26 + self.weather_modifiers.get("water_bonus", 0)
        chosen = sorted(targets, key=lambda f: (f.stage, f.affinity), reverse=True)[:limit]
        messages: list[str] = []
        for plot in chosen:
            result = plot.apply_care(growth_amount, "water", flavor_bonus=self.weather_modifiers.get("vitality_bonus", 0))
            if result["applied"]:
                text = f"{plot.display_name} 물주기 (+{growth_amount + result['bonus']} 성장)"
                if result["stage_changed"]:
                    text += " / 성장!"
                messages.append(text)
        if messages:
            self._log(" · ".join(messages))
        else:
            self._log("물 효과가 미미했습니다.")

    def _play_sun(self) -> None:
        targets = [
            field
            for field in self.fields
            if field.is_care_target() and field.stage >= 2 and not field.care_marks["sun"]
        ]
        if not targets:
            self._log("햇살을 비출 밭이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        growth_amount = 22 + self.weather_modifiers.get("sun_bonus", 0)
        chosen = sorted(targets, key=lambda f: (f.stage, f.affinity), reverse=True)[:2]
        messages: list[str] = []
        for plot in chosen:
            result = plot.apply_care(growth_amount, "sun", flavor_bonus=self.weather_modifiers.get("vitality_bonus", 0))
            if result["applied"]:
                text = f"{plot.display_name} 햇살욕 (+{growth_amount + result['bonus']} 성장)"
                if result["stage_changed"]:
                    text += " / 꽃이 맺힙니다!"
                messages.append(text)
        self._log(" · ".join(messages))

    def _play_tonic(self) -> None:
        targets = [
            field
            for field in self.fields
            if field.is_care_target() and field.stage >= 2 and not field.care_marks["tonic"]
        ]
        if not targets:
            self._log("영양제를 줄 밭이 없습니다.")
            return
        if not self._consume_energy(2):
            return
        chosen = max(targets, key=lambda f: (f.stage, f.vitality_points))
        vitality_bonus = 6 + self.weather_modifiers.get("vitality_bonus", 0)
        result = chosen.apply_care(24, "tonic", flavor_bonus=vitality_bonus)
        message = f"{chosen.display_name}에 영양제를 뿌려 활력 {vitality_bonus} 확보"
        if result["stage_changed"]:
            message += " / 성장!"
        self._log(message)

    def _play_harvest(self) -> None:
        ready = [field for field in self.fields if field.is_ready()]
        if not ready:
            self._log("수확할 작물이 없습니다.")
            return
        if not self._consume_energy(1):
            return
        harvested: list[str] = []
        bonuses: list[str] = []
        for plot in ready:
            reward = plot.harvest()
            if not reward:
                continue
            quality = reward["quality"]
            self.storage_counts[quality] += 1
            earned = 4 + quality * 2
            self.coins += earned
            self.reputation += 1 + quality
            label = f"{reward['crop']} ({QUALITY_LABELS[quality]})"
            harvested.append(label)
            if quality >= 2 and random.random() < 0.4:
                self.rare_seeds += 1
                bonuses.append("희귀 씨앗 발견!")
        self._maybe_unlock_energy()
        self._refresh_status()
        summary = "수확 완료: " + ", ".join(harvested)
        if bonuses:
            summary += " · " + " · ".join(bonuses)
        self._log(summary)

    def _play_research(self) -> None:
        if not self._consume_energy(1):
            return
        summary = None
        if self.storage_counts[3] > 0:
            self.storage_counts[3] -= 1
            self.rare_seeds += 1
            summary = "전설 상자를 해체하여 희귀 씨앗을 확보했습니다."
        elif self.storage_counts[2] > 0:
            self.storage_counts[2] -= 1
            self.seeds += 2
            summary = "특급 수확물을 연구해 씨앗 2개를 얻었습니다."
        elif self.coins >= 4:
            self.coins -= 4
            self.seeds += 2
            summary = "시장 자료를 구입해 씨앗 2개를 얻었습니다."
        else:
            summary = "연구 자료가 부족해 성과가 없었습니다."
        self._refresh_status()
        self._log(summary)

    def _maybe_add_companion(self) -> None:
        while len(self.waiting_companions) < 2:
            candidate = dict(random.choice(COMPANION_LIBRARY))
            self.waiting_companions.append(candidate)

    def _maybe_unlock_energy(self) -> None:
        thresholds = {9: 6, 18: 7}
        for requirement, new_max in thresholds.items():
            if self.reputation >= requirement and requirement not in self.energy_unlocks:
                self.energy_unlocks.add(requirement)
                self.max_energy = new_max
                self.energy = self.max_energy
                self._log(f"평판이 올라 하루 에너지가 {self.max_energy}로 증가했습니다!")

    def _start_next_day(self) -> None:
        self.day += 1
        matured_count = 0
        for plot in self.fields:
            if plot.advance_day(self.weather_modifiers):
                matured_count += 1
        self.energy = self.max_energy
        self._maybe_add_companion()
        self._refresh_status()
        if matured_count:
            self._log(f"새로운 하루! {matured_count}개의 밭이 수확 준비를 마쳤습니다.")
        else:
            self._log("새로운 하루가 시작되었지만 조금 더 보살핌이 필요합니다.")
        self._set_weather(random.choice(WEATHERS))

    def update(self) -> None:
        if Rs.userJustPressed(pygame.K_SPACE):
            self._start_next_day()
        self.status_layout.update()
        for row_layout in self.field_rows:
            row_layout.update()
        self.card_layout.adjustLayout()
        self.card_layout.update()
        self.end_day_button.update()
        return

    def draw(self) -> None:
        self.field_panel.draw()
        for row_layout in self.field_rows:
            row_layout.draw()
        self.card_panel.draw()
        self.card_layout.draw()
        self.end_day_button.draw()
        self.status_layout.draw()
        self.weather_box.draw()
        self.weather_title.draw()
        self.weather_desc.draw()
        self.tip_panel.draw()
        self.tip_text.draw()
        self.log_box_bg.draw()
        self.log_box.draw()
        return


class Scenes:
    mainScene = PocketRanchScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="포켓 목장 프로토타입")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
