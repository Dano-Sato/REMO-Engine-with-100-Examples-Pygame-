from __future__ import annotations

import random
from dataclasses import dataclass

from REMOLib import *


@dataclass(frozen=True)
class CardSpec:
    name: str
    cost: int
    card_type: str
    description: str
    sell_value: int = 0
    is_product: bool = False
    action_cost: dict[str, int] | None = None
    action_gain: dict[str, int] | None = None
    draw_cards: int = 0
    craft_product: str | None = None
    auction: bool = False
    trash_cards: int = 0
    crafted_bonus: int = 0


class CardInstance:
    def __init__(self, spec: CardSpec, sell_bonus: int = 0) -> None:
        self.spec = spec
        self.sell_bonus = sell_bonus

    @property
    def sell_value(self) -> int:
        return self.spec.sell_value + self.sell_bonus


class ModeButton(rectObj):
    def __init__(self, label: str, mode_key: str, on_click: callable) -> None:
        super().__init__(pygame.Rect(0, 0, 160, 48), color=Cs.dark(Cs.steelblue), edge=4, radius=16)
        self.mode_key = mode_key
        self._on_click = on_click
        self._base_color = self.color
        self._hover_color = Cs.light(self._base_color)
        self.label = textObj(label, size=22, color=Cs.white)
        self.label.setParent(self, depth=1)
        self.label.center = self.offsetRect.center

    def set_active(self, active: bool) -> None:
        self.color = Cs.dark(Cs.orange) if active else self._base_color

    def update(self) -> None:
        hovered = self.collideMouse()
        if hovered and Rs.userJustLeftClicked():
            self._on_click(self.mode_key)
        target_color = self._hover_color if hovered else self.color
        if self.color != target_color and self.color != Cs.dark(Cs.orange):
            self.color = target_color
        if self.color == Cs.dark(Cs.orange) and hovered:
            self.color = Cs.light(Cs.orange)


class ActionButton(rectObj):
    def __init__(self, label: str, on_click: callable) -> None:
        super().__init__(pygame.Rect(0, 0, 180, 52), color=Cs.dark(Cs.darkslategray), edge=4, radius=16)
        self._on_click = on_click
        self._base_color = self.color
        self._hover_color = Cs.light(self._base_color)
        self.label = textObj(label, size=24, color=Cs.white)
        self.label.setParent(self, depth=1)
        self.label.center = self.offsetRect.center

    def update(self) -> None:
        hovered = self.collideMouse()
        if hovered and Rs.userJustLeftClicked():
            self._on_click()
        target_color = self._hover_color if hovered else self._base_color
        if self.color != target_color:
            self.color = target_color


class WorkshopCard(rectObj):
    WIDTH = 200
    HEIGHT = 280

    def __init__(self, card: CardInstance, on_click: callable, is_market: bool) -> None:
        self.card = card
        self._on_click = on_click
        self.is_market = is_market
        super().__init__(pygame.Rect(0, 0, self.WIDTH, self.HEIGHT), color=self._base_color(), edge=5, radius=20)
        self._hover_color = Cs.light(self.color)

        self.title_text = textObj(card.spec.name, size=22, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 16)

        self.type_text = textObj(card.spec.card_type, size=18, color=Cs.light(Cs.silver))
        self.type_text.setParent(self, depth=1)
        self.type_text.midtop = self.title_text.midbottom + RPoint(0, 6)

        badge_color = Cs.dark(Cs.black)
        self.cost_badge = rectObj(pygame.Rect(0, 0, 58, 58), radius=16, edge=4, color=badge_color)
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.pos = self.offsetRect.topleft

        self.cost_text = textObj("", size=24, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.desc_text = longTextObj("", pos=RPoint(0, 0), size=18, color=Cs.white, textWidth=160)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.type_text.rect.bottom + 12

        self.sell_text = textObj("", size=18, color=Cs.light(Cs.gold))
        self.sell_text.setParent(self, depth=1)
        self.sell_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 16)

        self.refresh()

    def _base_color(self) -> tuple[int, int, int]:
        if self.card.spec.is_product:
            return Cs.dark(Cs.teal)
        return Cs.dark(Cs.steelblue)

    def refresh(self) -> None:
        self.title_text.text = self.card.spec.name
        self.type_text.text = self.card.spec.card_type
        if self.is_market:
            self.cost_text.text = str(self.card.spec.cost)
            self.sell_text.text = "구매 카드"
        else:
            if self.card.spec.is_product:
                self.cost_text.text = "판매"
                self.sell_text.text = f"판매가 {self.card.sell_value}G"
            else:
                self.cost_text.text = "액션"
                self.sell_text.text = "사용 후 버림"

        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(30, 16)

        self.cost_text.center = self.cost_badge.offsetRect.center
        self.desc_text.text = self.card.spec.description
        self.desc_text.centerx = self.offsetRect.centerx

    def update(self, available: bool) -> None:
        hovered = self.collideMouse()
        if hovered and available and Rs.userJustLeftClicked():
            self._on_click(self)
        target_color = self._hover_color if hovered and available else self._base_color()
        if self.color != target_color:
            self.color = target_color
        alpha = 255 if available else 140
        if self.alpha != alpha:
            self.alpha = alpha
            self.title_text.alpha = alpha
            self.type_text.alpha = alpha
            self.desc_text.alpha = alpha
            self.cost_badge.alpha = alpha
            self.cost_text.alpha = alpha
            self.sell_text.alpha = alpha


class WorkshopScene(Scene):
    MAX_LOG = 7

    def initOnce(self) -> None:
        self.turn = 1
        self.mode = "action"
        self.gear = 0
        self.metal = 0
        self.mana = 0
        self.gold = 10
        self.actions = 1
        self.buys = 1
        self.sells = 1
        self.crafted_bonus = 0
        self.first_craft_bonus = 0
        self.first_craft_pending = False
        self.craft_gold_bonus = 0
        self.sell_gold_bonus = 0
        self.first_sale_bonus = 0
        self.first_sale_pending = False
        self.auction_remaining = 0
        self.auction_bonus = 0
        self.trash_remaining = 0
        self.enchant_remaining = 0
        self.enchant_bonus = 0

        self.logs: list[str] = []

        self.title = textObj("스팀펑크 마법공학 공방", size=36, color=Cs.white)
        self.title.midtop = (960, 16)

        self.resource_text = longTextObj("", pos=RPoint(40, 20), size=20, color=Cs.white, textWidth=520)
        self.mode_text = textObj("", size=22, color=Cs.light(Cs.yellow))
        self.mode_text.midtop = (960, 64)

        self.log_text = longTextObj("", pos=RPoint(40, 780), size=20, color=Cs.light(Cs.lightgoldenrodyellow), textWidth=500)

        self.mode_buttons = []
        button_data = [("액션", "action"), ("구매", "buy"), ("판매", "sell")]
        for idx, (label, key) in enumerate(button_data):
            button = ModeButton(label, key, self.set_mode)
            button.pos = (640 + idx * 180, 100)
            self.mode_buttons.append(button)

        self.end_turn_button = ActionButton("정리", self.end_turn)
        self.end_turn_button.pos = (1200, 96)

        self.card_specs = self._build_card_specs()
        self.start_deck = [
            self._make_card("잔돈 주머니") for _ in range(3)
        ] + [
            self._make_card("고철 수집") for _ in range(2)
        ] + [
            self._make_card("톱니 수집") for _ in range(2)
        ] + [
            self._make_card("마나 불씨")
        ]

        self.deck = self.start_deck[:]
        random.shuffle(self.deck)
        self.discard: list[CardInstance] = []
        self.hand: list[CardInstance] = []
        self.market: list[CardInstance] = []

        self.draw_cards(5)
        self.refresh_market()
        self._rebuild_widgets()
        self.add_log("공방 운영을 시작합니다!")
        self._refresh_ui()

    def _build_card_specs(self) -> dict[str, CardSpec]:
        def action_cost(**kwargs) -> dict[str, int]:
            return dict(kwargs)

        def action_gain(**kwargs) -> dict[str, int]:
            return dict(kwargs)

        specs = {
            "자동인형 C형": CardSpec(
                name="자동인형 C형",
                cost=0,
                card_type="상품",
                description="액션: 톱니-4 금속-3 마나-2 / 자동인형 A형 제작",
                sell_value=15,
                is_product=True,
                action_cost=action_cost(gear=4, metal=3, mana=2),
                craft_product="자동인형 A형",
            ),
            "자동인형 A형": CardSpec(
                name="자동인형 A형",
                cost=0,
                card_type="상품",
                description="액션: 금속-1 마나-1 / 톱니+2",
                sell_value=9,
                is_product=True,
                action_cost=action_cost(metal=1, mana=1),
                action_gain=action_gain(gear=2),
            ),
            "자동인형 B형": CardSpec(
                name="자동인형 B형",
                cost=0,
                card_type="상품",
                description="액션: 톱니-1 마나-1 금속-1 / 작은 자동인형 제작",
                sell_value=11,
                is_product=True,
                action_cost=action_cost(gear=1, mana=1, metal=1),
                craft_product="작은 자동인형",
            ),
            "작은 자동인형": CardSpec(
                name="작은 자동인형",
                cost=0,
                card_type="상품",
                description="판매 전용",
                sell_value=6,
                is_product=True,
            ),
            "브로치": CardSpec(
                name="브로치",
                cost=0,
                card_type="상품",
                description="판매 전용",
                sell_value=7,
                is_product=True,
            ),
            "작업반장": CardSpec(
                name="작업반장",
                cost=3,
                card_type="인물",
                description="액션 +2, 카드+1",
                draw_cards=1,
                action_gain=action_gain(actions=2),
            ),
            "마이스터": CardSpec(
                name="마이스터",
                cost=6,
                card_type="인물",
                description="카드+1 액션+2 / 이번 턴 첫 제작 상품 가치 +6",
                draw_cards=1,
                action_gain=action_gain(actions=2),
            ),
            "공장 감독관": CardSpec(
                name="공장 감독관",
                cost=4,
                card_type="인물",
                description="카드+1 액션+2 / 이번 턴 제작 상품 1장당 골드+1",
                draw_cards=1,
                action_gain=action_gain(actions=2),
            ),
            "감정사": CardSpec(
                name="감정사",
                cost=3,
                card_type="인물",
                description="카드+1 액션+1 / 이번 턴 첫 상품 판매시 골드+3",
                draw_cards=1,
                action_gain=action_gain(actions=1),
            ),
            "정보상": CardSpec(
                name="정보상",
                cost=3,
                card_type="인물",
                description="카드+2 액션+2",
                draw_cards=2,
                action_gain=action_gain(actions=2),
            ),
            "밀수업자": CardSpec(
                name="밀수업자",
                cost=4,
                card_type="인물",
                description="골드+2 카드+1 액션+1",
                draw_cards=1,
                action_gain=action_gain(gold=2, actions=1),
            ),
            "장물상": CardSpec(
                name="장물상",
                cost=3,
                card_type="인물",
                description="골드+1 판매+1",
                action_gain=action_gain(gold=1, sells=1),
            ),
            "대장장이": CardSpec(
                name="대장장이",
                cost=4,
                card_type="인물",
                description="액션 +3",
                action_gain=action_gain(actions=3),
            ),
            "상인": CardSpec(
                name="상인",
                cost=3,
                card_type="인물",
                description="골드 +2",
                action_gain=action_gain(gold=2),
            ),
            "대상인": CardSpec(
                name="대상인",
                cost=6,
                card_type="인물",
                description="골드 +3, 판매+1, 구매+1",
                action_gain=action_gain(gold=3,sells=1,buys=1),
            ),
            "마정석 코어": CardSpec(
                name="마정석 코어",
                cost=6,
                card_type="장치",
                description="마나 +3",
                action_gain=action_gain(mana=3),
            ),
            "톱니 제련소": CardSpec(
                name="톱니 제련소",
                cost=5,
                card_type="시설",
                description="금속-1 마나-1 / 톱니+3",
                action_cost=action_cost(metal=1, mana=1),
                action_gain=action_gain(gear=3),
            ),
            "금속 공급 계약": CardSpec(
                name="금속 공급 계약",
                cost=3,
                card_type="계약",
                description="골드-4 / 금속+2 액션+1",
                action_cost=action_cost(gold=4),
                action_gain=action_gain(metal=2, actions=1),
            ),
            "금속 채굴권": CardSpec(
                name="금속 채굴권",
                cost=4,
                card_type="계약",
                description="금속+2 액션+1",
                action_gain=action_gain(metal=2, actions=1),
            ),
            "톱니 판매 계약": CardSpec(
                name="톱니 판매 계약",
                cost=3,
                card_type="계약",
                description="톱니-3 / 골드+6 액션+1",
                action_cost=action_cost(gear=3),
                action_gain=action_gain(gold=6, actions=1),
            ),
            "금속 판매 계약": CardSpec(
                name="금속 판매 계약",
                cost=3,
                card_type="계약",
                description="금속-2 / 골드+6 액션+1",
                action_cost=action_cost(metal=2),
                action_gain=action_gain(gold=6, actions=1),
            ),
            "룬 주입": CardSpec(
                name="룬 주입",
                cost=3,
                card_type="의식",
                description="마나+1 / 이번 턴 제작 상품 가치 +2",
                action_gain=action_gain(mana=1),
                crafted_bonus=2,
            ),
            "룬 각인": CardSpec(
                name="룬 각인",
                cost=5,
                card_type="의식",
                description="손패의 상품 1장의 판매가 +3",
            ),
            "브로치 제작": CardSpec(
                name="브로치 제작",
                cost=3,
                card_type="공정",
                description="금속-1 마나-1 / 브로치 제작",
                action_cost=action_cost(metal=1, mana=1),
                craft_product="브로치",
            ),
            "경매장": CardSpec(
                name="경매장",
                cost=4,
                card_type="시설",
                description="상품 최대 3장 추가 2골드로 판매",
                auction=True,
            ),
            "작업장 정리": CardSpec(
                name="작업장 정리",
                cost=2,
                card_type="시설",
                description="손패에서 최대 2장 폐기",
                trash_cards=2,
            ),
            "마공학 연구실": CardSpec(
                name="마공학 연구실",
                cost=4,
                card_type="시설",
                description="카드+2 액션+1 마나+1",
                draw_cards=2,
                action_gain=action_gain(actions=1, mana=1),
            ),
            "유통망": CardSpec(
                name="유통망",
                cost=4,
                card_type="시설",
                description="구매+1 판매+1 액션+1",
                action_gain=action_gain(buys=1, sells=1, actions=1),
            ),
            "분해 작업": CardSpec(
                name="분해 작업",
                cost=3,
                card_type="시설",
                description="손패 카드 1장 폐기 / 금속+1 톱니+2",
                action_gain=action_gain(metal=1, gear=2),
                trash_cards=1,
            ),
            "설계실": CardSpec(
                name="설계실",
                cost=4,
                card_type="시설",
                description="덱 위 4장 확인 후 2장 손패 / 나머지 버림 액션+1",
                action_gain=action_gain(actions=1),
            ),
            "에테르 정제소": CardSpec(
                name="에테르 정제소",
                cost=4,
                card_type="시설",
                description="금속-1 / 골드+2, 마나+2 카드+1",
                action_cost=action_cost(metal=1),
                action_gain=action_gain(mana=2,gold=2),
                draw_cards=1,
            ),
            "증기압 조절기": CardSpec(
                name="증기압 조절기",
                cost=3,
                card_type="장치",
                description="마나-1 / 액션+3, 카드+2",
                action_cost=action_cost(mana=1),
                action_gain=action_gain(actions=3),
                draw_cards=2,
            ),
            "부품 프레스": CardSpec(
                name="부품 프레스",
                cost=3,
                card_type="장치",
                description="금속-1 / 표준 부품 제작",
                action_cost=action_cost(metal=1),
                craft_product="표준 부품",
            ),
            "시계 제작": CardSpec(
                name="시계 제작",
                cost=4,
                card_type="공정",
                description="톱니-2 금속-1 마나-1 / 기계식 시계 제작",
                action_cost=action_cost(gear=2, metal=1, mana=1),
                craft_product="기계식 시계",
            ),
            "룬 조각 정련": CardSpec(
                name="룬 조각 정련",
                cost=3,
                card_type="공정",
                description="마나-1 / 룬 조각 제작",
                action_cost=action_cost(mana=1),
                craft_product="룬 조각",
            ),
            "표준 부품": CardSpec(
                name="표준 부품",
                cost=0,
                card_type="상품",
                description="판매 전용",
                sell_value=3,
                is_product=True,
            ),
            "기계식 시계": CardSpec(
                name="기계식 시계",
                cost=0,
                card_type="상품",
                description="액션: 카드+1 액션+1",
                sell_value=14,
                is_product=True,
                draw_cards=1,
                action_gain=action_gain(actions=1),
            ),
            "룬 조각": CardSpec(
                name="룬 조각",
                cost=0,
                card_type="상품",
                description="액션: 마나+2",
                sell_value=4,
                is_product=True,
                action_gain=action_gain(mana=2),
            ),
            "일괄 납품": CardSpec(
                name="일괄 납품",
                cost=2,
                card_type="공정",
                description="판매+2 / 이번 턴 판매 상품 1장당 골드+1",
                action_gain=action_gain(sells=2),
            ),
            "잔돈 주머니": CardSpec(
                name="잔돈 주머니",
                cost=0,
                card_type="기본",
                description="골드+1, 액션+1",
                action_gain=action_gain(gold=1,actions=1),
            ),
            "고철 수집": CardSpec(
                name="고철 수집",
                cost=0,
                card_type="기본",
                description="금속+1",
                action_gain=action_gain(metal=1),
            ),
            "톱니 수집": CardSpec(
                name="톱니 수집",
                cost=0,
                card_type="기본",
                description="톱니+2",
                action_gain=action_gain(gear=2),
            ),
            "마나 불씨": CardSpec(
                name="마나 불씨",
                cost=0,
                card_type="기본",
                description="마나+1 카드+1, 액션+1",
                action_gain=action_gain(mana=1,actions=1),
                draw_cards=1,
            ),
        }
        return specs

    def _make_card(self, name: str, sell_bonus: int = 0) -> CardInstance:
        return CardInstance(self.card_specs[name], sell_bonus=sell_bonus)

    def has_action(self, spec: CardSpec) -> bool:
        return any(
            [
                spec.action_cost,
                spec.action_gain,
                spec.draw_cards,
                spec.craft_product,
                spec.crafted_bonus,
                spec.auction,
                spec.trash_cards,
                spec.name == "룬 각인",
            ]
        )

    def refresh_market(self) -> None:
        purchasable = [
            name
            for name, spec in self.card_specs.items()
            if spec.cost > 0 and not spec.is_product
        ]
        while len(self.market) < 6:
            choice = random.choice(purchasable)
            self.market.append(self._make_card(choice))

    def reset_market(self) -> None:
        self.market.clear()
        self.refresh_market()

    def _rebuild_widgets(self) -> None:
        self.hand_widgets = [WorkshopCard(card, self.on_hand_click, is_market=False) for card in self.hand]
        self.market_widgets = [WorkshopCard(card, self.on_market_click, is_market=True) for card in self.market]
        self.layout_cards()

    def layout_cards(self) -> None:
        for idx, widget in enumerate(self.market_widgets):
            widget.pos = (80 + idx * 220, 160)
        for idx, widget in enumerate(self.hand_widgets):
            widget.pos = (80 + idx * 220, 520)

    def add_log(self, message: str) -> None:
        self.logs.append(message)
        self.logs = self.logs[-self.MAX_LOG :]
        self.log_text.text = "\n".join(self.logs)

    def set_mode(self, mode: str) -> None:
        if self.trash_remaining > 0:
            self.add_log("폐기 모드 중에는 모드를 변경할 수 없습니다.")
            return
        if self.enchant_remaining > 0:
            self.add_log("각인 대상 선택 중에는 모드를 변경할 수 없습니다.")
            return
        self.mode = mode
        self.add_log(f"모드 변경: {mode}")
        self._refresh_ui()

    def can_pay(self, cost: dict[str, int] | None) -> bool:
        if not cost:
            return True
        return (
            self.gear >= cost.get("gear", 0)
            and self.metal >= cost.get("metal", 0)
            and self.mana >= cost.get("mana", 0)
            and self.gold >= cost.get("gold", 0)
        )

    def pay_cost(self, cost: dict[str, int] | None) -> None:
        if not cost:
            return
        self.gear -= cost.get("gear", 0)
        self.metal -= cost.get("metal", 0)
        self.mana -= cost.get("mana", 0)
        self.gold -= cost.get("gold", 0)

    def apply_gain(self, gain: dict[str, int] | None) -> None:
        if not gain:
            return
        self.gear += gain.get("gear", 0)
        self.metal += gain.get("metal", 0)
        self.mana += gain.get("mana", 0)
        self.gold += gain.get("gold", 0)
        self.actions += gain.get("actions", 0)
        self.buys += gain.get("buys", 0)
        self.sells += gain.get("sells", 0)

    def draw_cards(self, count: int) -> None:
        for _ in range(count):
            card = self.draw_from_deck()
            if not card:
                return
            self.hand.append(card)

    def draw_from_deck(self) -> CardInstance | None:
        if not self.deck:
            if not self.discard:
                return None
            self.deck = self.discard[:]
            random.shuffle(self.deck)
            self.discard.clear()
            self.add_log("버림패를 섞어 덱으로 되돌렸습니다.")
        return self.deck.pop()

    def resolve_design_room(self) -> None:
        drawn: list[CardInstance] = []
        for _ in range(4):
            card = self.draw_from_deck()
            if not card:
                break
            drawn.append(card)
        if not drawn:
            self.add_log("설계실: 덱에 카드가 없습니다.")
            return
        to_hand = drawn[:2]
        to_discard = drawn[2:]
        self.hand.extend(to_hand)
        self.discard.extend(to_discard)
        self.add_log(f"설계실: 손패 {len(to_hand)}장, 버림 {len(to_discard)}장")

    def on_hand_click(self, widget: WorkshopCard) -> None:
        card = widget.card
        if self.trash_remaining > 0:
            self.hand.remove(card)
            self.trash_remaining -= 1
            self.add_log(f"{card.spec.name} 폐기 완료.")
            self._rebuild_widgets()
            self._refresh_ui()
            return

        if self.enchant_remaining > 0:
            if not card.spec.is_product:
                self.add_log("상품 카드만 각인할 수 있습니다.")
                return
            card.sell_bonus += self.enchant_bonus
            self.enchant_remaining -= 1
            self.add_log(f"{card.spec.name} 판매가 +{self.enchant_bonus}G")
            if self.enchant_remaining == 0:
                self.enchant_bonus = 0
            self._rebuild_widgets()
            self._refresh_ui()
            return

        if self.auction_remaining > 0 and card.spec.is_product:
            self.hand.remove(card)
            bonus = self.sell_gold_bonus
            if self.first_sale_pending:
                bonus += self.first_sale_bonus
                self.first_sale_pending = False
            self.gold += card.sell_value + self.auction_bonus + bonus
            self.auction_remaining -= 1
            self.add_log(f"경매로 {card.spec.name} 판매 (+{card.sell_value + self.auction_bonus + bonus}G)")
            if self.auction_remaining == 0:
                self.add_log("경매 종료")
            self._rebuild_widgets()
            self._refresh_ui()
            return

        if self.mode == "sell":
            if not card.spec.is_product:
                self.add_log("상품 카드만 판매할 수 있습니다.")
                return
            if self.sells <= 0:
                self.add_log("판매 횟수가 부족합니다.")
                return
            self.hand.remove(card)
            self.sells -= 1
            bonus = self.sell_gold_bonus
            if self.first_sale_pending:
                bonus += self.first_sale_bonus
                self.first_sale_pending = False
            self.gold += card.sell_value + bonus
            self.add_log(f"{card.spec.name} 판매 (+{card.sell_value + bonus}G)")
            self._rebuild_widgets()
            self._refresh_ui()
            return

        if self.mode != "action":
            self.add_log("액션 모드가 아닙니다.")
            return

        if self.actions <= 0:
            self.add_log("액션이 부족합니다.")
            return

        spec = card.spec
        if not self.has_action(spec):
            self.add_log("사용할 액션이 없습니다.")
            return
        if not self.can_pay(spec.action_cost):
            self.add_log("자원이 부족합니다.")
            return

        self.actions -= 1
        self.pay_cost(spec.action_cost)
        self.apply_gain(spec.action_gain)
        if spec.draw_cards:
            self.draw_cards(spec.draw_cards)
        if spec.craft_product:
            bonus = self.crafted_bonus
            if self.first_craft_pending:
                bonus += self.first_craft_bonus
                self.first_craft_pending = False
            crafted = self._make_card(spec.craft_product, sell_bonus=bonus)
            self.hand.append(crafted)
            total_bonus_text = f"(+{bonus}G 보너스)" if bonus else ""
            self.add_log(f"{spec.craft_product} 제작 {total_bonus_text}")
            if self.craft_gold_bonus:
                self.gold += self.craft_gold_bonus
                self.add_log(f"제작 보너스 골드 +{self.craft_gold_bonus}G")
        if spec.crafted_bonus:
            self.crafted_bonus += spec.crafted_bonus
            self.add_log(f"이번 턴 제작 상품 가치 +{spec.crafted_bonus}G")
        if spec.auction:
            self.auction_remaining = 3
            self.auction_bonus = 2
            self.add_log("경매 시작: 상품 최대 3장 +2G")
        if spec.trash_cards:
            self.trash_remaining = spec.trash_cards
            self.add_log(f"폐기 모드: {spec.trash_cards}장 선택")
        if spec.name == "룬 각인":
            self.enchant_remaining = 1
            self.enchant_bonus = 3
            self.add_log("각인 대상: 상품 1장 선택")
        if spec.name == "마이스터":
            self.first_craft_bonus = 6
            self.first_craft_pending = True
            self.add_log("이번 턴 첫 제작 상품 가치 +6G")
        if spec.name == "공장 감독관":
            self.craft_gold_bonus += 1
            self.add_log("이번 턴 제작 상품 1장당 골드 +1G")
        if spec.name == "일괄 납품":
            self.sell_gold_bonus += 1
            self.add_log("이번 턴 판매 상품 1장당 골드 +1G")
        if spec.name == "감정사":
            self.first_sale_bonus = 3
            self.first_sale_pending = True
            self.add_log("이번 턴 첫 상품 판매 골드 +3G")
        if spec.name == "설계실":
            self.resolve_design_room()

        self.hand.remove(card)
        self.discard.append(card)
        self._rebuild_widgets()
        self._refresh_ui()

    def on_market_click(self, widget: WorkshopCard) -> None:
        if self.mode != "buy":
            self.add_log("구매 모드가 아닙니다.")
            return
        if self.buys <= 0:
            self.add_log("구매 횟수가 부족합니다.")
            return
        card = widget.card
        if self.gold < card.spec.cost:
            self.add_log("골드가 부족합니다.")
            return
        self.gold -= card.spec.cost
        self.buys -= 1
        self.market.remove(card)
        self.discard.append(card)
        self.add_log(f"{card.spec.name} 구매 (-{card.spec.cost}G)")
        self.refresh_market()
        self._rebuild_widgets()
        self._refresh_ui()

    def end_turn(self) -> None:
        self.add_log("정리 단계 시작")
        self.discard.extend(self.hand)
        self.hand.clear()
        self.mana = 0
        self.actions = 1
        self.buys = 1
        self.sells = 1
        self.crafted_bonus = 0
        self.first_craft_bonus = 0
        self.first_craft_pending = False
        self.craft_gold_bonus = 0
        self.sell_gold_bonus = 0
        self.first_sale_bonus = 0
        self.first_sale_pending = False
        self.auction_remaining = 0
        self.auction_bonus = 0
        self.trash_remaining = 0
        self.enchant_remaining = 0
        self.enchant_bonus = 0
        self.turn += 1
        self.mode = "action"
        self.draw_cards(5)
        self.reset_market()
        self._rebuild_widgets()
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        self.resource_text.text = (
            f"턴 {self.turn}\n"
            f"톱니 {self.gear} / 금속 {self.metal} / 마나 {self.mana} / 골드 {self.gold}\n"
            f"액션 {self.actions} / 구매 {self.buys} / 판매 {self.sells}\n"
            f"덱 {len(self.deck)} / 버림 {len(self.discard)}"
        )
        mode_korean = {"action": "액션", "buy": "구매", "sell": "판매"}.get(self.mode, self.mode)
        extra = ""
        if self.auction_remaining > 0:
            extra = f" (경매 {self.auction_remaining}회 남음)"
        if self.trash_remaining > 0:
            extra = f" (폐기 {self.trash_remaining}장 선택)"
        if self.enchant_remaining > 0:
            extra = " (각인 대상 선택)"
        self.mode_text.text = f"현재 모드: {mode_korean}{extra}"
        for button in self.mode_buttons:
            button.set_active(button.mode_key == self.mode)
        for widget in self.hand_widgets:
            widget.refresh()
        for widget in self.market_widgets:
            widget.refresh()

    def update(self) -> None:
        for button in self.mode_buttons:
            button.update()
        self.end_turn_button.update()

        for widget in self.hand_widgets:
            if self.trash_remaining > 0:
                available = True
            elif self.auction_remaining > 0:
                available = widget.card.spec.is_product
            elif self.mode == "sell":
                available = widget.card.spec.is_product and self.sells > 0
            elif self.mode == "action":
                available = (
                    self.actions > 0
                    and self.has_action(widget.card.spec)
                    and self.can_pay(widget.card.spec.action_cost)
                )
            else:
                available = False
            widget.update(available)

        for widget in self.market_widgets:
            available = self.mode == "buy" and self.buys > 0 and self.gold >= widget.card.spec.cost
            widget.update(available)

        self.layout_cards()

    def draw(self) -> None:
        self.title.draw()
        self.resource_text.draw()
        self.mode_text.draw()
        self.log_text.draw()
        for button in self.mode_buttons:
            button.draw()
        self.end_turn_button.draw()
        for widget in self.market_widgets:
            widget.draw()
        for widget in self.hand_widgets:
            widget.draw()


class Scenes:
    workshop = WorkshopScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False)
    window.setCurrentScene(Scenes.workshop)
    window.run()
