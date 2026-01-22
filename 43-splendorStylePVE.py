from __future__ import annotations

import random
from dataclasses import dataclass, field

import pygame

from REMOLib import *


COLORS = ["red", "blue", "yellow", "green", "black"]
COLOR_MAP = {
    "red": Cs.red,
    "blue": Cs.steelblue,
    "yellow": Cs.gold,
    "green": Cs.seagreen,
    "black": Cs.dark(Cs.grey25),
    "gold": Cs.gold,
}


@dataclass
class CardData:
    name: str
    cost: dict[str, int]
    points: int
    card_type: str
    discount_color: str | None = None
    description: str = ""


@dataclass
class FacilityData:
    name: str
    cost_gold: int
    description: str
    facility_type: str
    used_once: bool = False


@dataclass
class TurnModifiers:
    extra_take: int = 0
    allow_second_purchase: bool = False
    purchase_surcharge: int = 0
    temp_discount_color: str | None = None
    temp_discount_amount: int = 0
    score_bonus: int = 0
    cost_reduction: int = 0
    return_token_after_purchase: bool = False

    def reset(self) -> None:
        self.extra_take = 0
        self.allow_second_purchase = False
        self.purchase_surcharge = 0
        self.temp_discount_color = None
        self.temp_discount_amount = 0
        self.score_bonus = 0
        self.cost_reduction = 0
        self.return_token_after_purchase = False


class CardWidget(rectObj):
    def __init__(self, card: CardData, on_click):
        super().__init__(pygame.Rect(0, 0, 180, 240), color=Cs.dark(Cs.slateblue), edge=4)
        self.card = card
        self._on_click = on_click
        self.title = textObj(card.name, size=20, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 12)

        cost_text = ", ".join(f"{color[0].upper()}{amt}" for color, amt in card.cost.items())
        self.cost = textObj(cost_text, size=18, color=Cs.white)
        self.cost.setParent(self, depth=1)
        self.cost.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 44)

        self.points = textObj(f"{card.points}점", size=18, color=Cs.yellow)
        self.points.setParent(self, depth=1)
        self.points.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 70)

        if card.discount_color:
            self.discount = textObj(f"할인 +1: {card.discount_color}", size=16, color=Cs.light(Cs.green))
            self.discount.setParent(self, depth=1)
            self.discount.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 96)
        else:
            self.discount = None

        self.desc = longTextObj(card.description, pos=RPoint(0, 0), size=16, color=Cs.white, textWidth=150)
        self.desc.setParent(self, depth=1)
        self.desc.center = self.offsetRect.center

        self.type_text = textObj(card.card_type, size=16, color=Cs.light(Cs.grey))
        self.type_text.setParent(self, depth=1)
        self.type_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 10)

    def update(self):
        if self.collideMouse() and Rs.userJustLeftClicked():
            self._on_click(self.card)


class FacilityWidget(rectObj):
    def __init__(self, facility: FacilityData, on_click):
        super().__init__(pygame.Rect(0, 0, 200, 150), color=Cs.dark(Cs.teal), edge=4)
        self.facility = facility
        self._on_click = on_click

        self.title = textObj(facility.name, size=18, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 10)

        self.cost = textObj(f"골드 {facility.cost_gold}", size=16, color=Cs.gold)
        self.cost.setParent(self, depth=1)
        self.cost.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 36)

        self.desc = longTextObj(facility.description, pos=RPoint(0, 0), size=15, color=Cs.white, textWidth=170)
        self.desc.setParent(self, depth=1)
        self.desc.center = self.offsetRect.center

    def update(self):
        if self.collideMouse() and Rs.userJustLeftClicked():
            self._on_click(self.facility)


class GameState:
    def __init__(self):
        self.turn_limit = 20
        self.target_score = 15
        self.turn = 1
        self.points = 0
        self.tokens = {color: 0 for color in COLORS}
        self.gold = 0
        self.max_tokens = 10
        self.discounts = {color: 0 for color in COLORS}
        self.prestige_cards = []
        self.score_cards = []
        self.facilities: list[FacilityData] = []
        self.modifiers = TurnModifiers()
        self.used_facility_this_turn = False
        self.market = {
            "discount": [],
            "prestige": [],
            "score": [],
            "facility": [],
        }
        self.decks = {
            "discount": [],
            "prestige": [],
            "score": [],
            "facility": [],
        }
        self.logs: list[str] = []
        self.used_exhibition = False
        self.purchases_this_turn = 0

    def log(self, message: str) -> None:
        self.logs.append(message)
        if len(self.logs) > 7:
            self.logs.pop(0)

    def token_total(self) -> int:
        return sum(self.tokens.values()) + self.gold

    def discard_overflow(self) -> None:
        limit = self.max_tokens
        while self.token_total() > limit:
            all_tokens = [(color, count) for color, count in self.tokens.items() if count > 0]
            if self.gold > 0:
                all_tokens.append(("gold", self.gold))
            if not all_tokens:
                break
            color, _ = max(all_tokens, key=lambda item: item[1])
            if color == "gold":
                self.gold -= 1
                self.log("보유 한도 초과: 골드 1개 버림")
            else:
                self.tokens[color] -= 1
                self.log(f"보유 한도 초과: {color} 1개 버림")

    def apply_discount(self, cost: dict[str, int]) -> dict[str, int]:
        discounted = {}
        for color, amount in cost.items():
            reduction = self.discounts.get(color, 0)
            if self.modifiers.temp_discount_color == color:
                reduction += self.modifiers.temp_discount_amount
            discounted[color] = max(0, amount - reduction)
        return discounted

    def can_afford(self, card: CardData) -> bool:
        cost = self.apply_discount(card.cost)
        total_needed = sum(cost.values())
        available = sum(self.tokens[color] for color in COLORS) + self.gold
        reduction = self.modifiers.cost_reduction
        return available >= max(0, total_needed - reduction)

    def pay_cost(self, card: CardData) -> bool:
        cost = self.apply_discount(card.cost)
        total_cost = sum(cost.values())
        reduction = min(self.modifiers.cost_reduction, total_cost)
        remaining_cost = total_cost - reduction
        if sum(self.tokens.values()) + self.gold < remaining_cost:
            return False
        for color, amount in cost.items():
            pay = min(self.tokens[color], amount)
            self.tokens[color] -= pay
            cost[color] -= pay
        gold_needed = sum(cost.values())
        if gold_needed > self.gold:
            return False
        self.gold -= gold_needed
        return True


class mainScene(Scene):
    def initOnce(self):
        self.state = GameState()
        self._create_decks()
        self._draw_market()

        self.action_mode = None
        self.pending_choice: list[str] = []
        self.pending_color: str | None = None
        self.pending_row: str | None = None
        self.selected_cards: list[CardData] = []

        self.title = textObj("Splendor Style 솔로 카드 엔진", size=36, color=Cs.white)
        self.title.pos = RPoint(40, 20)

        self.status = longTextObj("", pos=RPoint(40, 70), size=18, color=Cs.white, textWidth=700)

        self.log_area = longTextObj("", pos=RPoint(40, 660), size=18, color=Cs.light(Cs.grey))

        self.action_buttons = []
        self._create_action_buttons()

        self.market_widgets: dict[str, list[CardWidget]] = {
            "discount": [],
            "prestige": [],
            "score": [],
        }
        self.facility_widgets: list[FacilityWidget] = []
        self.owned_facility_widgets: list[FacilityWidget] = []
        self._refresh_market_widgets()

    def _create_decks(self):
        discount_cards = []
        for color in COLORS:
            for idx in range(1, 4):
                discount_cards.append(
                    CardData(
                        name=f"{color} 할인 {idx}",
                        cost={color: 2 + idx % 2},
                        points=0,
                        card_type="할인",
                        discount_color=color,
                        description="영구 할인 +1",
                    )
                )
        prestige_cards = []
        for color in COLORS:
            prestige_cards.append(
                CardData(
                    name=f"{color} 명성",
                    cost={color: 3, random.choice(COLORS): 1},
                    points=1,
                    card_type="명성",
                    discount_color=color,
                    description="영구 할인 +1, 점수 1",
                )
            )
            prestige_cards.append(
                CardData(
                    name=f"{color} 명성+",
                    cost={color: 4, random.choice(COLORS): 2},
                    points=2,
                    card_type="명성",
                    discount_color=color,
                    description="영구 할인 +1, 점수 2",
                )
            )
        score_cards = []
        for idx in range(10):
            colors = random.sample(COLORS, 2)
            score_cards.append(
                CardData(
                    name=f"점수 카드 {idx+1}",
                    cost={colors[0]: 4, colors[1]: 2},
                    points=3 + idx % 4,
                    card_type="점수",
                    description="점수 중심 카드",
                )
            )
        facilities = self._facility_defs()
        random.shuffle(discount_cards)
        random.shuffle(prestige_cards)
        random.shuffle(score_cards)
        random.shuffle(facilities)
        self.state.decks["discount"] = discount_cards
        self.state.decks["prestige"] = prestige_cards
        self.state.decks["score"] = score_cards
        self.state.decks["facility"] = facilities

    def _draw_market(self):
        for key, count in [("discount", 4), ("prestige", 4), ("score", 4), ("facility", 3)]:
            for _ in range(count):
                self._refill_market(key)

    def _refill_market(self, key: str) -> None:
        if self.state.decks[key]:
            self.state.market[key].append(self.state.decks[key].pop())

    def _create_action_buttons(self):
        labels = [
            ("서로 다른 색 3개", self._action_take_three),
            ("같은 색 2개", self._action_take_two),
            ("골드 1개", self._action_take_gold),
            ("카드 구매", self._action_buy_card),
            ("턴 종료", self._end_turn),
        ]
        x, y = 40, 380
        for idx, (label, action) in enumerate(labels):
            button = monoTextButton(label, pos=(x, y + idx * 40), size=20, color=Cs.dark(Cs.grey))
            button.connect(action)
            self.action_buttons.append(button)

    def _refresh_market_widgets(self):
        for row in self.market_widgets.values():
            row.clear()
        self.facility_widgets.clear()

        start_positions = {
            "discount": RPoint(300, 160),
            "prestige": RPoint(300, 410),
            "score": RPoint(1100, 160),
        }
        for key in ("discount", "prestige", "score"):
            start = start_positions[key]
            for idx, card in enumerate(self.state.market[key]):
                widget = CardWidget(card, self._on_card_clicked)
                widget.pos = start + RPoint(idx * 190, 0)
                self.market_widgets[key].append(widget)
        facility_start = RPoint(1100, 410)
        for idx, facility in enumerate(self.state.market["facility"]):
            widget = FacilityWidget(facility, self._on_facility_market_clicked)
            widget.pos = facility_start + RPoint(idx * 210, 0)
            self.facility_widgets.append(widget)

        self._refresh_owned_facilities()

    def _refresh_owned_facilities(self):
        self.owned_facility_widgets.clear()
        start = RPoint(40, 640)
        for idx, facility in enumerate(self.state.facilities):
            widget = FacilityWidget(facility, self._on_facility_owned_clicked)
            widget.pos = start + RPoint((idx % 4) * 210, (idx // 4) * 160)
            if facility.used_once:
                widget.alpha = 120
            self.owned_facility_widgets.append(widget)

    def _update_status(self):
        discounts = ", ".join(f"{c}:{v}" for c, v in self.state.discounts.items())
        tokens = ", ".join(f"{c}:{self.state.tokens[c]}" for c in COLORS)
        status_text = (
            f"턴 {self.state.turn}/{self.state.turn_limit} | 점수 {self.state.points} / {self.state.target_score}\n"
            f"토큰 [{tokens}] 골드:{self.state.gold} (한도 {self.state.max_tokens})\n"
            f"할인 [{discounts}] | 구매 횟수 {self.state.purchases_this_turn}"
        )
        self.status.text = status_text
        log_text = "\n".join(self.state.logs)
        self.log_area.text = log_text

    def _action_take_three(self):
        self.action_mode = "take_three"
        self.pending_choice.clear()
        self.state.log("서로 다른 색 3개 선택")

    def _action_take_two(self):
        self.action_mode = "take_two"
        self.pending_choice.clear()
        self.state.log("같은 색 2개 선택")

    def _action_take_gold(self):
        self.state.gold += 1
        self.state.log("골드 1개 획득")
        self._post_action()

    def _action_buy_card(self):
        self.action_mode = "buy"
        self.state.log("구매할 카드를 선택하세요")

    def _on_card_clicked(self, card: CardData):
        if self.action_mode != "buy":
            return
        if self.state.purchases_this_turn >= 1 and not self.state.modifiers.allow_second_purchase:
            self.state.log("이번 턴 추가 구매 불가")
            return
        if self.state.purchases_this_turn >= 2:
            self.state.log("이번 턴 구매 한도 도달")
            return
        surcharge = self.state.modifiers.purchase_surcharge if self.state.purchases_this_turn == 1 else 0
        if surcharge:
            card = CardData(
                name=card.name,
                cost={k: v + 1 for k, v in card.cost.items()},
                points=card.points,
                card_type=card.card_type,
                discount_color=card.discount_color,
                description=card.description + " (비용 +1)",
            )
        if not self.state.can_afford(card):
            self.state.log("자원이 부족합니다")
            return
        if not self.state.pay_cost(card):
            self.state.log("지불 실패")
            return
        if card.card_type == "할인":
            self.state.discounts[card.discount_color] += 1
        elif card.card_type == "명성":
            self.state.discounts[card.discount_color] += 1
            self.state.prestige_cards.append(card)
            self.state.points += card.points + self.state.modifiers.score_bonus
        elif card.card_type == "점수":
            self.state.score_cards.append(card)
            self.state.points += card.points + self.state.modifiers.score_bonus
        if self.state.modifiers.return_token_after_purchase:
            for color in COLORS:
                if self.state.tokens[color] >= 0:
                    self.state.tokens[color] += 1
                    self.state.log("재활용 라인: 토큰 1개 반환")
                    break
        self.state.purchases_this_turn += 1
        self.state.log(f"{card.name} 구매")
        self._remove_card_from_market(card)
        self._post_action()

    def _remove_card_from_market(self, card: CardData):
        for key in ("discount", "prestige", "score"):
            for idx, existing in enumerate(self.state.market[key]):
                if existing is card:
                    self.state.market[key].pop(idx)
                    self._refill_market(key)
                    self._refresh_market_widgets()
                    return

    def _on_facility_market_clicked(self, facility: FacilityData):
        if self.action_mode != "buy":
            self.state.log("시설 구매는 카드 구매 행동 중에만 가능")
            return
        if self.state.gold < facility.cost_gold:
            self.state.log("골드가 부족합니다")
            return
        if self.state.purchases_this_turn >= 1 and not self.state.modifiers.allow_second_purchase:
            self.state.log("이번 턴 추가 구매 불가")
            return
        self.state.gold -= facility.cost_gold
        self.state.facilities.append(facility)
        self.state.log(f"시설 {facility.name} 구매")
        self.state.purchases_this_turn += 1
        self.state.market["facility"].remove(facility)
        self._refill_market("facility")
        self._refresh_market_widgets()
        self._post_action()

    def _on_facility_owned_clicked(self, facility: FacilityData):
        if self.state.used_facility_this_turn:
            self.state.log("이번 턴 시설 이미 사용")
            return
        if facility.used_once:
            self.state.log("시설이 소진됨")
            return
        self._use_facility(facility)

    def _use_facility(self, facility: FacilityData):
        self.state.used_facility_this_turn = True
        facility.used_once = True
        if facility.name == "정제소":
            self.action_mode = "facility_refinery"
            self.pending_choice.clear()
            self.state.log("버릴 토큰 2개 선택")
        elif facility.name == "압축기":
            self.action_mode = "facility_compressor"
            self.pending_choice.clear()
            self.state.log("서로 다른 색 3개 버림")
        elif facility.name == "창고":
            self.state.max_tokens += 3
            self.state.log("이번 턴 한도 +3")
        elif facility.name == "재활용 라인":
            self.state.modifiers.return_token_after_purchase = True
            self.state.log("이번 턴 구매 후 토큰 1개 반환")
        elif facility.name == "중개소":
            self.action_mode = "facility_broker"
            self.state.log("버릴 시장 카드 선택")
        elif facility.name == "감정원":
            self.action_mode = "facility_appraiser"
            self.state.log("줄을 선택하여 상단 3장 확인")
        elif facility.name == "긴급 발주":
            self.action_mode = "facility_emergency"
            self.state.log("덱 선택 후 카드 검색")
        elif facility.name == "추가 운송로":
            self.state.modifiers.extra_take = 1
            self.state.log("이번 턴 자원 추가 +1")
        elif facility.name == "구매 부스터":
            self.state.modifiers.allow_second_purchase = True
            self.state.modifiers.purchase_surcharge = 1
            self.state.log("이번 턴 2장 구매 가능 (두 번째 비용 +1)")
        elif facility.name == "임시 할인기":
            self.action_mode = "facility_temp_discount"
            self.state.log("할인 색 선택")
        elif facility.name == "홍보국":
            self.state.modifiers.score_bonus = 1
            self.state.log("이번 턴 점수 카드 구매 시 +1점")
        elif facility.name == "전시관":
            if self.state.used_exhibition:
                self.state.log("전시관은 게임당 1회")
            else:
                unique = sum(1 for val in self.state.discounts.values() if val > 0)
                if unique >= 5:
                    self.state.points += 2
                    self.state.used_exhibition = True
                    self.state.log("전시관 발동! 점수 +2")
                else:
                    self.state.log("할인 색 5개 미만")
        elif facility.name == "명예 훈장소":
            if len(self.state.prestige_cards) >= 2:
                self.state.modifiers.cost_reduction = 2
                self.state.log("이번 턴 구매 비용 -2")
            else:
                self.state.log("명성 카드 2장 필요")
        elif facility.name == "재배치실":
            self.action_mode = "facility_relocate"
            self.state.log("교체할 시장 카드 2장 선택")
            self.pending_choice.clear()
        elif facility.name == "비축 금고":
            self.action_mode = "facility_vault"
            self.state.log("골드 1개를 색 토큰 2개로 교환")
        self._refresh_owned_facilities()

    def _end_turn(self):
        self.state.turn += 1
        self.state.used_facility_this_turn = False
        self.state.modifiers.reset()
        self.state.purchases_this_turn = 0
        for facility in self.state.facilities:
            facility.used_once = False
        self.state.max_tokens = 10
        self.action_mode = None
        self.pending_choice.clear()
        self._refresh_owned_facilities()
        self.state.log("턴 종료")
        if self.state.turn > self.state.turn_limit:
            if self.state.points >= self.state.target_score:
                self.state.log("승리! 목표 점수 달성")
            else:
                self.state.log("패배... 점수 부족")

    def _post_action(self):
        self.action_mode = None
        self.pending_choice.clear()
        self.state.discard_overflow()

    def _facility_select_row(self, row: str):
        self.pending_row = row

    def _facility_replace_market_card(self, card: CardData):
        for key in ("discount", "prestige", "score"):
            for idx, existing in enumerate(self.state.market[key]):
                if existing is card:
                    self.state.market[key].pop(idx)
                    self._refill_market(key)
                    self.state.log(f"{existing.name} 버림")
                    self._refresh_market_widgets()
                    return

    def _facility_appraise(self, row: str):
        deck = self.state.decks[row]
        if not deck:
            self.state.log("덱이 비었습니다")
            return
        reveal = deck[-3:]
        chosen = reveal[-1]
        if reveal:
            chosen = random.choice(reveal)
        if chosen:
            deck.remove(chosen)
            self.state.market[row].append(chosen)
            self.state.log(f"감정원: {chosen.name} 공개")
        self._refresh_market_widgets()
        self._post_action()

    def _facility_emergency(self, row: str):
        deck = self.state.decks[row]
        if not deck:
            self.state.log("덱이 비었습니다")
            return
        chosen = random.choice(deck)
        deck.remove(chosen)
        self.state.market[row].append(chosen)
        self.state.log(f"긴급 발주: {chosen.name} 공개 (이번 턴 비용 +1)")
        self.state.modifiers.purchase_surcharge = 1
        self._refresh_market_widgets()
        self._post_action()

    def _facility_temp_discount(self, color: str):
        self.state.modifiers.temp_discount_color = color
        self.state.modifiers.temp_discount_amount = 2
        self.state.log(f"이번 턴 {color} 할인 +2")
        self._post_action()

    def _facility_vault(self, colors: list[str]):
        if self.state.gold < 1:
            self.state.log("골드 부족")
            return
        self.state.gold -= 1
        for color in colors:
            self.state.tokens[color] += 1
        self.state.log("비축 금고: 토큰 2개 획득")
        self._post_action()

    def _select_color(self, color: str):
        if self.action_mode in ("take_three", "facility_compressor"):
            if color in self.pending_choice:
                return
            self.pending_choice.append(color)
            if len(self.pending_choice) == 3:
                if self.action_mode == "take_three":
                    for c in self.pending_choice:
                        self.state.tokens[c] += 1
                    extra = self.state.modifiers.extra_take
                    if extra:
                        self.state.tokens[self.pending_choice[0]] += extra
                    self.state.log("색 토큰 획득")
                    self._post_action()
                else:
                    valid = all(self.state.tokens[c] > 0 for c in self.pending_choice)
                    if not valid:
                        self.state.log("토큰 부족")
                        self.pending_choice.clear()
                        return
                    for c in self.pending_choice:
                        self.state.tokens[c] -= 1
                    self.action_mode = "facility_compressor_gain"
                    self.pending_choice.clear()
                    self.state.log("원하는 색 2개 선택")
            return
        if self.action_mode == "facility_compressor_gain":
            self.pending_choice.append(color)
            if len(self.pending_choice) == 2:
                for c in self.pending_choice:
                    self.state.tokens[c] += 1
                self.state.log("압축기: 토큰 2개 획득")
                self._post_action()
            return
        if self.action_mode == "take_two":
            if self.state.tokens[color] >= 0:
                if self._supply_count(color) >= 4:
                    self.state.tokens[color] += 2 + self.state.modifiers.extra_take
                    self.state.log(f"{color} 토큰 2개 획득")
                    self._post_action()
                else:
                    self.state.log("공급 부족 (4개 이상 필요)")
        if self.action_mode == "facility_vault":
            if len(self.pending_choice) < 2:
                self.pending_choice.append(color)
            if len(self.pending_choice) == 2:
                self._facility_vault(self.pending_choice)
        if self.action_mode == "facility_refinery":
            self.pending_choice.append(color)
            if len(self.pending_choice) == 2:
                if all(self.state.tokens[c] > 0 for c in self.pending_choice):
                    for c in self.pending_choice:
                        self.state.tokens[c] -= 1
                    self.action_mode = "facility_refinery_gain"
                    self.pending_choice.clear()
                    self.state.log("원하는 색 1개 선택")
                else:
                    self.state.log("버릴 토큰 부족")
                    self.pending_choice.clear()
        elif self.action_mode == "facility_refinery_gain":
            self.state.tokens[color] += 1
            self.state.log("정제소: 토큰 1개 획득")
            self._post_action()
        elif self.action_mode == "facility_temp_discount":
            self._facility_temp_discount(color)

    def _supply_count(self, color: str) -> int:
        return 7

    def _facility_relocate_select(self, card: CardData):
        if card in self.selected_cards:
            return
        self.selected_cards.append(card)
        if len(self.selected_cards) == 2:
            for card_item in self.selected_cards:
                self._facility_replace_market_card(card_item)
            self.selected_cards.clear()
            self._post_action()

    def _handle_market_click(self, card: CardData):
        if self.action_mode == "facility_broker":
            self._facility_replace_market_card(card)
            self._post_action()
        elif self.action_mode == "facility_relocate":
            self._facility_relocate_select(card)

    def _handle_facility_row_select(self, row: str):
        if self.action_mode == "facility_appraiser":
            self._facility_appraise(row)
        elif self.action_mode == "facility_emergency":
            self._facility_emergency(row)

    def _facility_defs(self) -> list[FacilityData]:
        return [
            FacilityData("정제소", 2, "토큰 2개 버림 → 원하는 색 1개", "resource"),
            FacilityData("압축기", 2, "서로 다른 색 3개 버림 → 원하는 색 2개", "resource"),
            FacilityData("창고", 3, "이번 턴 토큰 한도 +3", "resource"),
            FacilityData("재활용 라인", 3, "구매 후 토큰 1개 반환", "resource"),
            FacilityData("중개소", 2, "시장 카드 1장 교체", "market"),
            FacilityData("감정원", 3, "덱 상단 3장 중 1장 공개", "market"),
            FacilityData("긴급 발주", 4, "덱에서 1장 찾아 공개 (이번 턴 비용 +1)", "market"),
            FacilityData("추가 운송로", 3, "이번 턴 자원 +1", "tempo"),
            FacilityData("구매 부스터", 4, "이번 턴 2장 구매 (두 번째 +1)", "tempo"),
            FacilityData("임시 할인기", 2, "이번 턴 특정 색 할인 +2", "tempo"),
            FacilityData("홍보국", 3, "이번 턴 점수/명성 구매 +1점", "score"),
            FacilityData("전시관", 4, "할인 색 5개 이상이면 점수 +2 (1회)", "score"),
            FacilityData("명예 훈장소", 3, "명성 2장 이상이면 이번 턴 비용 -2", "score"),
            FacilityData("재배치실", 2, "시장 카드 2장 교체", "stability"),
            FacilityData("비축 금고", 3, "골드 1개를 토큰 2개로", "stability"),
        ]

    def _draw_color_buttons(self):
        if self.action_mode in (
            "take_three",
            "take_two",
            "facility_refinery",
            "facility_refinery_gain",
            "facility_compressor",
            "facility_compressor_gain",
            "facility_temp_discount",
            "facility_vault",
        ):
            for idx, color in enumerate(COLORS):
                button = monoTextButton(color, pos=(40 + idx * 90, 320), size=18, color=COLOR_MAP[color])
                button.connect(lambda c=color: self._select_color(c))
                button.draw()
                button.update()
            if self.action_mode == "facility_vault":
                if len(self.pending_choice) < 2:
                    return

    def _draw_row_buttons(self):
        if self.action_mode in ("facility_appraiser", "facility_emergency"):
            for idx, row in enumerate(["discount", "prestige", "score"]):
                button = monoTextButton(row, pos=(400 + idx * 140, 80), size=18, color=Cs.dark(Cs.grey))
                button.connect(lambda r=row: self._handle_facility_row_select(r))
                button.draw()
                button.update()

    def update(self):
        for button in self.action_buttons:
            button.update()
        self._update_status()

        for row in self.market_widgets.values():
            for widget in row:
                widget.update()
        for widget in self.facility_widgets:
            widget.update()
        for widget in self.owned_facility_widgets:
            widget.update()

        if self.action_mode in ("facility_broker", "facility_relocate"):
            for row in self.market_widgets.values():
                for widget in row:
                    if widget.collideMouse() and Rs.userJustLeftClicked():
                        self._handle_market_click(widget.card)


    def draw(self):
        self.title.draw()
        self.status.draw()
        self.log_area.draw()
        for button in self.action_buttons:
            button.draw()
        for row in self.market_widgets.values():
            for widget in row:
                widget.draw()
        for widget in self.facility_widgets:
            widget.draw()
        for widget in self.owned_facility_widgets:
            widget.draw()
        self._draw_color_buttons()
        self._draw_row_buttons()


class Scenes:
    mainScene = mainScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="REMO Solo PVE")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
