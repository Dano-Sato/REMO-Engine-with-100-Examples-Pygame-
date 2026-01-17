from __future__ import annotations

import math
import random

import pygame

from REMOLib.core import *


class Card:
    def __init__(
        self,
        name: str,
        cost: int,
        *,
        card_type: str = "Operation",
        description: str,
        keywords: tuple[str, ...] = (),
    ):
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.description = description
        self.keywords = keywords

    @property
    def base_color(self) -> tuple[int, int, int]:
        mapping = {
            "Operation": Cs.dark(Cs.steelblue),
            "Finance": Cs.dark(Cs.teal),
            "Utility": Cs.dark(Cs.purple),
            "Attack": Cs.dark(Cs.orange),
            "Status": Cs.dark(Cs.grey),
        }
        return mapping.get(self.card_type, Cs.dark(Cs.steelblue))

    @property
    def badge_color(self) -> tuple[int, int, int]:
        mapping = {
            "Operation": Cs.dark(Cs.lightseagreen),
            "Finance": Cs.dark(Cs.seagreen),
            "Utility": Cs.dark(Cs.indigo),
            "Attack": Cs.dark(Cs.red),
            "Status": Cs.dark(Cs.grey75),
        }
        return mapping.get(self.card_type, Cs.dark(Cs.slateblue))


class PlayerState:
    def __init__(self):
        self.max_stability = 40
        self.stability = 40
        self.base_voltage = 3
        self.voltage = 3
        self.output = 0
        self.protected_output = 0
        self.battery = 0
        self.debt = 0
        self.credit_limit = 6
        self.stress = 0
        self.volatility = 0
        self.rating = 3
        self.pending_margin_call = False
        self.turn_voltage_modifier = 0
        self.interest_bonus = 0.0
        self.circuit_breaker_ready = False
        self.turn_shield = False
        self.surplus_conversion = 0
        self.next_turn_generate_bonus = 0
        self.next_turn_load_reduction = 0

    def interest_rate(self) -> float:
        return min(0.25, 0.1 + self.stress * 0.02 + self.interest_bonus)


class EnemyState:
    BASE_ENEMIES = [
        "Heatwave",
        "Polar Vortex",
        "Liquidity Drought",
        "Regulator",
        "Cyberattack",
        "Generator Failure",
    ]
    ELITES = ["Margin Call Hunter", "Rating Agency"]
    BOSSES = ["Regional Blackout", "Credit Freeze", "AI Demand Shock"]

    def __init__(self, threat: int, name: str):
        self.name = name
        self.max_threat = threat
        self.threat = threat
        self.intent: tuple[str, int] = ("pressure", 2)
        self.load_base = 4
        self.load_growth = 0
        self.generate_penalty = 0
        self.turns = 0

    def roll_intent(self) -> None:
        self.turns += 1
        if self.name == "Heatwave":
            self.load_growth += 1
            self.intent = ("heatwave", 2 + self.turns // 2)
        elif self.name == "Polar Vortex":
            self.generate_penalty = 1
            self.intent = ("freeze", 2 + self.turns // 2)
        elif self.name == "Liquidity Drought":
            self.intent = ("liquidity", 2)
        elif self.name == "Regulator":
            self.intent = ("regulation", 1 + self.turns // 3)
        elif self.name == "Cyberattack":
            self.intent = ("cyber", 1 + self.turns // 2)
        elif self.name == "Generator Failure":
            self.intent = ("failure", 1 + self.turns // 2)
        elif self.name == "Margin Call Hunter":
            self.intent = ("margin", 2 + self.turns // 2)
        elif self.name == "Rating Agency":
            self.intent = ("downgrade", 1 + self.turns // 3)
        elif self.name == "Regional Blackout":
            self.intent = ("blackout", 3 + self.turns // 2)
            if self.turns % 3 == 0:
                self.load_growth += 2
        elif self.name == "Credit Freeze":
            self.intent = ("freeze", 2 + self.turns // 2)
        elif self.name == "AI Demand Shock":
            self.intent = ("shock", 3 + self.turns // 2)
            self.load_growth += 1
        else:
            self.intent = ("pressure", 2)

    def current_load(self, player: PlayerState) -> int:
        base = self.load_base + self.load_growth
        base += max(0, self.turns // 3)
        return max(1, base - player.next_turn_load_reduction)


class CardWidget(rectObj):
    def __init__(self, card: Card, on_play):
        super().__init__(pygame.Rect(0, 0, 190, 270), color=card.base_color, edge=6)
        self.card = card
        self._on_play = on_play
        self.playable = True
        self._base_color = card.base_color
        self._hover_color = Cs.light(self._base_color)
        self._badge_base = card.badge_color
        self._badge_hover = Cs.light(self._badge_base)

        self.type_text = textObj(card.card_type.upper(), size=18, color=Cs.white)
        self.type_text.setParent(self, depth=1)
        self.type_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 48)

        self.title_text = textObj(card.name, size=24, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 78)

        self.cost_badge = rectObj(pygame.Rect(0, 0, 54, 54), radius=18, edge=3, color=self._badge_base)
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.x = 0
        self.cost_badge.y = 0

        self.cost_text = textObj(str(card.cost), size=26, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.desc_text = longTextObj(card.description, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=150)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.title_text.rect.bottom + 8

        self.keyword_text = textObj(" ".join(card.keywords), size=18, color=Cs.yellow)
        self.keyword_text.setParent(self, depth=1)
        self.keyword_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)

        self.set_playable(True)

    def refresh(self, voltage: int) -> None:
        self.playable = voltage >= self.card.cost
        self.cost_text.text = str(self.card.cost)
        self.title_text.text = self.card.name
        self.desc_text.text = self.card.description
        self.keyword_text.text = " ".join(self.card.keywords)
        self.type_text.text = self.card.card_type.upper()
        self.set_playable(self.playable)

    def set_playable(self, playable: bool) -> None:
        self.playable = playable
        alpha = 255 if playable else 160
        self.alpha = alpha
        self.type_text.alpha = alpha
        self.title_text.alpha = alpha
        self.desc_text.alpha = alpha
        self.keyword_text.alpha = alpha
        self.cost_badge.alpha = alpha
        self.cost_text.alpha = alpha

    def update(self):
        hovered = self.collideMouse()
        target_color = self._hover_color if hovered and self.playable else self._base_color
        if self.color != target_color:
            self.color = target_color

        badge_color = self._badge_hover if hovered and self.playable else self._badge_base
        if self.cost_badge.color != badge_color:
            self.cost_badge.color = badge_color

        if hovered and self.playable and Rs.userJustLeftClicked():
            self._on_play()


class GridTradingScene(Scene):
    HAND_LIMIT = 5

    def initOnce(self):
        self.player = PlayerState()
        self.enemy = self._roll_enemy(level=1)
        self.level = 1
        self.turn = 1
        self.selected_class: str | None = None
        self.relic_text = ""

        self.master_deck: list[Card] = []
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []
        self.hand_widgets: list[CardWidget] = []

        self.log_lines: list[str] = []
        self.log_box = longTextObj("", pos=RPoint(50, 430), size=22, color=Cs.white, textWidth=600)

        self.info_layout = layoutObj(pos=RPoint(50, 40), isVertical=True, spacing=18)
        self.player_text = textObj("", size=26, color=Cs.white)
        self.enemy_text = textObj("", size=26, color=Cs.white)
        self.intent_text = textObj("", size=24, color=Cs.tiffanyBlue)
        self.deck_text = textObj("", size=22, color=Cs.grey75)
        self.relic_label = textObj("", size=22, color=Cs.yellow)
        for t in (self.player_text, self.enemy_text, self.intent_text, self.deck_text, self.relic_label):
            t.setParent(self.info_layout)
        self.info_layout.adjustLayout()

        self.end_turn_button = textButton(
            "정산/턴 종료",
            pygame.Rect(0, 0, 220, 64),
            color=Cs.tiffanyBlue,
            textColor=Cs.white,
        )
        self.end_turn_button.pos = RPoint(1200, 40)
        self.end_turn_button.connect(self.end_turn)

        self.class_buttons: list[textButton] = []
        self._make_class_buttons()

        self.hand_layout = layoutObj(pos=RPoint(90, 690), spacing=52,isVertical=False)

        self._start_combat(reset_stability=False)

    def init(self):
        return

    def _make_class_buttons(self) -> None:
        self.class_buttons.clear()
        labels = [
            "Grid Operator",
            "Quant Desk",
            "Renewables Architect",
        ]
        for idx, label in enumerate(labels):
            button = textButton(
                label,
                pygame.Rect(0, 0, 260, 64),
                color=Cs.dark(Cs.grey),
                textColor=Cs.white,
            )
            button.pos = RPoint(800, 320 + idx * 90)
            button.connect(lambda choice=label: self._select_class(choice))
            self.class_buttons.append(button)

    def _select_class(self, choice: str) -> None:
        self.selected_class = choice
        if choice == "Grid Operator":
            self.relic_text = "Circuit Breaker Panel: 전투당 1회 Load 실패 피해 0"
            self.player.circuit_breaker_ready = True
        elif choice == "Quant Desk":
            self.relic_text = "Prime Broker Line: CL +2, 이자율 +5%"
            self.player.credit_limit += 2
            self.player.interest_bonus += 0.05
        elif choice == "Renewables Architect":
            self.relic_text = "Battery Farm: 전투 시작 Store +2"
            self.player.battery += 2
        self.master_deck = self._make_starter_deck(choice)
        self._start_combat(reset_stability=True)
        self._add_log(f"{choice} 클래스를 선택했습니다.")

    def _make_starter_deck(self, choice: str) -> list[Card]:
        deck: list[Card] = []
        deck.extend(
            [
                CARD_LIBRARY["Gas Peaker"],
                CARD_LIBRARY["Baseline Coal"],
                CARD_LIBRARY["Wind Surge"],
                CARD_LIBRARY["Transmission Upgrade"],
                CARD_LIBRARY["Battery Charge"],
                CARD_LIBRARY["Battery Discharge"],
                CARD_LIBRARY["Load Forecast"],
                CARD_LIBRARY["Overclock Loan"],
                CARD_LIBRARY["Liquidity Injection"],
                CARD_LIBRARY["Stabilize Frequency"],
            ]
        )
        if choice == "Quant Desk":
            deck.append(CARD_LIBRARY["Price Spike Arbitrage"])
        elif choice == "Renewables Architect":
            deck.append(CARD_LIBRARY["Battery Charge"])
        else:
            deck.append(CARD_LIBRARY["Circuit Trip"])
        return deck

    def _roll_enemy(self, level: int) -> EnemyState:
        if level % 6 == 0:
            name = random.choice(EnemyState.BOSSES)
            threat = 45 + level * 2
        elif level % 3 == 0:
            name = random.choice(EnemyState.ELITES)
            threat = 35 + level * 2
        else:
            name = random.choice(EnemyState.BASE_ENEMIES)
            threat = 28 + level * 2
        enemy = EnemyState(threat, name)
        enemy.load_base = 4 + level // 2
        return enemy

    def _add_log(self, text: str) -> None:
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-7:]
        self.log_box.text = "\n".join(self.log_lines)

    def _reshuffle_discard_into_draw(self) -> None:
        if not self.draw_pile and self.discard_pile:
            random.shuffle(self.discard_pile)
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            self._add_log("버림 더미를 섞어 드로우 더미로 옮겼습니다.")

    def _draw_cards(self, n: int) -> None:
        for _ in range(n):
            if not self.draw_pile:
                self._reshuffle_discard_into_draw()
            if not self.draw_pile:
                return
            self.hand.append(self.draw_pile.pop())
        if n:
            self._add_log(f"카드를 {n}장 뽑았습니다.")

    def _start_combat(self, *, reset_stability: bool) -> None:
        if reset_stability:
            self.player.stability = self.player.max_stability
        self.player.output = 0
        self.player.protected_output = 0
        self.player.turn_shield = False
        self.turn = 1
        self.enemy = self._roll_enemy(level=self.level)
        self.draw_pile = self.master_deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile.clear()
        self.hand.clear()
        self._add_log(f"{self.enemy.name} 사건을 시작합니다!")
        self._draw_cards(GridTradingScene.HAND_LIMIT)
        self.enemy.roll_intent()
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        load = self.enemy.current_load(self.player)
        self.player_text.text = (
            "안정성 {}/{} | 전압 {} | Output {} | Load {} | 부채 {} | CL {} | Stress {} | Volatility {}"
        ).format(
            self.player.stability,
            self.player.max_stability,
            self.player.voltage,
            self.player.output + self.player.protected_output,
            load,
            self.player.debt,
            self.player.credit_limit,
            self.player.stress,
            self.player.volatility,
        )
        self.enemy_text.text = f"{self.enemy.name} Threat {self.enemy.threat}/{self.enemy.max_threat}"
        intent_type, intent_value = self.enemy.intent
        intent_label = {
            "heatwave": "폭염",
            "freeze": "한파",
            "liquidity": "유동성 경색",
            "regulation": "규제",
            "cyber": "사이버 공격",
            "failure": "발전기 고장",
            "margin": "마진콜 압박",
            "downgrade": "등급 하향",
            "blackout": "블랙아웃 파동",
            "shock": "수요 쇼크",
            "pressure": "시장 압박",
        }.get(intent_type, intent_type)
        self.intent_text.text = f"예고: Load {load} / 적 의도: {intent_label} {intent_value}"
        self.deck_text.text = f"드로우 {len(self.draw_pile)}장 · 버림 {len(self.discard_pile)}장"
        self.relic_label.text = f"유물: {self.relic_text}" if self.relic_text else ""
        self.info_layout.adjustLayout()
        self._rebuild_hand_widgets()

    def _rebuild_hand_widgets(self) -> None:
        self.hand_layout.clearChilds(0)
        self.hand_widgets.clear()
        for card in self.hand:
            widget = CardWidget(card, on_play=lambda c=card: self.play_card(c))
            widget.setParent(self.hand_layout)
            widget.refresh(self.player.voltage)
            self.hand_widgets.append(widget)
        self.hand_layout.adjustLayout()

    def _apply_damage(self, amount: int, *, reason: str) -> None:
        if amount <= 0:
            return
        if self.player.turn_shield:
            self._add_log(f"차단기가 {reason} 피해를 무효화했습니다!")
            self.player.turn_shield = False
            return
        self.player.stability = max(0, self.player.stability - amount)
        self._add_log(f"{reason} 피해 {amount}을 받았습니다.")

    def _set_margin_call(self) -> None:
        if self.player.debt >= self.player.credit_limit + 3:
            self.player.pending_margin_call = True
            self._add_log("마진콜 위험! 다음 턴 강제 상환 이벤트가 발생합니다.")

    def _trigger_margin_call(self) -> None:
        if not self.player.pending_margin_call:
            return
        self.player.pending_margin_call = False
        self._add_log("마진콜! 손패 1장 폐기, 안정성 3 감소.")
        if self.hand:
            dropped = random.choice(self.hand)
            self.hand.remove(dropped)
            self.discard_pile.append(dropped)
        self._apply_damage(3, reason="마진콜")

    def start_turn(self) -> None:
        self.player.voltage = max(0, self.player.base_voltage + self.player.turn_voltage_modifier)
        self.player.turn_voltage_modifier = 0
        if self.player.next_turn_generate_bonus:
            self.player.output += self.player.next_turn_generate_bonus
            self._add_log(f"풍력 예측 덕분에 Output +{self.player.next_turn_generate_bonus}.")
            self.player.next_turn_generate_bonus = 0
        if self.player.pending_margin_call:
            self._trigger_margin_call()
        draw_amount = GridTradingScene.HAND_LIMIT - len(self.hand)
        if draw_amount > 0:
            self._draw_cards(draw_amount)
        self.enemy.roll_intent()
        self._refresh_ui()
        self._add_log("새 턴이 시작되었습니다.")

    def play_card(self, card: Card) -> None:
        if self.selected_class is None:
            return
        if card not in self.hand:
            return
        if self.player.voltage < card.cost:
            return

        self.player.voltage -= card.cost
        self._resolve_card_effect(card)
        self.hand.remove(card)
        self.discard_pile.append(card)
        self._refresh_ui()

    def _resolve_card_effect(self, card: Card) -> None:
        name = card.name
        enemy = self.enemy
        player = self.player
        load = enemy.current_load(player)

        if name == "Gas Peaker":
            self._generate_output(4)
            player.stress += 1
            self._add_log("가스 피커: Output +4, Stress +1")
        elif name == "Baseline Coal":
            self._generate_output(6)
            self.discard_pile.append(CARD_LIBRARY["Pollution"])
            self._add_log("석탄 발전: Output +6, Pollution 추가")
        elif name == "Wind Surge":
            self._generate_output(2)
            player.next_turn_generate_bonus += 2
            if player.stress >= 3 and random.random() < 0.5:
                player.next_turn_generate_bonus = max(0, player.next_turn_generate_bonus - 2)
                self._add_log("강풍 불안정: 다음 턴 Output 보너스 실패")
            else:
                self._add_log("강풍: Output +2, 다음 턴 Output +2")
        elif name == "Transmission Upgrade":
            self._transmit_output(3)
            player.next_turn_load_reduction += 1
            self._add_log("송전 강화: Output 3 보호, 다음 2턴 Load -1")
        elif name == "Demand Response":
            self._shed_load(2)
            self._draw_cards(1)
            self._add_log("수요 반응: Load -2, 카드 1장 드로우")
        elif name == "Battery Charge":
            player.battery += 4
            self._add_log("배터리 충전: Store +4")
        elif name == "Battery Discharge":
            discharged = min(player.battery, 4)
            player.battery -= discharged
            player.output += discharged
            self._add_log(f"배터리 방전: Output +{discharged}")
        elif name == "Load Forecast":
            self._draw_cards(1)
            self._add_log(f"수요 예측: 다음 Load {load} 공개, 카드 1장 드로우")
        elif name == "Overclock Loan":
            player.debt += 2
            player.voltage += 2
            self._add_log("오버클럭 대출: Debt +2, 전압 +2")
        elif name == "Roll Over":
            player.credit_limit = max(2, player.credit_limit - 1)
            player.interest_bonus = max(0.0, player.interest_bonus - 0.03)
            self._add_log("만기연장: 이자 -30% (3턴), CL -1 (3턴)")
        elif name == "Liquidity Injection":
            self._repay_debt(3)
            self._draw_cards(2)
            player.stress = max(0, player.stress - 1)
            self._add_log("유동성 주입: Debt -3, 드로우 2, Stress -1")
        elif name == "Credit Default Swap":
            player.debt += 1
            player.turn_shield = True
            self._add_log("CDS: 이번 금융 피해 무효화, Debt +1")
        elif name == "Hedge Fund Raid":
            enemy.threat = max(0, enemy.threat - 7)
            player.volatility += 2
            self._add_log("헤지 펀드 습격: Threat -7, Volatility +2")
        elif name == "Swap Line":
            player.credit_limit += 2
            player.debt += 2
            self._add_log("스왑 라인: CL +2 (전투 종료), 전투 종료 시 Debt +2")
        elif name == "Circuit Trip":
            player.turn_shield = True
            player.turn_voltage_modifier -= 1
            self._add_log("차단기: 이번 턴 피해 0, 다음 턴 전압 -1")
        elif name == "Black Start":
            player.stability = min(player.max_stability, player.stability + 8)
            self.discard_pile.append(CARD_LIBRARY["Illiquid"])
            self._add_log("블랙 스타트: 안정성 +8, Illiquid 추가")
        elif name == "Regulatory Filing":
            player.stress = max(0, player.stress - 2)
            player.surplus_conversion -= 1
            self._add_log("규제 대응: Stress -2, 이번 턴 공격 불가")
        elif name == "Automation Patch":
            if self.hand:
                duplicate = random.choice(self.hand)
                self.hand.append(duplicate)
                self._add_log(f"자동화 패치: {duplicate.name} 복제")
            player.turn_voltage_modifier -= 1
        elif name == "Audit Avoidance":
            player.turn_shield = True
            self._add_log("감사 회피: Debt 증가 1회 무효화")
        elif name == "Stabilize Frequency":
            enemy.threat = max(0, enemy.threat - 4)
            player.surplus_conversion += 3
            self._add_log("주파수 안정화: Threat -4, Load 성공 시 추가 -3")
        elif name == "Island Mode":
            enemy.threat = max(0, enemy.threat - 6)
            player.next_turn_load_reduction += 1
            self._add_log("섬모드: Threat -6, 다음 턴 Load 완화")
        elif name == "Price Spike Arbitrage":
            enemy.threat = max(0, enemy.threat - 3)
            player.debt += 1
            player.surplus_conversion += 5
            self._add_log("가격 급등 재정거래: Threat -3, Surplus 있으면 추가 -5")
        elif name == "Curtailment Strike":
            enemy.threat = max(0, enemy.threat - 2)
            player.surplus_conversion += 4
            self._add_log("출력 억제 파업: Threat -2, Shed 연계 시 추가 -4")
        elif card.card_type == "Status":
            self._add_log(f"{card.name}: 패널티 카드")
        else:
            self._add_log(f"{card.name}: 효과 없음")

        if self.enemy.name == "Liquidity Drought" and "Borrow" in card.keywords:
            player.stress += 2
            self._add_log("유동성 가뭄: Borrow 사용으로 Stress +2")
        if self.enemy.name == "Regulator" and any(k in card.keywords for k in ("Borrow", "Arbitrage")):
            player.stress += 1
            self._add_log("규제기관: 고위험 카드 사용으로 Stress +1")

    def _generate_output(self, amount: int) -> None:
        if self.enemy.name == "Generator Failure" and self.enemy.intent[0] == "failure":
            self._add_log("발전기 고장으로 발전이 무효화되었습니다.")
            return
        penalty = self.enemy.generate_penalty
        actual = max(0, amount - penalty)
        self.player.output += actual
        if penalty:
            self._add_log(f"한파 패널티로 Output -{penalty}")

    def _transmit_output(self, amount: int) -> None:
        usable = min(self.player.output, amount)
        self.player.output -= usable
        self.player.protected_output += usable

    def _shed_load(self, amount: int) -> None:
        self.player.stress += 1
        self.player.next_turn_load_reduction += amount
        self._add_log(f"긴급 셰드: Load 감소 예약 {amount}, Stress +1")

    def _repay_debt(self, amount: int) -> None:
        reduced = min(self.player.debt, amount)
        self.player.debt -= reduced

    def end_turn(self) -> None:
        if self.selected_class is None:
            return
        self._resolve_load()
        self._resolve_enemy_intent()
        self._resolve_finance()
        self._cleanup_turn()
        if self.enemy.threat <= 0:
            self._advance_stage()
            return
        if self.player.stability <= 0:
            self._add_log("블랙아웃! 게임 오버.")
            return
        self.turn += 1
        self.start_turn()

    def _resolve_load(self) -> None:
        load = self.enemy.current_load(self.player)
        total_output = self.player.output + self.player.protected_output
        if total_output >= load:
            surplus = total_output - load
            self._add_log(f"Load 성공! Surplus {surplus} 발생.")
            bonus = surplus // 2
            if self.player.surplus_conversion > 0:
                bonus += self.player.surplus_conversion
            if bonus:
                self.enemy.threat = max(0, self.enemy.threat - bonus)
                self._add_log(f"Surplus 전환: Threat -{bonus}")
            self.player.surplus_conversion = 0
        else:
            shortfall = load - total_output
            damage = shortfall
            if self.enemy.name == "Heatwave":
                damage *= 2
            if self.player.circuit_breaker_ready:
                self._add_log("차단기 패널 발동! 이번 Load 실패 피해를 무효화합니다.")
                self.player.circuit_breaker_ready = False
                damage = 0
            self._apply_damage(damage, reason="Load 실패")
            self.player.stress += 1
            self._add_log("Stress +1")
        self.player.output = 0
        self.player.protected_output = 0

    def _resolve_enemy_intent(self) -> None:
        intent, value = self.enemy.intent
        if intent == "heatwave":
            self._apply_damage(value, reason="폭염")
        elif intent == "freeze":
            self._apply_damage(value, reason="한파 충격")
        elif intent == "liquidity":
            self.player.debt += value
            self._add_log(f"유동성 경색: Debt +{value}")
        elif intent == "regulation":
            self.player.stress += value
            self._add_log(f"규제 압박: Stress +{value}")
        elif intent == "cyber":
            self.discard_pile.append(CARD_LIBRARY["Malware"])
            self._add_log("사이버 공격: Malware 카드가 덱에 추가")
        elif intent == "failure":
            self._add_log("발전기 고장: 이번 턴 Generate 카드가 무력화")
        elif intent == "margin":
            self._set_margin_call()
        elif intent == "downgrade":
            if self.player.rating > 0:
                self.player.rating -= 1
                self.player.credit_limit = max(2, self.player.credit_limit - 1)
                self._add_log("등급 강등: CL -1")
        elif intent == "blackout":
            self._apply_damage(value + 2, reason="블랙아웃 파동")
        elif intent == "shock":
            self._apply_damage(value, reason="AI 수요 쇼크")
            self.player.volatility += 1
        else:
            self._apply_damage(value, reason="시장 압박")

    def _resolve_finance(self) -> None:
        interest = math.ceil(self.player.debt * self.player.interest_rate())
        if interest:
            self._apply_damage(interest, reason="이자")
        self._set_margin_call()

    def _cleanup_turn(self) -> None:
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        self.player.next_turn_load_reduction = max(0, self.player.next_turn_load_reduction - 1)
        if self.player.stability <= 0:
            return
        self._refresh_ui()

    def _advance_stage(self) -> None:
        self.level += 1
        reward = random.choice(list(CARD_LIBRARY.values()))
        if reward.card_type != "Status":
            self.master_deck.append(reward)
            self._add_log(f"위기 진압! 보상 카드: {reward.name}")
        else:
            self._add_log("위기 진압! 다음 전투로 이동합니다.")
        self._start_combat(reset_stability=False)

    def update(self):
        if self.selected_class is None:
            for button in self.class_buttons:
                button.update()
            return
        for widget in self.hand_widgets:
            widget.update()
        self.end_turn_button.update()

    def draw(self):
        if self.selected_class is None:
            title = textObj("전력망 운영 + 트레이딩 데스크", size=36, color=Cs.white)
            title.center = (960, 180)
            subtitle = longTextObj(
                "클래스를 선택해 카드 덱빌더 전투를 시작하세요.",
                pos=RPoint(680, 240),
                size=24,
                color=Cs.grey75,
                textWidth=560,
            )
            title.draw()
            subtitle.draw()
            for button in self.class_buttons:
                button.draw()
            return
        self.info_layout.draw()
        self.log_box.draw()
        self.end_turn_button.draw()
        for widget in self.hand_widgets:
            widget.draw()


CARD_LIBRARY = {
    "Gas Peaker": Card(
        "Gas Peaker",
        1,
        card_type="Operation",
        description="Generate 4. Stress +1.",
        keywords=("Generate",),
    ),
    "Baseline Coal": Card(
        "Baseline Coal",
        2,
        card_type="Operation",
        description="Generate 6. Pollution 1 추가.",
        keywords=("Generate", "Illiquid"),
    ),
    "Wind Surge": Card(
        "Wind Surge",
        0,
        card_type="Operation",
        description="Generate 2. 다음 턴 Generate 2.",
        keywords=("Generate",),
    ),
    "Transmission Upgrade": Card(
        "Transmission Upgrade",
        1,
        card_type="Operation",
        description="Transmit 3. 다음 2턴 Load -1.",
        keywords=("Transmit",),
    ),
    "Demand Response": Card(
        "Demand Response",
        1,
        card_type="Operation",
        description="Shed 2. 카드 1장 드로우.",
        keywords=("Shed",),
    ),
    "Battery Charge": Card(
        "Battery Charge",
        1,
        card_type="Operation",
        description="Store 4.",
        keywords=("Store",),
    ),
    "Battery Discharge": Card(
        "Battery Discharge",
        0,
        card_type="Operation",
        description="Store를 Output으로 전환.",
        keywords=("Store",),
    ),
    "Load Forecast": Card(
        "Load Forecast",
        0,
        card_type="Operation",
        description="다음 Load 공개. 카드 1장 드로우.",
        keywords=(),
    ),
    "Overclock Loan": Card(
        "Overclock Loan",
        0,
        card_type="Finance",
        description="Borrow 2. 이번 턴 전압 +2.",
        keywords=("Borrow",),
    ),
    "Roll Over": Card(
        "Roll Over",
        1,
        card_type="Finance",
        description="이자 -30% (3턴). CL -1 (3턴).",
        keywords=("Borrow",),
    ),
    "Liquidity Injection": Card(
        "Liquidity Injection",
        2,
        card_type="Finance",
        description="Repay 3. 드로우 2. Stress -1.",
        keywords=("Repay",),
    ),
    "Credit Default Swap": Card(
        "Credit Default Swap",
        1,
        card_type="Finance",
        description="금융 피해 1회 무효화. Debt +1.",
        keywords=("Hedge",),
    ),
    "Hedge Fund Raid": Card(
        "Hedge Fund Raid",
        2,
        card_type="Finance",
        description="Threat -7. Volatility +2.",
        keywords=("Volatility",),
    ),
    "Swap Line": Card(
        "Swap Line",
        2,
        card_type="Finance",
        description="CL +2 (전투 종료). 전투 종료 시 Debt +2.",
        keywords=("Borrow",),
    ),
    "Circuit Trip": Card(
        "Circuit Trip",
        1,
        card_type="Utility",
        description="이번 턴 Load 실패 피해 0. 다음 턴 전압 -1.",
        keywords=("Circuit Breaker",),
    ),
    "Black Start": Card(
        "Black Start",
        2,
        card_type="Utility",
        description="안정성 +8. Illiquid 추가.",
        keywords=("Illiquid",),
    ),
    "Regulatory Filing": Card(
        "Regulatory Filing",
        1,
        card_type="Utility",
        description="Stress -2. 이번 턴 공격 불가.",
        keywords=("Regulation",),
    ),
    "Automation Patch": Card(
        "Automation Patch",
        1,
        card_type="Utility",
        description="손패 1장 복제. 다음 턴 전압 -1.",
        keywords=(),
    ),
    "Audit Avoidance": Card(
        "Audit Avoidance",
        0,
        card_type="Utility",
        description="이번 턴 Debt 증가 1회 무효화.",
        keywords=("Hedge",),
    ),
    "Stabilize Frequency": Card(
        "Stabilize Frequency",
        1,
        card_type="Attack",
        description="Threat -4. Load 성공 시 추가 -3.",
        keywords=("Threat",),
    ),
    "Island Mode": Card(
        "Island Mode",
        2,
        card_type="Attack",
        description="Threat -6. 다음 턴 Load 완화.",
        keywords=("Threat",),
    ),
    "Price Spike Arbitrage": Card(
        "Price Spike Arbitrage",
        1,
        card_type="Attack",
        description="Threat -3. Surplus 있으면 추가 -5. Debt +1.",
        keywords=("Arbitrage",),
    ),
    "Curtailment Strike": Card(
        "Curtailment Strike",
        0,
        card_type="Attack",
        description="Threat -2. Shed 연계 시 추가 -4.",
        keywords=("Threat",),
    ),
    "Pollution": Card(
        "Pollution",
        1,
        card_type="Status",
        description="효과 없음. 덱 오염.",
        keywords=("Illiquid",),
    ),
    "Illiquid": Card(
        "Illiquid",
        1,
        card_type="Status",
        description="효과 없음. 손패 흐림.",
        keywords=("Illiquid",),
    ),
    "Malware": Card(
        "Malware",
        1,
        card_type="Status",
        description="효과 없음. 드로우 방해.",
        keywords=("Illiquid",),
    ),
}


class Scenes:
    mainScene = GridTradingScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1920, 1080),
        screen_size=(1920, 1080),
        fullscreen=False,
        caption="Grid Trader Deckbuilder",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
