from __future__ import annotations

import random
from dataclasses import dataclass

from REMOLib import *


@dataclass(frozen=True)
class CardData:
    name: str
    card_type: str
    play_cost: int
    description: str
    effect_key: str


CARD_LIBRARY: list[CardData] = [
    CardData(
        name="소형 태양광",
        card_type="발전",
        play_cost=5,
        description="B +1, U +1 (설비 투자)",
        effect_key="build_basic",
    ),
    CardData(
        name="원전 1기",
        card_type="발전",
        play_cost=41,
        description="B +10, U +10",
        effect_key="nuclear_single",
    ),
    CardData(
        name="초대형 CCGT",
        card_type="발전",
        play_cost=21,
        description="B +8, U +11",
        effect_key="mega_ccgt",
    ),
    CardData(
        name="재생에너지 메가팩",
        card_type="발전",
        play_cost=19,
        description="B +5, U +4",
        effect_key="renewable_megapack",
    ),
    CardData(
        name="노후 설비 전면 교체",
        card_type="정비",
        play_cost=27,
        description="B +2, U -3",
        effect_key="full_retrofit",
    ),
    CardData(
        name="복합가스(CCGT)",
        card_type="발전",
        play_cost=19,
        description="B +4, U +2",
        effect_key="ccgt",
    ),
    CardData(
        name="중형 석탄",
        card_type="발전",
        play_cost=11,
        description="B +5, U +7",
        effect_key="mid_coal",
    ),
    CardData(
        name="태양광 증설단지",
        card_type="발전",
        play_cost=15,
        description="B +3, U +1",
        effect_key="solar_expansion",
    ),
    CardData(
        name="풍력 단지",
        card_type="발전",
        play_cost=12,
        description="B +3, U +2",
        effect_key="wind_farm",
    ),
    CardData(
        name="디젤 발전기",
        card_type="발전",
        play_cost=4,
        description="B +2, U +3",
        effect_key="diesel_gen",
    ),
    CardData(
        name="가스 마이크로터빈",
        card_type="발전",
        play_cost=7,
        description="B +2, U +2",
        effect_key="gas_microturbine",
    ),
    CardData(
        name="소형 풍력",
        card_type="발전",
        play_cost=2,
        description="B +1, U +2",
        effect_key="small_wind",
    ),
    CardData(
        name="노후 설비 증설(싸구려)",
        card_type="발전",
        play_cost=3,
        description="B +2, U +4 (가성비는 좋지만 유지비 함정)",
        effect_key="cheap_expansion",
    ),
    CardData(
        name="스팟 전력 구매",
        card_type="즉발",
        play_cost=6,
        description="O +2 (즉발 조달)",
        effect_key="spot_purchase",
    ),
    CardData(
        name="비상 전력 수입",
        card_type="즉발",
        play_cost=10,
        description="O +4 (긴급 수입)",
        effect_key="emergency_import",
    ),
    CardData(
        name="효율 개선",
        card_type="정비",
        play_cost=10,
        description="B +1, U -1 (장기 최적화)",
        effect_key="efficiency",
    ),
    CardData(
        name="대출",
        card_type="금융",
        play_cost=0,
        description="Cash +8, Debt +10",
        effect_key="loan",
    ),
    CardData(
        name="리파이낸싱",
        card_type="금융",
        play_cost=2,
        description="Debt +2, 이자율 -3%",
        effect_key="refi",
    ),
    CardData(
        name="로드셰딩",
        card_type="수요",
        play_cost=6,
        description="L -3 (수요 억제)",
        effect_key="load_shedding",
    ),
    CardData(
        name="연계선 증설",
        card_type="수출",
        play_cost=8,
        description="P_export +1",
        effect_key="export_line",
    ),
    CardData(
        name="탄소세 도입",
        card_type="정책",
        play_cost=0,
        description="U +7, Tariff +1",
        effect_key="carbon_tax",
    ),
    CardData(
        name="블랙스타트 설비",
        card_type="위기",
        play_cost=4,
        description="BO -1, U +3",
        effect_key="blackstart",
    ),
    CardData(
        name="그리드 지원 요청",
        card_type="즉발",
        play_cost=0,
        description="O +2, Cash +6, Debt +8",
        effect_key="grid_support",
    ),
    CardData(
        name="피크 발전 가동",
        card_type="즉발",
        play_cost=4,
        description="O +3, U +1",
        effect_key="peak_generation",
    ),
    CardData(
        name="정비 스킵",
        card_type="정비",
        play_cost=0,
        description="O +3, B -1",
        effect_key="skip_maintenance",
    ),
    CardData(
        name="소형 배터리 팩",
        card_type="정비",
        play_cost=3,
        description="Cap +1",
        effect_key="small_battery_pack",
    ),
    CardData(
        name="예방정비",
        card_type="정비",
        play_cost=2,
        description="O -2, B +1, U -1",
        effect_key="preventive_maintenance",
    ),
    CardData(
        name="노후 설비 폐기",
        card_type="정비",
        play_cost=1,
        description="B -1, U -3",
        effect_key="retire_aging_equipment",
    ),
    CardData(
        name="수요반응 캠페인",
        card_type="수요",
        play_cost=3,
        description="L -2",
        effect_key="demand_response_campaign",
    ),
    CardData(
        name="운영 자동화",
        card_type="정비",
        play_cost=18,
        description="U -2, B +1",
        effect_key="operations_automation",
    ),
    CardData(
        name="AI 운영 최적화",
        card_type="정비",
        play_cost=41,
        description="U -4, B +2",
        effect_key="ai_operation_optimization",
    ),
    CardData(
        name="중형 배터리",
        card_type="정비",
        play_cost=7,
        description="Cap +3",
        effect_key="medium_battery",
    ),
    CardData(
        name="산업체 DR 계약",
        card_type="수요",
        play_cost=4,
        description="L -4, U +1",
        effect_key="industrial_dr_contract",
    ),
    CardData(
        name="수출 계약 체결",
        card_type="수출",
        play_cost=16,
        description="P_export x1.5, Tariff-1",
        effect_key="export_contract",
    ),
    CardData(
        name="요금 인상 청구",
        card_type="정책",
        play_cost=17,
        description="Tariff +1",
        effect_key="tariff_increase_request",
    ),
    CardData(
        name="운영자금 라인",
        card_type="금융",
        play_cost=0,
        description="Cash +12, Debt +16",
        effect_key="operating_credit_line",
    ),
    CardData(
        name="채무 스왑",
        card_type="금융",
        play_cost=4,
        description="U +1, 이자율 -2%",
        effect_key="debt_swap",
    ),
    CardData(
        name="HVDC 수출 라인",
        card_type="수출",
        play_cost=21,
        description="P_export +2 (영구)",
        effect_key="hvdc_export_line",
    ),
    CardData(
        name="신용등급 상향",
        card_type="금융",
        play_cost=16,
        description="이자율 -4% (영구)",
        effect_key="credit_rating_upgrade",
    ),
    CardData(
        name="자산유동화(ABS)",
        card_type="금융",
        play_cost=3,
        description="Debt -21, Tariff -1 (영구)",
        effect_key="abs_securitization",
    ),
    CardData(
        name="프로젝트 파이낸스(PF)",
        card_type="금융",
        play_cost=0,
        description="Cash +25, Debt +27, 이자율 +2%",
        effect_key="project_finance",
    ),
    CardData(
        name="예비력 계약(소형)",
        card_type="즉발",
        play_cost=0,
        description="Cash +7, Store -2",
        effect_key="small_reserve_contract",
    ),
]


CARD_COLORS = {
    "발전": Cs.dark(Cs.orange),
    "즉발": Cs.dark(Cs.steelblue),
    "정비": Cs.dark(Cs.teal),
    "금융": Cs.dark(Cs.purple),
    "수요": Cs.dark(Cs.sienna),
    "수출": Cs.dark(Cs.gold),
    "정책": Cs.dark(Cs.red),
    "위기": Cs.dark(Cs.indigo),
}


class SimpleButton(rectObj):
    def __init__(self, label: str, pos: tuple[int, int], size: tuple[int, int], on_click, *, color=None):
        super().__init__(pygame.Rect(pos[0], pos[1], size[0], size[1]), color=color or Cs.dark(Cs.gray), edge=4, radius=12)
        self.label = textObj(label, size=24, color=Cs.white)
        self.label.setParent(self, depth=1)
        self.label.center = self.offsetRect.center
        self._on_click = on_click
        self._base_color = self.color
        self._hover_color = Cs.light(self.color)
        self.enabled = True

    def set_label(self, label: str) -> None:
        self.label.text = label
        self.label.center = self.offsetRect.center

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        alpha = 255 if enabled else 140
        if self.alpha != alpha:
            self.alpha = alpha
            self.label.alpha = alpha

    def update(self) -> None:
        if not self.enabled:
            return
        self.color = self._hover_color if self.collideMouse() else self._base_color
        if self.collideMouse() and Rs.userJustLeftClicked():
            self._on_click()
        return


class CardWidget(rectObj):
    WIDTH = 220
    HEIGHT = 280

    def __init__(self, card: CardData | None, on_click) -> None:
        super().__init__(pygame.Rect(0, 0, self.WIDTH, self.HEIGHT), color=Cs.dark(Cs.gray), edge=5, radius=18)
        self.card = card
        self._on_click = on_click
        self._base_color = self.color
        self._hover_color = Cs.light(self.color)
        self.purchased = False

        self.type_text = textObj("", size=18, color=Cs.lightgrey)
        self.type_text.setParent(self, depth=1)
        self.type_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 12)

        self.title_text = textObj("", size=24, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.centerx = self.offsetRect.centerx
        self.title_text.y = 56

        self.cost_badge = rectObj(pygame.Rect(0, 0, 54, 54), radius=16, edge=3, color=Cs.dark(Cs.black))
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.topleft = RPoint(self.offsetRect.topleft) + RPoint(12, 12)

        self.cost_text = textObj("0", size=22, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.desc_text = longTextObj("", pos=RPoint(0, 0), size=18, color=Cs.white, textWidth=self.WIDTH - 30)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = 110

        self.note_text = textObj("", size=18, color=Cs.yellow)
        self.note_text.setParent(self, depth=1)
        self.note_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 14)



        self.set_card(card)

    def set_card(self, card: CardData | None) -> None:
        self.card = card
        self.purchased = False
        if card is None:
            self.color = Cs.dark(Cs.gray)
            self._base_color = self.color
            self._hover_color = Cs.light(self.color)
            self.type_text.text = ""
            self.title_text.text = "빈 슬롯"
            self.cost_text.text = "-"
            self.desc_text.text = ""
            self.note_text.text = ""
            return
        self._base_color = CARD_COLORS.get(card.card_type, Cs.dark(Cs.steelblue))
        self._hover_color = Cs.light(self._base_color)
        self.color = self._base_color
        self.type_text.text = card.card_type
        self.title_text.text = card.name
        self.cost_text.text = str(card.play_cost)
        self.desc_text.text = card.description
        self.note_text.text = ""

        self.type_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 12)
        self.title_text.centerx = self.offsetRect.centerx
        self.desc_text.centerx = self.offsetRect.centerx
        self.note_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 14)


    def mark_purchased(self) -> None:
        self.purchased = True
        self.note_text.text = "구매 완료"
        self.color = Cs.dark(Cs.black)

    def update(self, enabled: bool, *, allow_click: bool = True) -> bool:
        if not self.card:
            return False
        if self.purchased:
            return False
        if not enabled:
            return False
        self.color = self._hover_color if self.collideMouse() else self._base_color
        if allow_click and self.collideMouse() and Rs.userJustLeftClicked():
            self._on_click(self)
            return True
        return False


class PowerGridFinanceScene(Scene):
    BLACKOUT_LIMIT = 3

    def initOnce(self) -> None:
        self.background = rectObj(Rs.screenRect(), color=Cs.dark(Cs.darkslategray))
        self.title = textObj("전력망 x 금융 카드 운영", pos=(40, 28), size=46, color=Cs.white)
        self.subtitle = textObj("Load를 맞추고 금융 리스크를 버텨 살아남으세요.", pos=(44, 84), size=24, color=Cs.lightgrey)

        self.phase = "select"
        self.turn = 1
        self.log_messages: list[str] = []
        self.game_over = False
        self.archetype = ""
        self.builder_bonus = False
        self.purchase_cost = 2
        self.surplus_mode = "export"

        self._init_state()
        self._create_panels()
        self._create_buttons()
        self._create_market_widgets()
        self._refresh_status()
        self._log("아키타입을 선택해 게임을 시작하세요.")

    def _init_state(self) -> None:
        self.cash = 20
        self.debt = 0
        self.interest_rate = 0.08
        self.tariff = 2
        self.p_export = 0.5
        self.base_output = 3
        self.output = 3
        self.store = 0
        self.cap = 4
        self.upkeep = 1
        self.load = 8
        self.blackout_count = 0
        self.served = 0
        self.surplus_exported = 0
        self.reroll_cost = 1
        self.market_cards: list[CardData] = []
        self.hand_cards: list[CardData] = []
        self.hand_widgets: list[CardWidget] = []

    def _create_panels(self) -> None:
        self.status_panel = rectObj(pygame.Rect(40, 150, 440, 850), color=Cs.dark(Cs.black), edge=4, radius=20)
        self.market_panel = rectObj(pygame.Rect(520, 150, 1320, 420), color=Cs.dark(Cs.steelblue), edge=4, radius=24)
        self.hand_panel = rectObj(pygame.Rect(520, 600, 1320, 300), color=Cs.dark(Cs.slategray), edge=4, radius=24)
        self.log_panel = rectObj(pygame.Rect(520, 920, 1320, 140), color=Cs.dark(Cs.black), edge=4, radius=20)

        self.status_layout = layoutObj(pos=RPoint(70, 190), spacing=12, isVertical=True)
        self.turn_text = textObj("", size=28, color=Cs.white)
        self.phase_text = textObj("", size=24, color=Cs.lightgrey)
        self.archetype_text = textObj("", size=24, color=Cs.yellow)
        self.cash_text = textObj("", size=26, color=Cs.light(Cs.skyblue))
        self.debt_text = textObj("", size=24, color=Cs.light(Cs.orange))
        self.interest_text = textObj("", size=22, color=Cs.light(Cs.lightcoral))
        self.tariff_text = textObj("", size=22, color=Cs.light(Cs.lightgoldenrodyellow))
        self.export_text = textObj("", size=22, color=Cs.light(Cs.lightgreen))
        self.load_text = textObj("", size=26, color=Cs.light(Cs.white))
        self.output_text = textObj("", size=22, color=Cs.light(Cs.palegreen))
        self.base_text = textObj("", size=22, color=Cs.light(Cs.palegreen))
        self.store_text = textObj("", size=22, color=Cs.light(Cs.aquamarine))
        self.upkeep_text = textObj("", size=22, color=Cs.light(Cs.lightpink))
        self.bo_text = textObj("", size=24, color=Cs.light(Cs.tomato))

        for label in (
            self.turn_text,
            self.phase_text,
            self.archetype_text,
            self.cash_text,
            self.debt_text,
            self.interest_text,
            self.tariff_text,
            self.export_text,
            self.load_text,
            self.output_text,
            self.base_text,
            self.store_text,
            self.upkeep_text,
            self.bo_text,
        ):
            label.setParent(self.status_layout)

        self.status_layout.adjustLayout()

        self.log_text = longTextObj("", pos=RPoint(544, 940), size=20, color=Cs.white, textWidth=1260)

    def _create_buttons(self) -> None:
        self.contractor_button = SimpleButton("계약자", (80, 520), (360, 60), lambda: self._select_archetype("contractor"))
        self.contractor_button.centerx = Rs.screenRect().centerx
        self.operator_button = SimpleButton("오퍼레이터", (80, 600), (360, 60), lambda: self._select_archetype("operator"))
        self.operator_button.centerx = Rs.screenRect().centerx
        self.builder_button = SimpleButton("빌더", (80, 680), (360, 60), lambda: self._select_archetype("builder"))
        self.builder_button.centerx = Rs.screenRect().centerx

        self.reroll_button = SimpleButton("리롤 (1$)", (540, 520), (220, 50), self._reroll_market)
        self.to_play_button = SimpleButton("플레이 단계", (780, 520), (220, 50), self._enter_play_phase)
        self.to_dispatch_button = SimpleButton("운영 단계", (1020, 520), (220, 50), self._enter_dispatch_phase)
        self.end_turn_button = SimpleButton("턴 종료", (1260, 520), (220, 50), self._end_turn)

        self.discharge_one_button = SimpleButton("방전 +1", (1520, 520), (160, 50), self._discharge_one)
        self.discharge_all_button = SimpleButton("전량 방전", (1700, 520), (160, 50), self._discharge_all)

        self.surplus_mode_button = SimpleButton("잉여: 수출", (1520, 460), (340, 50), self._toggle_surplus_mode)
        self.pay_debt_button = SimpleButton("부채 5 상환", (80, 780), (360, 60), self._pay_debt_partial)
        self.pay_all_button = SimpleButton("부채 전액 상환", (80, 860), (360, 60), self._pay_debt_all)

    def _create_market_widgets(self) -> None:
        self.market_layout = layoutObj(pos=RPoint(560, 190), spacing=30, isVertical=False)
        self.market_widgets: list[CardWidget] = []
        for _ in range(4):
            widget = CardWidget(None, self._buy_card)
            widget.setParent(self.market_layout)
            self.market_widgets.append(widget)
        self.market_layout.adjustLayout()

        self.hand_layout = cardLayout(RPoint(560, 640), spacing=30, maxWidth=1260, isVertical=False)

    def _select_archetype(self, archetype: str) -> None:
        if self.phase != "select":
            return
        self.archetype = archetype
        if archetype == "contractor":
            self.purchase_cost = 1
            self.cash = 25
            self.base_output = 2
            self.upkeep = 1
            self.cap = 0
            self.p_export = 1
        elif archetype == "operator":
            self.purchase_cost = 2
            self.cash = 16
            self.base_output = 4
            self.upkeep = 2
            self.cap = 4
        elif archetype == "builder":
            self.purchase_cost = 2
            self.cash = 18
            self.base_output = 3
            self.upkeep = 1
            self.cap = 0
            self.builder_bonus = True
        else:
            print("archetype BUG")
        self.output = self.base_output
        self.store = min(self.store, self.cap)
        self.phase = "market"
        self.turn = 1
        self.blackout_count = 0
        self.debt = 0
        self.interest_rate = 0.08
        self.tariff = 2
        self.p_export = 1
        self._start_turn()
        self._log(f"{self._archetype_label()} 시작! 시장에서 카드를 구매하세요.")

    def _archetype_label(self) -> str:
        return {
            "contractor": "계약자",
            "operator": "오퍼레이터",
            "builder": "빌더",
        }.get(self.archetype, "")

    def _start_turn(self) -> None:
        self.phase = "market"
        self.load = random.randint(4 + self.turn // 2, 8 + self.turn // 2)
        self.output = self.base_output
        self.reroll_cost = 1
        self.surplus_mode = "export"
        self.served = 0
        self.surplus_exported = 0
        self._refresh_market()
        self._refresh_buttons()

    def _refresh_market(self) -> None:
        self.market_cards = random.sample(CARD_LIBRARY, k=4)
        for widget, card in zip(self.market_widgets, self.market_cards):
            widget.set_card(card)
        self.market_layout.adjustLayout()

    def _clear_hand(self) -> None:
        for widget in list(self.hand_widgets):
            widget.setParent(None)
        self.hand_widgets.clear()
        self.hand_cards.clear()
        self.hand_layout.adjustLayout()

    def _buy_card(self, widget: CardWidget) -> None:
        if self.phase != "market" or not widget.card:
            return
        if widget.purchased:
            return
        if self.cash < self.purchase_cost:
            self._log("현금이 부족해 카드를 구매할 수 없습니다.")
            return
        self.cash -= self.purchase_cost
        self.hand_cards.append(widget.card)
        self._add_hand_card(widget.card)
        widget.mark_purchased()
        self._log(f"{widget.card.name} 카드 구매.")

    def _add_hand_card(self, card: CardData) -> None:
        widget = CardWidget(card, self._play_card)
        widget.setParent(self.hand_layout)
        self.hand_widgets.append(widget)
        self.hand_layout.adjustLayout()

    def _reroll_market(self) -> None:
        if self.phase != "market":
            return
        if self.cash < self.reroll_cost:
            self._log("리롤 비용이 부족합니다.")
            return
        self.cash -= self.reroll_cost
        self.reroll_cost += 1
        self._refresh_market()
        self._log("시장 카드가 갱신되었습니다.")

    def _enter_play_phase(self) -> None:
        if self.phase != "market":
            return
        self.phase = "play"
        self._log("플레이 단계: 카드를 실행하세요.")
        self._refresh_buttons()

    def _enter_dispatch_phase(self) -> None:
        if self.phase != "play":
            return
        self.phase = "dispatch"
        self._log("운영 단계: 방전/수출/상환을 결정하세요.")
        self._refresh_buttons()

    def _play_card(self, widget: CardWidget) -> None:
        if self.phase != "play" or not widget.card:
            return
        card = widget.card
        if self.cash < card.play_cost:
            self._log("카드 실행 비용이 부족합니다.")
            return
        self.cash -= card.play_cost
        self._apply_card_effect(card)
        self._log(f"{card.name} 실행.")
        widget.setParent(None)
        if widget in self.hand_widgets:
            self.hand_widgets.remove(widget)
        if card in self.hand_cards:
            self.hand_cards.remove(card)
        self.hand_layout.adjustLayout()

    def _apply_card_effect(self, card: CardData) -> None:
        if card.effect_key == "build_basic":
            self.base_output += 1
            self.upkeep += 1
            if self.builder_bonus:
                self.cash += 3
        elif card.effect_key == "nuclear_single":
            self.base_output += 10
            self.upkeep += 10
        elif card.effect_key == "mega_ccgt":
            self.base_output += 8
            self.upkeep += 11
        elif card.effect_key == "renewable_megapack":
            self.base_output += 5
            self.upkeep += 4
        elif card.effect_key == "full_retrofit":
            self.base_output += 2
            self.upkeep = max(0, self.upkeep - 3)
        elif card.effect_key == "ccgt":
            self.base_output += 4
            self.upkeep += 2
        elif card.effect_key == "mid_coal":
            self.base_output += 5
            self.upkeep += 7
        elif card.effect_key == "solar_expansion":
            self.base_output += 3
            self.upkeep += 1
        elif card.effect_key == "wind_farm":
            self.base_output += 3
            self.upkeep += 2
        elif card.effect_key == "diesel_gen":
            self.base_output += 2
            self.upkeep += 3
        elif card.effect_key == "gas_microturbine":
            self.base_output += 2
            self.upkeep += 1
        elif card.effect_key == "small_wind":
            self.base_output += 1
            self.upkeep += 2
        elif card.effect_key == "cheap_expansion":
            self.base_output += 2
            self.upkeep += 4
        elif card.effect_key == "spot_purchase":
            self.output += 2
        elif card.effect_key == "emergency_import":
            self.output += 4
        elif card.effect_key == "efficiency":
            self.base_output += 1
            self.upkeep = max(0, self.upkeep - 1)
        elif card.effect_key == "loan":
            self.cash += 8
            self.debt += 10
        elif card.effect_key == "refi":
            self.debt += 2
            self.interest_rate = max(0.0, self.interest_rate - 0.03)
        elif card.effect_key == "load_shedding":
            self.load = max(0, self.load - 3)
        elif card.effect_key == "export_line":
            self.p_export += 1
        elif card.effect_key == "carbon_tax":
            self.upkeep += 7
            self.tariff += 1
        elif card.effect_key == "blackstart":
            self.blackout_count = max(0, self.blackout_count - 1)
            self.upkeep += 3
        elif card.effect_key == "grid_support":
            self.output += 2
            self.cash += 6
            self.debt += 8
        elif card.effect_key == "peak_generation":
            self.output += 3
            self.upkeep += 1
        elif card.effect_key == "skip_maintenance":
            self.output += 3
            self.base_output = max(0, self.base_output - 1)
        elif card.effect_key == "small_battery_pack":
            self.cap += 1
        elif card.effect_key == "preventive_maintenance":
            self.output = max(0, self.output - 2)
            self.base_output += 1
            self.upkeep = max(0, self.upkeep - 1)
        elif card.effect_key == "retire_aging_equipment":
            self.base_output = max(0, self.base_output - 1)
            self.upkeep = max(0, self.upkeep - 3)
        elif card.effect_key == "demand_response_campaign":
            self.load = max(0, self.load - 2)
        elif card.effect_key == "operations_automation":
            self.upkeep = max(0, self.upkeep - 2)
            self.base_output += 1
        elif card.effect_key == "ai_operation_optimization":
            self.upkeep = max(0, self.upkeep - 4)
            self.base_output += 2
        elif card.effect_key == "medium_battery":
            self.cap += 3
        elif card.effect_key == "industrial_dr_contract":
            self.load = max(0, self.load - 4)
            self.upkeep += 1
        elif card.effect_key == "export_contract":
            self.p_export *= 1.5
            self.tarrif -= 1
        elif card.effect_key == "tariff_increase_request":
            self.tariff += 1
        elif card.effect_key == "operating_credit_line":
            self.cash += 12
            self.debt += 16
        elif card.effect_key == "debt_swap":
            self.upkeep += 1
            self.interest_rate = max(0.0, self.interest_rate - 0.02)
        elif card.effect_key == "hvdc_export_line":
            self.p_export += 2
        elif card.effect_key == "credit_rating_upgrade":
            self.interest_rate = max(0.0, self.interest_rate - 0.04)
        elif card.effect_key == "abs_securitization":
            self.debt = max(0, self.debt - 21)
            self.tariff = max(0, self.tariff - 1)
        elif card.effect_key == "project_finance":
            self.cash += 25
            self.debt += 27
            self.interest_rate += 0.02
        elif card.effect_key == "small_reserve_contract":
            self.cash += 7
            self.store = max(0, self.store - 2)

    def _discharge_one(self) -> None:
        if self.phase != "dispatch":
            return
        if self.store <= 0:
            self._log("저장된 에너지가 없습니다.")
            return
        self.store -= 1
        self.output += 1
        self._log("배터리 1만큼 방전.")

    def _discharge_all(self) -> None:
        if self.phase != "dispatch":
            return
        if self.store <= 0:
            self._log("저장된 에너지가 없습니다.")
            return
        self.output += self.store
        self._log(f"배터리 {self.store}만큼 전량 방전.")
        self.store = 0

    def _toggle_surplus_mode(self) -> None:
        if self.phase != "dispatch":
            return
        self.surplus_mode = "store" if self.surplus_mode == "export" else "export"
        label = "잉여: 저장" if self.surplus_mode == "store" else "잉여: 수출"
        self.surplus_mode_button.set_label(label)

    def _pay_debt_partial(self) -> None:
        if self.phase != "dispatch":
            return
        if self.debt <= 0:
            self._log("상환할 부채가 없습니다.")
            return
        payment = min(5, self.debt, self.cash)
        if payment <= 0:
            self._log("상환할 현금이 부족합니다.")
            return
        self.debt -= payment
        self.cash -= payment
        self._log(f"부채 {payment}$ 상환.")

    def _pay_debt_all(self) -> None:
        if self.phase != "dispatch":
            return
        if self.debt <= 0:
            self._log("상환할 부채가 없습니다.")
            return
        payment = min(self.debt, self.cash)
        if payment <= 0:
            self._log("상환할 현금이 부족합니다.")
            return
        self.debt -= payment
        self.cash -= payment
        self._log(f"부채 {payment}$ 전액 상환.")

    def _end_turn(self) -> None:
        if self.phase != "dispatch":
            return
        served = min(self.load, self.output)
        self.served = served
        if served < self.load:
            self.blackout_count += 1
            self._log("블랙아웃 발생! 수요를 충족하지 못했습니다.")
        surplus = max(0, self.output - served)
        export_amount = 0
        if surplus > 0:
            if self.surplus_mode == "store":
                stored = min(self.cap - self.store, surplus)
                self.store += stored
                export_amount = surplus - stored
            else:
                export_amount = surplus
        self.surplus_exported = export_amount

        self.cash += self.tariff * served
        self.cash += self.p_export * export_amount
        self.cash -= self.debt * self.interest_rate
        self.cash -= self.upkeep

        self._log(
            f"수익: 공급 {served} (Tariff {self.tariff}$), 수출 {export_amount} (단가 {self.p_export}$)."
        )
        self._log(f"이자 {self.debt * self.interest_rate}$, 유지비 {self.upkeep}$ 지불.")

        if self.cash <= 0:
            self.game_over = True
            self.phase = "gameover"
            self._log("현금이 0 이하가 되어 패배했습니다.")
            return
        if self.blackout_count >= self.BLACKOUT_LIMIT:
            self.game_over = True
            self.phase = "gameover"
            self._log("블랙아웃 누적 한도 초과로 패배했습니다.")
            return

        self.turn += 1
        self._start_turn()
        self._log("새로운 턴이 시작되었습니다.")

    def _log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > 4:
            self.log_messages.pop(0)
        self.log_text.text = "\n".join(self.log_messages)

    def _refresh_buttons(self) -> None:
        is_market = self.phase == "market"
        is_play = self.phase == "play"
        is_dispatch = self.phase == "dispatch"

        self.reroll_button.set_enabled(is_market)
        self.to_play_button.set_enabled(is_market)
        self.to_dispatch_button.set_enabled(is_play)
        self.end_turn_button.set_enabled(is_dispatch)

        self.discharge_one_button.set_enabled(is_dispatch)
        self.discharge_all_button.set_enabled(is_dispatch)
        self.surplus_mode_button.set_enabled(is_dispatch)
        self.pay_debt_button.set_enabled(is_dispatch)
        self.pay_all_button.set_enabled(is_dispatch)

        self.contractor_button.set_enabled(self.phase == "select")
        self.operator_button.set_enabled(self.phase == "select")
        self.builder_button.set_enabled(self.phase == "select")

    def _refresh_status(self) -> None:
        self.turn_text.text = f"턴 {self.turn}"
        self.phase_text.text = f"단계: {self.phase.upper()}"
        self.archetype_text.text = f"아키타입: {self._archetype_label()}"
        self.cash_text.text = f"Cash: {self.cash:.2f}$"
        self.debt_text.text = f"Debt: {self.debt}$"
        self.interest_text.text = f"이자율: {int(self.interest_rate * 100)}%"
        self.tariff_text.text = f"Tariff: {self.tariff}$"
        self.export_text.text = f"수출 단가: {self.p_export}$"
        self.load_text.text = f"Load: {self.load}"
        self.output_text.text = f"Output: {self.output}"
        self.base_text.text = f"Base: {self.base_output}"
        self.store_text.text = f"Store: {self.store}/{self.cap}"
        self.upkeep_text.text = f"Upkeep: {self.upkeep}$"
        self.bo_text.text = f"Blackout: {self.blackout_count}/{self.BLACKOUT_LIMIT}"

        self.reroll_button.set_label(f"리롤 ({self.reroll_cost}$)")
        if self.surplus_mode == "store":
            self.surplus_mode_button.set_label("잉여: 저장")
        else:
            self.surplus_mode_button.set_label("잉여: 수출")

    def update(self) -> None:
        self._refresh_status()
        if self.phase == "select":
            self.contractor_button.update()
            self.operator_button.update()
            self.builder_button.update()
        else:
            for widget in self.market_widgets:
                widget.update(self.phase == "market")
            hand_click_used = False
            for widget in list(self.hand_widgets):
                if widget.update(self.phase == "play", allow_click=not hand_click_used):
                    hand_click_used = True
            self.market_layout.adjustLayout()
            self.hand_layout.adjustLayout()
            self.reroll_button.update()
            self.to_play_button.update()
            self.to_dispatch_button.update()
            self.end_turn_button.update()
            self.discharge_one_button.update()
            self.discharge_all_button.update()
            self.surplus_mode_button.update()
            self.pay_debt_button.update()
            self.pay_all_button.update()

    def draw(self) -> None:
        self.background.draw()
        self.title.draw()
        self.subtitle.draw()

        self.status_panel.draw()
        self.market_panel.draw()
        self.hand_panel.draw()
        self.log_panel.draw()

        self.status_layout.draw()
        self.log_text.draw()

        if self.phase == "select":
            self.contractor_button.draw()
            self.operator_button.draw()
            self.builder_button.draw()
        else:
            self.market_layout.draw()
            self.hand_layout.draw()

            self.reroll_button.draw()
            self.to_play_button.draw()
            self.to_dispatch_button.draw()
            self.end_turn_button.draw()
            self.discharge_one_button.draw()
            self.discharge_all_button.draw()
            self.surplus_mode_button.draw()
            self.pay_debt_button.draw()
            self.pay_all_button.draw()

        if self.game_over:
            overlay = rectObj(pygame.Rect(0, 0, 1920, 1080), color=Cs.dark(Cs.black))
            overlay.alpha = 160
            overlay.draw()
            game_over_text = textObj("게임 오버", size=72, color=Cs.white)
            game_over_text.center = Rs.screenRect().center
            game_over_text.draw()


class Scenes:
    mainScene = PowerGridFinanceScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="전력망 x 금융 카드 운영")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
