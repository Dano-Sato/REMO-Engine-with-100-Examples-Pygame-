from __future__ import annotations

import random
import pygame

from REMOLib.core import *


WARNING = (230, 190, 30)


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def shift_toward_zero(value: int, amount: int) -> int:
    if value > 0:
        return max(0, value - amount)
    if value < 0:
        return min(0, value + amount)
    return 0


class CardDef:
    def __init__(self, verb: str, effect_text: str):
        self.verb = verb
        self.effect_text = effect_text


class ThreatDef:
    def __init__(self, name: str):
        self.name = name


class TankState:
    def __init__(self):
        self.ready = 40
        self.balance = 0
        self.risk = 0
        self.locked = False


class MinimalBrewScene(Scene):
    def __init__(self):
        super().__init__()

    def initOnce(self):
        self.screen_w, self.screen_h = Rs.getWindowRes()

        self.day = 1
        self.cash = 0
        self.rep = 0

        self.tanks = [TankState(), TankState()]
        self.active_tank_index = 0

        self.hand: list[CardDef] = []
        self.deck: list[CardDef] = []
        self.discard: list[CardDef] = []

        self.ap = 2
        self.hand_size = 5
        self.next_threat_preview: ThreatDef | None = None
        self.current_threat: ThreatDef | None = None

        self.used_clean = False
        self.used_rush = False
        self.used_bottle = False
        self.inspection_required = False
        self.tune_penalty = 0
        self.bad_batch = False
        self.price_up = False
        self.humid = False
        self.urgent_order_days: int | None = None

        self.top_day_text = textObj("Day 1", size=28, color=Cs.black)
        self.top_cash_text = textObj("Cash 0", size=28, color=Cs.black)
        self.top_rep_text = textObj("Rep 0", size=28, color=Cs.black)

        self.threat_title = textObj("TODAY THREAT", size=20, color=WARNING)
        self.threat_name = textObj("", size=30, color=Cs.black)
        self.next_threat_text = textObj("", size=18, color=WARNING)
        self.ap_text = textObj("", size=18, color=Cs.black)

        self.end_day_button = pygame.Rect(self.screen_w - 180, self.screen_h - 90, 140, 50)

        self._build_deck()
        self._shuffle_deck()
        self._start_day()

    def _build_deck(self) -> None:
        self.deck = []
        self._add_cards("TUNE", "Balance →0 x2", 3)
        self._add_cards("CLEAN", "Risk -2", 2)
        self._add_cards("STIR", "Ready +5, Balance -1", 2)
        self._add_cards("RUSH", "Ready +20, Risk +1", 2)
        self._add_cards("SAMPLE", "Next threat, Ready +5", 1)
        self._add_cards("BOTTLE", "Lock + Bottle", 2)

    def _add_cards(self, verb: str, effect_text: str, count: int) -> None:
        for _ in range(count):
            self.deck.append(CardDef(verb, effect_text))

    def _shuffle_deck(self) -> None:
        random.shuffle(self.deck)

    def _draw_cards(self, amount: int) -> None:
        for _ in range(amount):
            if not self.deck:
                self.deck = self.discard
                self.discard = []
                self._shuffle_deck()
            if not self.deck:
                return
            self.hand.append(self.deck.pop())

    def _start_day(self) -> None:
        self.ap = 2
        self.used_clean = False
        self.used_rush = False
        self.used_bottle = False
        self.inspection_required = False
        self.tune_penalty = 0
        self.bad_batch = False
        self.price_up = False
        self.humid = False
        if self.hand:
            self.discard.extend(self.hand)
            self.hand = []

        self._set_daily_threat()
        self._apply_threat_start()

        self._draw_cards(self.hand_size)

    def _set_daily_threat(self) -> None:
        if self.next_threat_preview:
            self.current_threat = self.next_threat_preview
            self.next_threat_preview = None
        else:
            self.current_threat = random.choice(self._all_threats())

    def _apply_threat_start(self) -> None:
        if not self.current_threat:
            return
        name = self.current_threat.name
        if name == "SPIKE":
            self._apply_to_tanks(balance_delta=2)
        elif name == "DROP":
            self._apply_to_tanks(balance_delta=-2)
        elif name == "CONTAM":
            self._apply_to_tanks(risk_delta=2)
        elif name == "LEAK":
            self._apply_to_tanks(ready_delta=-10)
        elif name == "DELAY":
            self.ap = max(0, self.ap - 1)
        elif name == "RUSH-ORDER":
            self.urgent_order_days = 2
        elif name == "INSPECTION":
            self.inspection_required = True
        elif name == "POWER-ISSUE":
            self.tune_penalty = 1
        elif name == "SHORT-STAFF":
            self.hand_size = 4
        elif name == "BAD-BATCH":
            self.bad_batch = True
        elif name == "PRICE-UP":
            self.price_up = True
        elif name == "HUMID":
            self.humid = True

    def _apply_to_tanks(self, ready_delta=0, balance_delta=0, risk_delta=0) -> None:
        for tank in self.tanks:
            tank.ready = clamp(tank.ready + ready_delta, 0, 100)
            tank.balance = clamp(tank.balance + balance_delta, -3, 3)
            tank.risk = clamp(tank.risk + risk_delta, 0, 6)

    def _all_threats(self) -> list[ThreatDef]:
        return [
            ThreatDef("SPIKE"),
            ThreatDef("DROP"),
            ThreatDef("CONTAM"),
            ThreatDef("LEAK"),
            ThreatDef("DELAY"),
            ThreatDef("RUSH-ORDER"),
            ThreatDef("INSPECTION"),
            ThreatDef("POWER-ISSUE"),
            ThreatDef("SHORT-STAFF"),
            ThreatDef("BAD-BATCH"),
            ThreatDef("PRICE-UP"),
            ThreatDef("HUMID"),
        ]

    def _play_card(self, card: CardDef) -> None:
        if self.ap <= 0:
            return
        tank = self.tanks[self.active_tank_index]
        if tank.locked:
            return
        self.ap -= 1
        if card.verb == "TUNE":
            shift = max(0, 2 - self.tune_penalty)
            tank.balance = clamp(shift_toward_zero(tank.balance, shift), -3, 3)
        elif card.verb == "CLEAN":
            tank.risk = clamp(tank.risk - 2, 0, 6)
            self.used_clean = True
        elif card.verb == "STIR":
            tank.ready = clamp(tank.ready + 5, 0, 100)
            tank.balance = clamp(tank.balance - 1, -3, 3)
        elif card.verb == "RUSH":
            tank.ready = clamp(tank.ready + 20, 0, 100)
            tank.risk = clamp(tank.risk + 1, 0, 6)
            self.used_rush = True
            if self.price_up:
                self.cash -= 2
        elif card.verb == "SAMPLE":
            tank.ready = clamp(tank.ready + 5, 0, 100)
            if not self.next_threat_preview:
                self.next_threat_preview = random.choice(self._all_threats())
        elif card.verb == "BOTTLE":
            tank.locked = True
            self.used_bottle = True
            self._resolve_bottle(tank)

        self.hand.remove(card)
        self.discard.append(card)

    def _resolve_bottle(self, tank: TankState) -> None:
        success = (
            85 <= tank.ready <= 95
            and abs(tank.balance) <= 1
            and tank.risk <= 2
        )
        if self.bad_batch and tank.risk >= 3:
            success = False
        if success:
            self.cash += 5
            self.rep += 1
            tank.ready = 0
            tank.balance = 0
            tank.risk = 0
        else:
            self.rep -= 1
            tank.risk = clamp(tank.risk + 1, 0, 6)

    def _end_day(self) -> None:
        for tank in self.tanks:
            tank.ready = clamp(tank.ready + 10, 0, 100)
            tank.balance = clamp(shift_toward_zero(tank.balance, 1), -3, 3)
            if abs(tank.balance) >= 2:
                tank.risk = clamp(tank.risk + 1, 0, 6)

        if self.humid:
            for tank in self.tanks:
                if abs(tank.balance) >= 2:
                    tank.risk = clamp(tank.risk + 2, 0, 6)

        if self.inspection_required and not self.used_clean:
            for tank in self.tanks:
                tank.risk = clamp(tank.risk + 2, 0, 6)

        if self.urgent_order_days is not None:
            if self.used_bottle:
                self.urgent_order_days = None
            else:
                self.urgent_order_days -= 1
                if self.urgent_order_days <= 0:
                    self.rep -= 10
                    self.urgent_order_days = None

        for tank in self.tanks:
            tank.locked = False

        self.day += 1
        self.hand_size = 5
        self._start_day()

    def update(self):
        self.top_day_text.text = f"Day {self.day}"
        self.top_cash_text.text = f"Cash {self.cash}"
        self.top_rep_text.text = f"Rep {self.rep}"

        threat_name = self.current_threat.name if self.current_threat else ""
        self.threat_name.text = threat_name
        if self.next_threat_preview:
            self.next_threat_text.text = f"Next: {self.next_threat_preview.name}"
        else:
            self.next_threat_text.text = ""

        mouse_pos = Rs.mousePos()
        if Rs.userJustLeftClicked():
            if self.end_day_button.collidepoint(mouse_pos.toTuple()):
                self._end_day()
                return
            for index, rect in enumerate(self._tank_rects()):
                if rect.collidepoint(mouse_pos.toTuple()):
                    self.active_tank_index = index
                    return
            for card, rect in self._hand_rects():
                if rect.collidepoint(mouse_pos.toTuple()):
                    self._play_card(card)
                    return

    def draw(self):
        Rs.fillScreen(Cs.grey75)
        screen = Rs.screen

        self._draw_top_bar(screen)
        self._draw_tanks(screen)
        self._draw_threat(screen)
        self._draw_hand(screen)
        self._draw_ap(screen)
        self._draw_end_day(screen)

    def _draw_top_bar(self, screen: pygame.Surface) -> None:
        self.top_day_text.pos = (40, 20)
        self.top_cash_text.pos = (220, 20)
        self.top_rep_text.pos = (420, 20)
        self.top_day_text.draw()
        self.top_cash_text.draw()
        self.top_rep_text.draw()

    def _draw_rect(self, rect: pygame.Rect, color, *, radius: int = 0) -> None:
        rectObj(rect, color=color, radius=radius).draw()

    def _draw_rect_with_border(
        self,
        rect: pygame.Rect,
        *,
        fill_color,
        border_color,
        border: int = 2,
        radius: int = 0,
    ) -> None:
        self._draw_rect(rect, border_color, radius=radius)
        inner = rect.inflate(-2 * border, -2 * border)
        if inner.width > 0 and inner.height > 0:
            self._draw_rect(inner, fill_color, radius=radius)

    def _draw_tanks(self, screen: pygame.Surface) -> None:
        for index, rect in enumerate(self._tank_rects()):
            selected = index == self.active_tank_index
            border_color = WARNING if selected else Cs.black
            backdrop = rect.inflate(10, 10)
            self._draw_rect_with_border(
                backdrop,
                fill_color=Cs.lightgrey,
                border_color=Cs.grey25,
                border=1,
            )
            self._draw_rect_with_border(
                rect,
                fill_color=Cs.white,
                border_color=border_color,
                border=2,
            )
            tank = self.tanks[index]

            label = textObj(f"TANK {index + 1}", size=18, color=Cs.black)
            label.pos = (rect.x + 12, rect.y + 10)
            label.draw()

            if tank.locked:
                lock_text = textObj("LOCK", size=18, color=WARNING)
                lock_text.pos = (rect.right - 60, rect.y + 10)
                lock_text.draw()

            ready_label = textObj("Ready", size=16, color=Cs.black)
            ready_label.pos = (rect.x + 12, rect.y + 50)
            ready_label.draw()
            ready_value = textObj(f"{tank.ready}%", size=16, color=Cs.black)
            ready_value.pos = (rect.right - 70, rect.y + 50)
            ready_value.draw()

            bar_x = rect.x + 80
            bar_y = rect.y + 54
            bar_w = rect.width - 100
            bar_h = 12
            bar_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
            self._draw_rect_with_border(
                bar_rect,
                fill_color=Cs.white,
                border_color=Cs.black,
                border=1,
            )
            fill_w = int(bar_w * (tank.ready / 100))
            if fill_w > 0:
                self._draw_rect(
                    pygame.Rect(bar_x, bar_y, fill_w, bar_h),
                    Cs.black,
                )

            balance_label = textObj("Balance", size=16, color=Cs.black)
            balance_label.pos = (rect.x + 12, rect.y + 85)
            balance_label.draw()
            balance_value = textObj(f"{tank.balance:+d}", size=16, color=Cs.black)
            balance_value.pos = (rect.right - 70, rect.y + 85)
            balance_value.draw()

            line_x = rect.x + 90
            line_y = rect.y + 95
            line_w = rect.width - 120
            pygame.draw.line(screen, Cs.black, (line_x, line_y), (line_x + line_w, line_y), 2)
            for step in range(7):
                tick_x = line_x + int(line_w * step / 6)
                pygame.draw.line(screen, Cs.black, (tick_x, line_y - 6), (tick_x, line_y + 6), 1)
            balance_pos = (tank.balance + 3) / 6
            dot_x = line_x + int(line_w * balance_pos)
            pygame.draw.circle(screen, Cs.black, (dot_x, line_y), 6)

            risk_label = textObj("Risk", size=16, color=Cs.black)
            risk_label.pos = (rect.x + 12, rect.y + 125)
            risk_label.draw()
            risk_value = textObj(f"{tank.risk}/6", size=16, color=Cs.black)
            risk_value.pos = (rect.right - 70, rect.y + 125)
            risk_value.draw()

            dot_start_x = rect.x + 70
            dot_y = rect.y + 135
            for dot in range(6):
                color = Cs.black if dot < tank.risk else Cs.white
                pygame.draw.circle(screen, color, (dot_start_x + dot * 22, dot_y), 6)
                pygame.draw.circle(screen, Cs.black, (dot_start_x + dot * 22, dot_y), 6, 1)

    def _draw_threat(self, screen: pygame.Surface) -> None:
        rect = self._threat_rect()
        self._draw_rect_with_border(
            rect,
            fill_color=Cs.white,
            border_color=WARNING,
            border=2,
        )
        self.threat_title.pos = (rect.x + 16, rect.y + 12)
        self.threat_title.draw()
        self.threat_name.pos = (rect.x + 16, rect.y + 50)
        self.threat_name.draw()
        if self.next_threat_text.text:
            self.next_threat_text.pos = (rect.x + 16, rect.y + 100)
            self.next_threat_text.draw()

    def _draw_hand(self, screen: pygame.Surface) -> None:
        for card, rect in self._hand_rects():
            enabled = self.ap > 0 and not self.tanks[self.active_tank_index].locked
            border_color = Cs.black if enabled else WARNING
            backdrop = rect.inflate(8, 8)
            self._draw_rect_with_border(
                backdrop,
                fill_color=Cs.lightgrey,
                border_color=Cs.grey25,
                border=1,
            )
            self._draw_rect_with_border(
                rect,
                fill_color=Cs.white,
                border_color=border_color,
                border=2,
            )
            verb_text = textObj(card.verb, size=24, color=Cs.black)
            verb_text.pos = (rect.x + 12, rect.y + 12)
            verb_text.draw()
            effect_text = textObj(card.effect_text, size=16, color=Cs.black)
            effect_text.pos = (rect.x + 12, rect.y + 52)
            effect_text.draw()

    def _draw_ap(self, screen: pygame.Surface) -> None:
        ap_label = textObj("AP", size=18, color=Cs.black)
        ap_label.pos = (40, self.screen_h - 90)
        ap_label.draw()
        self.ap_text.text = f"{self.ap}/2"
        self.ap_text.pos = (70, self.screen_h - 90)
        self.ap_text.draw()
        for idx in range(2):
            color = Cs.black if idx < self.ap else Cs.white
            pygame.draw.circle(screen, color, (90 + idx * 20, self.screen_h - 78), 6)
            pygame.draw.circle(screen, Cs.black, (90 + idx * 20, self.screen_h - 78), 6, 1)

    def _draw_end_day(self, screen: pygame.Surface) -> None:
        self._draw_rect_with_border(
            self.end_day_button,
            fill_color=Cs.white,
            border_color=Cs.black,
            border=2,
        )
        label = textObj("END DAY", size=18, color=Cs.black)
        label.pos = (self.end_day_button.x + 18, self.end_day_button.y + 12)
        label.draw()

    def _tank_rects(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(40, 110, 360, 180),
            pygame.Rect(40, 320, 360, 180),
        ]

    def _threat_rect(self) -> pygame.Rect:
        return pygame.Rect(640, 200, 560, 180)

    def _hand_rects(self) -> list[tuple[CardDef, pygame.Rect]]:
        card_w = 170
        card_h = 110
        gap = 12
        total_w = len(self.hand) * card_w + max(0, len(self.hand) - 1) * gap
        start_x = (self.screen_w - total_w) // 2
        y = self.screen_h - 160
        rects = []
        for index, card in enumerate(self.hand):
            rects.append((card, pygame.Rect(start_x + index * (card_w + gap), y, card_w, card_h)))
        return rects


class Scenes:
    gameScene = MinimalBrewScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="Minimal Brew",
    )
    game.setCurrentScene(Scenes.gameScene)
    game.run()
