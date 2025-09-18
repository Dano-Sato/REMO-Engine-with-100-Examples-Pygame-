from REMOLib.core import *
import random
import pygame


class Card:
    """전투에 사용되는 카드를 정의한다."""

    def __init__(
        self,
        name: str,
        cost: int,
        *,
        card_type: str = "Attack",
        damage: int = 0,
        block: int = 0,
        draw: int = 0,
        energy: int = 0,
        description: str | None = None,
    ):
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.damage = damage
        self.block = block
        self.draw = draw
        self.energy = energy
        self.description = description or self._generate_description()

    def _generate_description(self) -> str:
        parts: list[str] = []
        if self.damage:
            parts.append(f"{self.damage} 피해")
        if self.block:
            parts.append(f"{self.block} 방어")
        if self.draw:
            parts.append(f"카드 {self.draw}장 드로우")
        if self.energy:
            parts.append(f"에너지 {self.energy} 회복")
        if not parts:
            parts.append("효과 없음")
        return "\n".join(parts)

    @property
    def summary(self) -> str:
        parts: list[str] = []
        if self.damage:
            parts.append(f"공격 {self.damage}")
        if self.block:
            parts.append(f"방어 {self.block}")
        if self.draw:
            parts.append(f"드로우 {self.draw}")
        if self.energy:
            parts.append(f"에너지 +{self.energy}")
        return " · ".join(parts) if parts else "특수 효과"

    @property
    def base_color(self) -> tuple[int, int, int]:
        if self.card_type.lower() == "attack":
            return Cs.dark(Cs.orange)
        if self.card_type.lower() == "skill":
            return Cs.dark(Cs.teal)
        if self.card_type.lower() == "power":
            return Cs.dark(Cs.purple)
        return Cs.dark(Cs.steelblue)

    @property
    def badge_color(self) -> tuple[int, int, int]:
        if self.card_type.lower() == "attack":
            return Cs.dark(Cs.red)
        if self.card_type.lower() == "skill":
            return Cs.dark(Cs.lightseagreen)
        if self.card_type.lower() == "power":
            return Cs.dark(Cs.indigo)
        return Cs.dark(Cs.slateblue)


class PlayerState:
    def __init__(self):
        self.max_hp = 40
        self.hp = 40
        self.block = 0
        self.max_energy = 3
        self.energy = self.max_energy


class EnemyState:
    NAMES = [
        "슬라임 도적",
        "돌갑옷 고블린",
        "혼돈의 마도사",
        "철갑 기사",
        "공허 추적자",
    ]

    def __init__(self, level: int = 1):
        self.level = level
        self.name = random.choice(self.NAMES)
        base_hp = 32 + level * 5
        self.max_hp = base_hp
        self.hp = base_hp
        self.block = 0
        self.intent: tuple[str, int] = ("attack", 6 + level)

    def roll_intent(self) -> None:
        roll = random.random()
        if roll < 0.65:
            self.intent = ("attack", 6 + self.level + random.randint(0, 3))
        elif roll < 0.85:
            self.intent = ("block", 5 + self.level)
        else:
            self.intent = ("buff", 2 + self.level // 2)


class CardWidget(rectObj):
    """카드 데이터를 시각화하고 상호작용을 처리하는 위젯."""

    def __init__(self, card: Card, on_play):
        super().__init__(pygame.Rect(0, 0, 180, 260), color=card.base_color, edge=6)
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

        self.title_text = textObj(card.name, size=26, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 78)

        self.cost_badge = rectObj(pygame.Rect(0, 0, 54, 54), radius=18, edge=3, color=self._badge_base)
        self.cost_badge.setParent(self, depth=1)
        self.cost_badge.x = 0
        self.cost_badge.y = 0

        self.cost_text = textObj(str(card.cost), size=26, color=Cs.white)
        self.cost_text.setParent(self.cost_badge, depth=1)
        self.cost_text.center = self.cost_badge.offsetRect.center

        self.desc_text = longTextObj(card.description, pos=RPoint(0, 0), size=20, color=Cs.white, textWidth=140)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.centerx = self.offsetRect.centerx
        self.desc_text.y = self.title_text.rect.bottom + 10

        self.summary_text = textObj(card.summary, size=20, color=Cs.yellow)
        self.summary_text.setParent(self, depth=1)
        self.summary_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)

        self.set_playable(True)

    def refresh(self, energy: int) -> None:
        self.playable = energy >= self.card.cost
        self.cost_text.text = str(self.card.cost)
        self.title_text.text = self.card.name
        self.desc_text.text = self.card.description
        self.summary_text.text = self.card.summary
        self.type_text.text = self.card.card_type.upper()
        self.set_playable(self.playable)

    def set_playable(self, playable: bool) -> None:
        self.playable = playable
        alpha = 255 if playable else 160
        self.alpha = alpha
        self.type_text.alpha = alpha
        self.title_text.alpha = alpha
        self.desc_text.alpha = alpha
        self.summary_text.alpha = alpha
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


class GameScene(Scene):
    HAND_LIMIT = 5

    def initOnce(self):
        self.level = 1
        self.player = PlayerState()
        self.enemy = EnemyState(self.level)

        self.master_deck: list[Card] = self._make_starter_deck()
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []
        self.hand_widgets: list[CardWidget] = []

        self.info_layout = layoutObj(pos=RPoint(50, 40), isVertical=True, spacing=18)
        self.player_text = textObj("", size=28, color=Cs.white)
        self.enemy_text = textObj("", size=28, color=Cs.white)
        self.intent_text = textObj("", size=26, color=Cs.tiffanyBlue)
        self.deck_text = textObj("", size=24, color=Cs.grey75)
        for t in (self.player_text, self.enemy_text, self.intent_text, self.deck_text):
            t.setParent(self.info_layout)
        self.info_layout.adjustLayout()

        self.log_lines: list[str] = []
        self.log_box = longTextObj("", pos=RPoint(50, 320), size=22, color=Cs.white, textWidth=560)

        self.end_turn_button = textButton(
            "턴 종료",
            pygame.Rect(0, 0, 200, 64),
            color=Cs.tiffanyBlue,
            textColor=Cs.white,
        )
        self.end_turn_button.pos = RPoint(1020, 40)
        self.end_turn_button.connect(self.end_turn)

        self.hand_layout = cardLayout(RPoint(120, 640), spacing=28, maxWidth=1080, isVertical=False)

        self._start_combat(reset_hp=False)

    def init(self):
        return

    def _make_starter_deck(self) -> list[Card]:
        deck = [Card("강타", 1, card_type="Attack", damage=6) for _ in range(5)]
        deck += [Card("수비", 1, card_type="Skill", block=5) for _ in range(5)]
        deck.append(Card("집중", 0, card_type="Skill", draw=2, description="카드 2장 드로우"))
        deck.append(Card("격려", 1, card_type="Power", energy=1, description="이번 턴에 에너지 1 회복"))
        return deck

    def _add_log(self, text: str) -> None:
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-6:]
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

    def _start_turn(self) -> None:
        self.player.energy = self.player.max_energy
        self.player.block = 0
        draw_amount = GameScene.HAND_LIMIT - len(self.hand)
        if draw_amount > 0:
            self._draw_cards(draw_amount)
        self.enemy.roll_intent()
        self._refresh_ui()
        self._add_log("새 턴이 시작되었습니다.")

    def _start_combat(self, *, reset_hp: bool) -> None:
        if reset_hp:
            self.player.hp = self.player.max_hp
        self.player.block = 0
        self.enemy = EnemyState(self.level)
        self.draw_pile = self.master_deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile.clear()
        self.hand.clear()
        self._add_log(f"{self.enemy.name}과(와)의 전투를 시작합니다!")
        self._draw_cards(GameScene.HAND_LIMIT)
        self.enemy.roll_intent()
        self._refresh_ui()

    def _rebuild_hand_widgets(self) -> None:
        self.hand_layout.clearChilds(0)
        self.hand_widgets.clear()

        for card in self.hand:
            widget = CardWidget(card, on_play=lambda c=card: self.play_card(c))
            widget.setParent(self.hand_layout)
            widget.refresh(self.player.energy)
            self.hand_widgets.append(widget)
        self.hand_layout.adjustLayout()

    def _refresh_ui(self) -> None:
        self.player_text.text = (
            f"플레이어 HP {self.player.hp}/{self.player.max_hp}  방어 {self.player.block}  에너지 {self.player.energy}/{self.player.max_energy}"
        )
        self.enemy_text.text = f"{self.enemy.name} HP {self.enemy.hp}/{self.enemy.max_hp}  방어 {self.enemy.block}"
        intent_type, intent_value = self.enemy.intent
        intent_label = {
            "attack": "공격",
            "block": "방어",
            "buff": "강화",
        }.get(intent_type, intent_type)
        self.intent_text.text = f"적 의도: {intent_label} {intent_value}"
        self.deck_text.text = f"드로우 {len(self.draw_pile)}장 · 버림 {len(self.discard_pile)}장"
        self.info_layout.adjustLayout()
        self._rebuild_hand_widgets()

    def play_card(self, card: Card) -> None:
        if card not in self.hand:
            return
        if self.player.energy < card.cost:
            return

        self.player.energy -= card.cost
        self._resolve_card_effect(card)
        self.hand.remove(card)
        self.discard_pile.append(card)

        if self.enemy.hp <= 0:
            self._on_victory()
            return

        self._refresh_ui()

    def _resolve_card_effect(self, card: Card) -> None:
        if card.damage:
            effective_damage = max(0, card.damage - self.enemy.block)
            self.enemy.block = max(0, self.enemy.block - card.damage)
            self.enemy.hp -= effective_damage
            self._add_log(f"{card.name} 사용! {effective_damage} 피해를 주었습니다.")
        if card.block:
            self.player.block += card.block
            self._add_log(f"{card.block}만큼의 방어도를 얻었습니다.")
        if card.draw:
            self._draw_cards(card.draw)
        if card.energy:
            self.player.energy += card.energy
            self._add_log(f"에너지를 {card.energy} 회복했습니다.")

    def end_turn(self) -> None:
        intent, value = self.enemy.intent
        if intent == "attack":
            damage = max(0, value - self.player.block)
            self.player.block = max(0, self.player.block - value)
            self.player.hp -= damage
            self._add_log(f"적이 공격하여 {damage} 피해를 받았습니다.")
        elif intent == "block":
            self.enemy.block += value
            self._add_log(f"적이 {value}의 방어도를 얻었습니다.")
        elif intent == "buff":
            self.enemy.block += value
            self.enemy.hp = min(self.enemy.max_hp, self.enemy.hp + value)
            self._add_log("적이 스스로를 강화했습니다.")

        self.discard_pile.extend(self.hand)
        self.hand.clear()

        if self.player.hp <= 0:
            self._on_defeat()
            return

        self._start_turn()

    def _on_victory(self) -> None:
        self._add_log(f"{self.enemy.name}을(를) 처치했습니다!")
        self.player.hp = min(self.player.max_hp, self.player.hp + 4)
        reward = random.choice(
            [
                Card("강타+", 1, card_type="Attack", damage=9),
                Card("방패 올리기", 1, card_type="Skill", block=9),
                Card("전술", 1, card_type="Skill", draw=1, energy=1, description="카드 1장 드로우 및 에너지 1 회복"),
            ]
        )
        self.master_deck.append(reward)
        self._add_log(f"새 카드 '{reward.name}'를 덱에 추가했습니다.")
        self._show_progress_dialog()

    def _show_progress_dialog(self) -> None:
        dialog = dialogObj(
            pygame.Rect(0, 0, 640, 320),
            title="다음 진행을 선택",
            content="다음 행선지를 고르세요.",
            buttons=["쉬운 전투", "정예 전투", "휴식"],
            color=Cs.black,
        )
        dialog.center = Rs.screenRect().center

        def go_easy():
            Rs.removePopup(dialog)
            self.level += 1
            self._start_combat(reset_hp=False)

        def go_elite():
            Rs.removePopup(dialog)
            self.level += 2
            self.enemy.block += 5
            self._start_combat(reset_hp=False)
            self._add_log("정예 전투에 돌입했습니다. 적의 방어도가 강화됩니다!")

        def rest():
            heal = max(6, int(self.player.max_hp * 0.25))
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            Rs.removePopup(dialog)
            self.level += 1
            self._start_combat(reset_hp=False)
            self._add_log(f"휴식을 취해 체력을 {heal} 회복했습니다.")

        dialog["쉬운 전투"].connect(go_easy)
        dialog["정예 전투"].connect(go_elite)
        dialog["휴식"].connect(rest)
        dialog.show()

    def _on_defeat(self) -> None:
        self._add_log("패배했습니다. 다시 도전하거나 종료할 수 있습니다.")
        dialog = dialogObj(
            pygame.Rect(0, 0, 520, 260),
            title="패배",
            content="다시 시도하시겠습니까?",
            buttons=["다시 시작", "종료"],
            color=Cs.black,
        )
        dialog.center = Rs.screenRect().center

        def retry():
            Rs.removePopup(dialog)
            self.level = 1
            self.player = PlayerState()
            self.master_deck = self._make_starter_deck()
            self._start_combat(reset_hp=True)

        def quit_game():
            REMOGame.exit()

        dialog["다시 시작"].connect(retry)
        dialog["종료"].connect(quit_game)
        dialog.show()

    def update(self):
        self.hand_layout.adjustLayout()
        self.hand_layout.update()
        self.end_turn_button.update()
        return

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.indigo))
        self.info_layout.draw()
        self.log_box.draw()
        self.end_turn_button.draw()
        self.hand_layout.draw()
        return


class Scenes:
    gameScene = GameScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1280, 1000),
        screen_size=(1280, 1000),
        fullscreen=False,
        caption="card roguelike",
    )
    game.setCurrentScene(Scenes.gameScene)
    game.run()
