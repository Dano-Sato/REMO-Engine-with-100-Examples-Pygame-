from __future__ import annotations

import random

import pygame

from REMOLib.core import *


class Card:
    def __init__(self, name: str, cost: int, card_type: str, desc: str):
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.desc = desc


class CardView(rectObj):
    COLOR_MAP = {
        "Attack": Cs.dark(Cs.red),
        "Skill": Cs.dark(Cs.steelblue),
        "Power": Cs.dark(Cs.purple),
        "Status": Cs.dark(Cs.grey),
    }

    def __init__(self, card: Card, on_play):
        super().__init__(pygame.Rect(0, 0, 200, 260), color=self.COLOR_MAP.get(card.card_type, Cs.dark(Cs.grey)), edge=6)
        self.card = card
        self.on_play = on_play
        self.playable = True

        self.name_text = textObj(card.name, size=24, color=Cs.white)
        self.name_text.setParent(self, depth=1)
        self.name_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 18)

        self.cost_badge = rectObj(pygame.Rect(0, 0, 56, 56), color=Cs.dark(Cs.tiffanyBlue), radius=16, edge=3)
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.topleft = RPoint(6, 6)

        self.cost_text = textObj(str(card.cost), size=28, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.type_text = textObj(card.card_type, size=18, color=Cs.grey75)
        self.type_text.setParent(self, depth=1)
        self.type_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 58)

        self.desc_text = longTextObj(card.desc, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=158)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.type_text.rect.bottom + 12

    def refresh(self, energy: int):
        self.playable = energy >= self.card.cost
        alpha = 255 if self.playable else 145
        self.alpha = alpha
        self.name_text.alpha = alpha
        self.cost_badge.alpha = alpha
        self.cost_text.alpha = alpha
        self.type_text.alpha = alpha
        self.desc_text.alpha = alpha

    def update(self):
        hovered = self.collideMouse() and self.playable
        self.color = Cs.light(self.COLOR_MAP.get(self.card.card_type, Cs.dark(Cs.grey))) if hovered else self.COLOR_MAP.get(
            self.card.card_type, Cs.dark(Cs.grey)
        )
        if hovered and Rs.userJustLeftClicked():
            self.on_play()


class DreamForgeScene(Scene):
    HAND_SIZE = 5

    def initOnce(self):
        self.level = 1
        self.max_hp = 64
        self.hp = self.max_hp
        self.energy = 3
        self.block = 0
        self.sparks = 0
        self.combo = 0
        self.overheat = 0
        self.intent_bonus = 0
        self.reward_pending = False
        self.game_over = False

        self.master_deck = self.make_starter_deck()
        self.draw_pile = []
        self.discard_pile = []
        self.hand: list[Card] = []
        self.hand_widgets: list[CardView] = []

        self.enemy_name = "거울 기사"
        self.enemy_hp = 36
        self.enemy_max_hp = 36
        self.enemy_intent = ("Attack", 6)

        self.log_lines: list[str] = []

        self.info_layout = layoutObj(pos=RPoint(46, 38), isVertical=True, spacing=14)
        self.player_text = textObj("", size=26, color=Cs.white)
        self.enemy_text = textObj("", size=26, color=Cs.white)
        self.intent_text = textObj("", size=24, color=Cs.tiffanyBlue)
        self.deck_text = textObj("", size=21, color=Cs.grey75)
        self.tips_text = textObj("", size=21, color=Cs.yellow)
        for obj in (self.player_text, self.enemy_text, self.intent_text, self.deck_text, self.tips_text):
            obj.setParent(self.info_layout)

        self.log_box = longTextObj("", pos=RPoint(46, 430), size=21, color=Cs.white, textWidth=620)

        self.hand_layout = layoutObj(pos=RPoint(84, 700), isVertical=False, spacing=44)

        self.end_turn_btn = textButton("턴 종료", pygame.Rect(0, 0, 190, 62), color=Cs.dark(Cs.orange), textColor=Cs.white)
        self.end_turn_btn.pos = RPoint(1240, 42)
        self.end_turn_btn.connect(self.end_turn)

        self.restart_btn = textButton("다시 시작", pygame.Rect(0, 0, 230, 68), color=Cs.dark(Cs.red), textColor=Cs.white)
        self.restart_btn.pos = RPoint(1190, 130)
        self.restart_btn.connect(self.restart_run)

        self.reward_title = textObj("", size=30, color=Cs.yellow)
        self.reward_title.pos = RPoint(790, 360)
        self.reward_buttons: list[textButton] = []

        self.start_combat(new_floor=True)

    def init(self):
        return

    def make_starter_deck(self) -> list[Card]:
        deck = []
        deck += [Card("Flare Slash", 1, "Attack", "피해 6.")] * 4
        deck += [Card("Aegis Stitch", 1, "Skill", "방어도 7.")] * 4
        deck += [Card("Ignite", 1, "Skill", "Sparks +2, 카드 1장 드로우.")] * 2
        deck += [Card("Echo Slash", 2, "Attack", "피해 7 + Combo x2.")] * 1
        return deck

    def add_log(self, text: str):
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-8:]
        self.log_box.text = "\n".join(self.log_lines)

    def reshuffle(self):
        if not self.draw_pile and self.discard_pile:
            random.shuffle(self.discard_pile)
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            self.add_log("버림 더미를 섞어 드로우 더미로 가져왔습니다.")

    def draw_cards(self, n: int):
        for _ in range(n):
            if not self.draw_pile:
                self.reshuffle()
            if not self.draw_pile:
                return
            self.hand.append(self.draw_pile.pop())

    def start_combat(self, *, new_floor: bool):
        if new_floor:
            self.enemy_name, self.enemy_max_hp = self.roll_enemy()
            self.enemy_hp = self.enemy_max_hp
            self.add_log(f"{self.enemy_name}이(가) 꿈의 제련소를 지킵니다.")
        self.block = 0
        self.combo = 0
        self.overheat = max(0, self.overheat - 1)
        self.energy = max(3 - self.overheat, 1)

        self.draw_pile = self.master_deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile = []
        self.hand = []
        self.draw_cards(DreamForgeScene.HAND_SIZE)
        self.roll_intent()
        self.refresh_ui()

    def roll_enemy(self):
        pool = [
            ("거울 기사", 36),
            ("재의 마법사", 34),
            ("심연 드론", 40),
            ("시간 거미", 38),
        ]
        boss_pool = [
            ("황혼 용광로", 62),
            ("무한 복제체", 58),
        ]
        if self.level % 4 == 0:
            name, hp = random.choice(boss_pool)
        else:
            name, hp = random.choice(pool)
        return name, hp + self.level * 2

    def roll_intent(self):
        if self.enemy_name == "시간 거미":
            if random.random() < 0.5:
                self.enemy_intent = ("Hex", 1)
            else:
                self.enemy_intent = ("Attack", 7 + self.level // 2 + self.intent_bonus)
        elif self.enemy_name == "황혼 용광로":
            if random.random() < 0.35:
                self.enemy_intent = ("Charge", 2)
            else:
                self.enemy_intent = ("Attack", 10 + self.level // 2 + self.intent_bonus)
        else:
            r = random.random()
            if r < 0.2:
                self.enemy_intent = ("Charge", 2)
            elif r < 0.42:
                self.enemy_intent = ("Hex", 1)
            else:
                self.enemy_intent = ("Attack", 6 + self.level // 3 + self.intent_bonus)

    def rebuild_hand(self):
        self.hand_layout.clearChilds(0)
        self.hand_widgets.clear()
        for card in self.hand:
            view = CardView(card, on_play=lambda c=card: self.play_card(c))
            view.setParent(self.hand_layout)
            view.refresh(self.energy)
            self.hand_widgets.append(view)
        self.hand_layout.adjustLayout()

    def refresh_ui(self):
        self.player_text.text = (
            f"HP {self.hp}/{self.max_hp} | 에너지 {self.energy} | 방어 {self.block} | Sparks {self.sparks} | Combo {self.combo} | Overheat {self.overheat}"
        )
        self.enemy_text.text = f"{self.enemy_name} HP {self.enemy_hp}/{self.enemy_max_hp} | 층 {self.level}"
        intent_name = {"Attack": "공격", "Hex": "해킹", "Charge": "충전"}[self.enemy_intent[0]]
        self.intent_text.text = f"적 의도: {intent_name} {self.enemy_intent[1]}"
        self.deck_text.text = f"드로우 {len(self.draw_pile)} · 버림 {len(self.discard_pile)} · 손패 {len(self.hand)}"
        self.tips_text.text = "팁: Sparks를 모아 Prism Beam으로 폭발시키세요."
        self.info_layout.adjustLayout()
        self.rebuild_hand()

    def gain_block(self, amount: int):
        self.block += amount

    def deal_damage(self, amount: int):
        self.enemy_hp = max(0, self.enemy_hp - amount)

    def play_card(self, card: Card):
        if self.reward_pending or self.game_over:
            return
        if card not in self.hand or card.cost > self.energy:
            return
        self.energy -= card.cost

        if card.name == "Flare Slash":
            self.deal_damage(6)
            self.combo += 1
            self.add_log("Flare Slash: 피해 6")
        elif card.name == "Aegis Stitch":
            self.gain_block(7)
            self.add_log("Aegis Stitch: 방어도 +7")
        elif card.name == "Ignite":
            self.sparks += 2
            self.draw_cards(1)
            self.add_log("Ignite: Sparks +2, 드로우 1")
        elif card.name == "Echo Slash":
            dmg = 7 + self.combo * 2
            self.deal_damage(dmg)
            self.combo += 1
            self.add_log(f"Echo Slash: 피해 {dmg}")
        elif card.name == "Prism Beam":
            dmg = 5 + self.sparks * 3
            self.deal_damage(dmg)
            self.sparks = 0
            self.combo += 1
            self.add_log(f"Prism Beam: 피해 {dmg}, Sparks 전부 소모")
        elif card.name == "Overclock":
            self.energy += 2
            self.overheat += 1
            self.add_log("Overclock: 에너지 +2, Overheat +1")
        elif card.name == "Recycle":
            if self.discard_pile:
                picked = random.choice(self.discard_pile)
                self.discard_pile.remove(picked)
                self.hand.append(picked)
                self.add_log(f"Recycle: {picked.name} 회수")
            else:
                self.draw_cards(1)
                self.add_log("Recycle: 버림 더미가 없어 드로우 1")
        elif card.name == "Glitch":
            self.add_log("Glitch: 방해 카드라 효과가 없습니다.")

        self.hand.remove(card)
        self.discard_pile.append(card)

        if self.enemy_hp <= 0:
            self.win_combat()
            return

        self.refresh_ui()

    def end_turn(self):
        if self.reward_pending or self.game_over:
            return
        self.resolve_enemy_turn()
        if self.hp <= 0:
            self.game_over = True
            self.add_log("당신의 의식이 붕괴했습니다. 다시 시작해 보세요.")
            self.refresh_ui()
            return

        self.block = 0
        self.combo = 0
        self.energy = max(3 - self.overheat, 1)
        self.overheat = max(0, self.overheat - 1)

        self.draw_cards(DreamForgeScene.HAND_SIZE - len(self.hand))
        self.roll_intent()
        self.refresh_ui()

    def resolve_enemy_turn(self):
        kind, value = self.enemy_intent
        if kind == "Attack":
            dmg = max(0, value - self.block)
            self.block = max(0, self.block - value)
            self.hp = max(0, self.hp - dmg)
            self.add_log(f"적 공격 {value} → 실제 피해 {dmg}")
            self.intent_bonus = 0
        elif kind == "Hex":
            self.discard_pile.append(Card("Glitch", 1, "Status", "효과 없음."))
            self.add_log("적 해킹: Glitch 카드가 버림 더미에 추가됩니다.")
        elif kind == "Charge":
            self.intent_bonus += value
            self.add_log(f"적 충전: 다음 공격 +{value}")

    def win_combat(self):
        self.reward_pending = True
        self.level += 1
        self.hp = min(self.max_hp, self.hp + 7)
        self.add_log("전투 승리! 카드 보상 1장을 선택하세요. HP 7 회복.")
        self.prepare_reward_buttons()
        self.refresh_ui()

    def prepare_reward_buttons(self):
        self.reward_title.text = "보상 선택: 덱에 1장을 추가"
        self.reward_title.alpha = 255
        for button in self.reward_buttons:
            button.isVisible = False
        self.reward_buttons.clear()

        reward_pool = [
            Card("Prism Beam", 2, "Attack", "피해 5 + Sparks x3, Sparks 초기화."),
            Card("Overclock", 0, "Power", "에너지 +2, Overheat +1."),
            Card("Recycle", 1, "Skill", "버림 더미 카드 1장 회수."),
            Card("Echo Slash", 2, "Attack", "피해 7 + Combo x2."),
            Card("Ignite", 1, "Skill", "Sparks +2, 카드 1장 드로우."),
            Card("Aegis Stitch", 1, "Skill", "방어도 7."),
        ]
        picks = random.sample(reward_pool, 3)
        for idx, card in enumerate(picks):
            button = textButton(
                f"{card.name} (비용 {card.cost})\n{card.desc}",
                pygame.Rect(0, 0, 460, 88),
                color=Cs.dark(Cs.seagreen),
                textColor=Cs.white,
            )
            button.pos = RPoint(720, 430 + idx * 100)
            button.connect(lambda c=card: self.pick_reward(c))
            self.reward_buttons.append(button)

    def pick_reward(self, card: Card):
        if not self.reward_pending:
            return
        self.master_deck.append(card)
        self.reward_pending = False
        self.reward_title.text = ""
        for button in self.reward_buttons:
            button.isVisible = False
        self.reward_buttons.clear()
        self.add_log(f"{card.name}을(를) 덱에 추가했습니다.")
        self.start_combat(new_floor=True)

    def restart_run(self):
        self.level = 1
        self.hp = self.max_hp
        self.energy = 3
        self.block = 0
        self.sparks = 0
        self.combo = 0
        self.overheat = 0
        self.intent_bonus = 0
        self.reward_pending = False
        self.game_over = False
        self.master_deck = self.make_starter_deck()
        self.log_lines.clear()
        self.reward_title.text = ""
        for button in self.reward_buttons:
            button.isVisible = False
        self.reward_buttons.clear()
        self.start_combat(new_floor=True)

    def update(self):
        if self.reward_pending:
            self.reward_title.draw()
            for button in self.reward_buttons:
                button.update()
        self.end_turn_btn.update()
        if self.game_over:
            self.restart_btn.update()


class Scenes:
    mainScene = DreamForgeScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1920, 1080),
        screen_size=(1920, 1080),
        fullscreen=False,
        caption="Dream Forge Deckbuilder",
    )
    game.setCurrentScene(Scenes.mainScene)
    game.run()
