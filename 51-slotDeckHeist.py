from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from REMOLib.core import *


HOOK_TEXT = "카드로 슬롯을 조작해서, 한 스핀으로 전투를 터뜨리는 덱빌더"
KEYWORDS = "키워드: 리그/홀드/너지/리롤/와일드/잭팟"


@dataclass
class SymbolDef:
    name: str
    value: int
    tags: tuple[str, ...]
    weight: int = 8
    special: str = ""


@dataclass
class CardDef:
    name: str
    cost: int
    category: str
    text: str
    heat: int = 0
    exhaust: bool = False


@dataclass
class EnemyState:
    name: str
    hp: int
    intent: int


class SlotDeckHeistScene(Scene):
    ROWS = 3
    REELS = 3

    def __init__(self):
        super().__init__()

    def initOnce(self):
        self.w, self.h = Rs.getWindowRes()
        self.random = random.Random()

        self.player_hp = 90
        self.player_block = 0
        self.gold = 0
        self.energy = 3
        self.turn = 1
        self.heat = 0
        self.audit_log = ""

        self.act = 1
        self.node = 1
        self.current_node_type = "전투"
        self.next_node_choices = ["이벤트", "전투", "상점", "휴식", "엘리트"]

        self.tag_weights = {
            "COIN": 1.0,
            "TECH": 1.0,
            "FRUIT": 1.0,
            "DEFENSE": 1.0,
            "CHAOS": 1.0,
        }
        self.extra_paylines = 0
        self.forced_break_weight = 0

        self.symbol_pool = self._build_symbol_pool()
        self.board = [[self._roll_symbol() for _ in range(self.REELS)] for _ in range(self.ROWS)]
        self.held_reels: set[int] = set()
        self.reel_nudges = [0, 0, 0]
        self.selected_reel = 0
        self.selected_cells: set[tuple[int, int]] = set()

        self.spin_multiplier = 1
        self.extra_spins = 0
        self.cashout_mode = False
        self.insurance_active = False
        self.pending_rerolls = 0

        self.last_spin_damage = 0
        self.last_spin_report = "아직 스핀 전"

        self.enemy = EnemyState("감사 보안요원", hp=65, intent=8)

        self.deck: list[CardDef] = []
        self.hand: list[CardDef] = []
        self.discard: list[CardDef] = []
        self._build_starter_deck()
        self._shuffle_deck()
        self._draw_cards(5)

    def _build_symbol_pool(self) -> list[SymbolDef]:
        return [
            SymbolDef("코인", 1, ("COIN",), 11),
            SymbolDef("금괴", 2, ("COIN",), 8),
            SymbolDef("지갑", 2, ("COIN",), 8),
            SymbolDef("ATM", 3, ("COIN",), 6),
            SymbolDef("금고", 4, ("COIN",), 5),
            SymbolDef("배터리", 1, ("TECH",), 11),
            SymbolDef("드론", 2, ("TECH",), 8),
            SymbolDef("서버", 2, ("TECH",), 8),
            SymbolDef("칩", 3, ("TECH",), 7),
            SymbolDef("레이저", 3, ("TECH",), 6),
            SymbolDef("체리", 1, ("FRUIT",), 11),
            SymbolDef("레몬", 1, ("FRUIT",), 10),
            SymbolDef("포도", 2, ("FRUIT",), 8),
            SymbolDef("수박", 3, ("FRUIT",), 6),
            SymbolDef("파인애플", 3, ("FRUIT",), 6),
            SymbolDef("방패", 1, ("DEFENSE",), 9),
            SymbolDef("벽", 2, ("DEFENSE",), 8),
            SymbolDef("수리봇", 2, ("DEFENSE", "TECH"), 7),
            SymbolDef("아머플레이트", 3, ("DEFENSE",), 6),
            SymbolDef("와일드", 0, ("WILD",), 4),
            SymbolDef("멀티플라이", 0, ("CHAOS",), 4, "MULT"),
            SymbolDef("스캐터", 0, ("CHAOS",), 4, "SCATTER"),
            SymbolDef("리스핀", 0, ("CHAOS",), 3, "RESPIN"),
            SymbolDef("폭탄", 2, ("CHAOS",), 7),
            SymbolDef("글리치", 1, ("CHAOS",), 7),
            SymbolDef("해커", 2, ("CHAOS",), 7),
            SymbolDef("훔치기", 2, ("CHAOS",), 7, "STEAL"),
            SymbolDef("고장", 0, ("CURSE",), 2),
            SymbolDef("압류", 0, ("CURSE",), 2),
            SymbolDef("잔고부족", 0, ("CURSE",), 2),
        ]

    def _build_starter_deck(self):
        self.deck = []
        self._add_cards("HOLD", 1, "즉발", "선택 릴 고정", 1, 3)
        self._add_cards("NUDGE ▲", 1, "즉발", "선택 릴 위로 1칸", 1, 2)
        self._add_cards("NUDGE ▼", 1, "즉발", "선택 릴 아래로 1칸", 1, 2)
        self._add_cards("REROLL", 1, "즉발", "선택 칸 1~3 재추첨", 1, 2)
        self._add_cards("INSURANCE", 1, "보험", "데미지 0이면 방어+12", 0, 2)
        self._add_cards("CLEANER", 1, "보험", "저주 1 제거, Heat -2", 0, 1)
        self._add_cards("DOUBLE DOWN", 1, "하이리스크", "이번 스핀 데미지 x2", 3, 1)
        self._add_cards("OVERLOAD", 2, "하이리스크", "스핀 +1회, 고장 심볼 추가", 2, 1)
        self._add_cards("WEIGHT COIN+", 2, "설치", "COIN 등장 확률 +20%", 0, 1)
        self._add_cards("PAYLINE +1", 2, "설치", "추가 페이라인 +1", 0, 1)
        self._add_cards("CASHOUT", 1, "보험", "데미지 절반, 골드 획득", 0, 1)

    def _add_cards(self, name, cost, category, text, heat, count):
        for _ in range(count):
            self.deck.append(CardDef(name, cost, category, text, heat))

    def _shuffle_deck(self):
        self.random.shuffle(self.deck)

    def _draw_cards(self, n: int):
        for _ in range(n):
            if not self.deck:
                self.deck, self.discard = self.discard, []
                self._shuffle_deck()
            if not self.deck:
                return
            self.hand.append(self.deck.pop())

    def _weighted_symbol_entries(self):
        entries = []
        for symbol in self.symbol_pool:
            weight = symbol.weight
            for tag in symbol.tags:
                weight = int(weight * self.tag_weights.get(tag, 1.0))
            if symbol.name == "고장":
                weight += self.forced_break_weight
            entries.extend([symbol] * max(1, weight))
        return entries

    def _roll_symbol(self) -> SymbolDef:
        return self.random.choice(self._weighted_symbol_entries())

    def _play_card(self, card: CardDef):
        if card.cost > self.energy:
            return
        self.energy -= card.cost
        self.heat = max(0, self.heat + card.heat)

        if card.name == "HOLD":
            if self.selected_reel in self.held_reels:
                self.held_reels.remove(self.selected_reel)
            else:
                self.held_reels.add(self.selected_reel)
        elif card.name == "NUDGE ▲":
            self.reel_nudges[self.selected_reel] -= 1
        elif card.name == "NUDGE ▼":
            self.reel_nudges[self.selected_reel] += 1
        elif card.name == "REROLL":
            self.pending_rerolls = min(3, max(1, len(self.selected_cells)))
        elif card.name == "INSURANCE":
            self.insurance_active = True
        elif card.name == "CLEANER":
            self._remove_one_curse()
            self.heat = max(0, self.heat - 2)
        elif card.name == "DOUBLE DOWN":
            self.spin_multiplier *= 2
        elif card.name == "OVERLOAD":
            self.extra_spins += 1
            self.forced_break_weight += 2
        elif card.name == "WEIGHT COIN+":
            self.tag_weights["COIN"] += 0.2
        elif card.name == "PAYLINE +1":
            self.extra_paylines += 1
        elif card.name == "CASHOUT":
            self.cashout_mode = True

        self.hand.remove(card)
        self.discard.append(card)

    def _remove_one_curse(self):
        for pile in (self.hand, self.deck, self.discard):
            for c in pile:
                if "CURSE" in c.name:
                    pile.remove(c)
                    return

    def _spin_once(self):
        original_board = [row[:] for row in self.board]
        for col in range(self.REELS):
            if col in self.held_reels:
                continue
            for row in range(self.ROWS):
                self.board[row][col] = self._roll_symbol()

        for col, offset in enumerate(self.reel_nudges):
            if offset == 0:
                continue
            column = [self.board[r][col] for r in range(self.ROWS)]
            shift = offset % self.ROWS
            column = column[-shift:] + column[:-shift]
            for r in range(self.ROWS):
                self.board[r][col] = column[r]

        if self.pending_rerolls > 0:
            targets = list(self.selected_cells)
            self.random.shuffle(targets)
            for row, col in targets[: self.pending_rerolls]:
                self.board[row][col] = self._roll_symbol()

        dmg, block_gain, report = self._score_board()
        self.last_spin_report = report
        self.last_spin_damage = dmg

        if self.cashout_mode:
            cash = dmg // 2
            dmg //= 2
            self.gold += cash
            self.last_spin_report += f" | CASHOUT +{cash}G"

        self.enemy.hp -= dmg
        self.player_block += block_gain

        if self.insurance_active and dmg == 0:
            self.player_block += 12
            self.last_spin_report += " | INSURANCE 발동(+12 Block)"

        if any(s.special == "RESPIN" for row in self.board for s in row):
            self.extra_spins += 1
            self.last_spin_report += " | RESPIN +1"

        if self.enemy.hp <= 0:
            self._win_combat()
            return

        self.extra_spins -= 1
        if self.extra_spins >= 0:
            self._spin_cleanup()
            return

        self.extra_spins = 0
        self._enemy_turn()
        self._start_next_turn()
        self._spin_cleanup()

    def _spin_cleanup(self):
        self.spin_multiplier = 1
        self.pending_rerolls = 0
        self.cashout_mode = False
        self.insurance_active = False
        self.reel_nudges = [0, 0, 0]

    def _paylines(self):
        lines = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(2, 0), (1, 1), (0, 2)],
        ]
        extra_candidates = [
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(1, 0), (0, 1), (1, 2)],
            [(1, 0), (2, 1), (1, 2)],
        ]
        lines.extend(extra_candidates[: self.extra_paylines])
        return lines

    def _line_tag_match(self, symbols: list[SymbolDef]):
        candidate_tags = None
        for symbol in symbols:
            if "WILD" in symbol.tags:
                continue
            tag_set = set(symbol.tags)
            candidate_tags = tag_set if candidate_tags is None else candidate_tags.intersection(tag_set)
        return candidate_tags if candidate_tags else set()

    def _score_board(self):
        total_damage = 0
        total_block = 0
        line_reports = []

        for idx, line in enumerate(self._paylines(), start=1):
            symbols = [self.board[r][c] for r, c in line]
            tags = self._line_tag_match(symbols)
            if not tags:
                continue
            base = sum(s.value for s in symbols)
            line_mult = 1
            if any(s.special == "MULT" for s in symbols):
                line_mult += 1
            if len({s.name for s in symbols}) == 1:
                line_mult += 1
            line_value = base * line_mult
            total_damage += line_value
            line_reports.append(f"L{idx}:{line_value}")

            if "DEFENSE" in tags:
                total_block += max(1, line_value // 2)

        scatter_count = sum(1 for row in self.board for s in row if s.special == "SCATTER")
        if scatter_count >= 2:
            self.gold += scatter_count
            line_reports.append(f"SCATTER +{scatter_count}G")

        steal_count = sum(1 for row in self.board for s in row if s.special == "STEAL")
        if steal_count > 0:
            self.gold += steal_count
            line_reports.append(f"STEAL +{steal_count}G")

        total_damage *= self.spin_multiplier
        return total_damage, total_block, " / ".join(line_reports) if line_reports else "노라인"

    def _enemy_turn(self):
        incoming = max(0, self.enemy.intent - self.player_block)
        self.player_block = max(0, self.player_block - self.enemy.intent)
        self.player_hp -= incoming
        self.enemy.intent = self.random.randint(7, 13) + (self.act - 1)

        if self.heat >= 8:
            self._trigger_audit()

        if self.player_hp <= 0:
            self.last_spin_report = "플레이어 다운! 게임 오버"

    def _trigger_audit(self):
        self.heat -= 5
        event = self.random.choice(["curse", "price", "jam"])
        if event == "curse":
            curse = CardDef("CURSE BUGGED CHIP", 0, "저주", "손에서 버려짐", 0)
            self.discard.append(curse)
            self.audit_log = "[AUDIT] 저주 카드가 덱에 추가됨"
        elif event == "price":
            self.gold = max(0, self.gold - 4)
            self.audit_log = "[AUDIT] 벌금 -4 Gold"
        else:
            self.forced_break_weight += 2
            self.audit_log = "[AUDIT] 릴 고장 확률 증가"

    def _win_combat(self):
        reward = 12 + self.act * 3
        self.gold += reward
        self.node += 1
        if self.node > 4:
            self.act += 1
            self.node = 1
        self.current_node_type = self.random.choice(self.next_node_choices)
        self.enemy = EnemyState(f"Act {self.act} 적", hp=60 + self.act * 15, intent=8 + self.act)
        self.last_spin_report = f"전투 승리! +{reward} Gold, 다음 노드: {self.current_node_type}"

    def _start_next_turn(self):
        self.turn += 1
        self.energy = 3
        self.player_block = max(0, self.player_block)
        if self.hand:
            self.discard.extend(self.hand)
            self.hand.clear()
        self._draw_cards(5)

    def _handle_click(self):
        if not Rs.userJustLeftClicked():
            return
        m = Rs.mousePos().toTuple()

        for idx, rect in enumerate(self._reel_selector_rects()):
            if rect.collidepoint(m):
                self.selected_reel = idx
                return

        for row, col, rect in self._board_cell_rects():
            if rect.collidepoint(m):
                key = (row, col)
                if key in self.selected_cells:
                    self.selected_cells.remove(key)
                else:
                    self.selected_cells.add(key)
                return

        if self._spin_button_rect().collidepoint(m):
            self._spin_once()
            return

        for card, rect in self._hand_rects():
            if rect.collidepoint(m):
                self._play_card(card)
                return

    def update(self):
        self._handle_click()

    def draw(self):
        Rs.fillScreen(Cs.grey75)
        self._draw_header()
        self._draw_status()
        self._draw_enemy_panel()
        self._draw_board()
        self._draw_controls()
        self._draw_hand()

    def _draw_rect_with_border(
        self,
        rect: pygame.Rect,
        *,
        fill_color,
        border_color,
        border: int = 2,
    ):
        rectObj(rect, color=border_color).draw()
        inner = rect.inflate(-border * 2, -border * 2)
        if inner.width > 0 and inner.height > 0:
            rectObj(inner, color=fill_color).draw()

    def _draw_header(self):
        textObj(HOOK_TEXT, pos=(24, 16), size=26, color=Cs.black).draw()
        textObj(KEYWORDS, pos=(24, 48), size=17, color=Cs.black).draw()

    def _draw_status(self):
        textObj(f"HP {self.player_hp}  Block {self.player_block}  Gold {self.gold}", pos=(24, 84), size=21, color=Cs.black).draw()
        textObj(f"Turn {self.turn}  Energy {self.energy}/3  Heat {self.heat}", pos=(24, 112), size=21, color=Cs.black).draw()
        textObj(f"Act {self.act}-{self.node} | 노드:{self.current_node_type} | 선택 릴:{self.selected_reel+1}", pos=(24, 140), size=18, color=Cs.black).draw()
        if self.audit_log:
            textObj(self.audit_log, pos=(24, 166), size=17, color=(160, 30, 30)).draw()

    def _draw_enemy_panel(self):
        panel = pygame.Rect(self.w - 360, 84, 320, 120)
        self._draw_rect_with_border(
            panel,
            fill_color=Cs.white,
            border_color=Cs.black,
            border=2,
        )
        textObj(self.enemy.name, pos=(panel.x + 14, panel.y + 12), size=22, color=Cs.black).draw()
        textObj(f"HP {self.enemy.hp}", pos=(panel.x + 14, panel.y + 48), size=20, color=Cs.black).draw()
        textObj(f"Intent: 공격 {self.enemy.intent}", pos=(panel.x + 14, panel.y + 76), size=20, color=Cs.black).draw()

    def _draw_board(self):
        for row, col, rect in self._board_cell_rects():
            symbol = self.board[row][col]
            selected = (row, col) in self.selected_cells
            fill = (255, 247, 200) if selected else Cs.white
            self._draw_rect_with_border(
                rect,
                fill_color=fill,
                border_color=Cs.black,
                border=2,
            )
            textObj(symbol.name, pos=(rect.x + 8, rect.y + 10), size=18, color=Cs.black).draw()
            textObj(f"{symbol.value}", pos=(rect.x + 8, rect.y + 40), size=16, color=Cs.black).draw()
            if symbol.tags:
                textObj(symbol.tags[0], pos=(rect.x + 8, rect.y + 62), size=14, color=Cs.black).draw()

        for idx, rect in enumerate(self._reel_selector_rects()):
            selected = idx == self.selected_reel
            held = idx in self.held_reels
            color = (255, 220, 180) if selected else Cs.lightgrey
            self._draw_rect_with_border(
                rect,
                fill_color=color,
                border_color=Cs.black,
                border=2,
            )
            label = f"REEL {idx+1}"
            if held:
                label += " [HOLD]"
            if self.reel_nudges[idx] != 0:
                label += f" N:{self.reel_nudges[idx]}"
            textObj(label, pos=(rect.x + 8, rect.y + 8), size=16, color=Cs.black).draw()

    def _draw_controls(self):
        spin_rect = self._spin_button_rect()
        self._draw_rect_with_border(
            spin_rect,
            fill_color=(255, 210, 90),
            border_color=Cs.black,
            border=3,
        )
        textObj("SPIN!", pos=(spin_rect.x + 30, spin_rect.y + 12), size=32, color=Cs.black).draw()
        textObj(f"결과: {self.last_spin_report}", pos=(24, 500), size=18, color=Cs.black).draw()

    def _draw_hand(self):
        for card, rect in self._hand_rects():
            usable = card.cost <= self.energy
            fill = Cs.white if usable else Cs.grey75
            self._draw_rect_with_border(
                rect,
                fill_color=fill,
                border_color=Cs.black,
                border=2,
            )
            textObj(f"{card.name} ({card.cost})", pos=(rect.x + 8, rect.y + 8), size=16, color=Cs.black).draw()
            textObj(card.category, pos=(rect.x + 8, rect.y + 32), size=14, color=Cs.black).draw()
            textObj(card.text, pos=(rect.x + 8, rect.y + 52), size=14, color=Cs.black).draw()
            if card.heat > 0:
                textObj(f"Heat +{card.heat}", pos=(rect.x + 8, rect.y + 72), size=14, color=(170, 50, 50)).draw()

    def _board_cell_rects(self):
        start_x = 140
        start_y = 220
        cell_w = 140
        cell_h = 88
        gap = 10
        for row in range(self.ROWS):
            for col in range(self.REELS):
                x = start_x + col * (cell_w + gap)
                y = start_y + row * (cell_h + gap)
                yield row, col, pygame.Rect(x, y, cell_w, cell_h)

    def _reel_selector_rects(self):
        start_x = 140
        y = 186
        w = 140
        h = 30
        gap = 10
        return [pygame.Rect(start_x + i * (w + gap), y, w, h) for i in range(self.REELS)]

    def _spin_button_rect(self):
        return pygame.Rect(600, 300, 150, 70)

    def _hand_rects(self):
        card_w = 180
        card_h = 96
        gap = 8
        total_w = len(self.hand) * card_w + max(0, len(self.hand) - 1) * gap
        x = (self.w - total_w) // 2
        y = self.h - 120
        rects = []
        for i, c in enumerate(self.hand):
            rects.append((c, pygame.Rect(x + i * (card_w + gap), y, card_w, card_h)))
        return rects


class Scenes:
    game = SlotDeckHeistScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="Slot Deck Heist",
    )
    game.setCurrentScene(Scenes.game)
    game.run()
