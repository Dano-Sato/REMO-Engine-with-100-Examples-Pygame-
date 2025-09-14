from REMOLib.core import *
import random
import math
import pygame


class Card:
    def __init__(self, name: str, cost: int, *, damage: int = 0, block: int = 0, description: str = ""):
        """카드 객체를 초기화한다.

        - name: 카드 이름
        - cost: 사용 에너지 비용
        - damage: 공격 피해량(옵션)
        - block: 획득 방어도(옵션)
        - description: 카드 설명(미지정 시 자동 생성)
        """
        self.name = name
        self.cost = cost
        self.damage = damage
        self.block = block
        self.description = description if description else self._auto_desc()

    def _auto_desc(self) -> str:
        """damage/block 값을 기반으로 간단한 설명 문자열을 생성한다."""
        parts = []
        if self.damage:
            parts.append(f"{self.damage} 피해")
        if self.block:
            parts.append(f"{self.block} 방어")
        if not parts:
            return "효과 없음"
        return ", ".join(parts)


class PlayerState:
    def __init__(self):
        """플레이어의 현재 상태(체력/방어/에너지)를 보관한다."""
        self.max_hp = 40
        self.hp = 40
        self.block = 0
        self.energy = 3


class EnemyState:
    def __init__(self, level: int = 1):
        """적 상태를 초기화한다.

        - level: 적 난이도 레벨(체력/의도 수치에 영향)
        """
        self.level = level
        self.max_hp = 28 + 4 * level
        self.hp = self.max_hp
        self.block = 0
        self.intent = ("attack", 6 + level)  # (type, value)

    def roll_intent(self):
        """다음 턴 적의 의도를 무작위로 결정한다(공격 70%, 방어 30%)."""
        # 간단한 의도: 70% 공격, 30% 방어
        if random.random() < 0.7:
            self.intent = ("attack", 6 + self.level)
        else:
            self.intent = ("block", 5 + self.level // 2)


class GameScene(Scene):
    HAND_SIZE = 5

    def initOnce(self):
        """씬 최초 1회 초기화: 상태/덱/UI 구성 후 전투를 시작한다."""
        self.ui_initiated = False
        self.level = 1
        self.player = PlayerState()
        self.enemy = EnemyState(self.level)

        # 덱 구성
        self.master_deck: list[Card] = (
            [Card("Strike", 1, damage=6) for _ in range(5)]
            + [Card("Defend", 1, block=5) for _ in range(5)]
        )
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []

        # UI 객체
        self.header_layout = layoutObj(pos=RPoint(40, 30), isVertical=True, spacing=40)
        self.player_text = textObj("", size=28, color=Cs.white)
        self.enemy_text = textObj("", size=28, color=Cs.white)
        self.intent_text = textObj("", size=26, color=Cs.tiffanyBlue)
        self.player_text.setParent(self.header_layout)
        self.enemy_text.setParent(self.header_layout)
        self.intent_text.setParent(self.header_layout)

        self.end_turn_btn = textButton("턴 종료", pygame.Rect(0, 0, 180, 55), color=Cs.tiffanyBlue, textColor=Cs.white)
        self.end_turn_btn.pos = RPoint(960, 30)
        self.end_turn_btn.connect(self.end_turn)

        # 손패 레이아웃
        self.hand_layout = layoutObj(pos=RPoint(60, 600), isVertical=False, spacing=20)

        # 시작
        self._start_combat(reset_hp=False)
        self.ui_initiated = True

    def init(self):
        # 매 씬 진입 시 호출
        """씬 진입 시마다 호출되는 훅. 현재는 추가 동작 없음."""
        return

    # ====== Game Flow ======
    def _reshuffle_discard_into_draw(self):
        """드로우 더미가 비었을 때, 버림 더미를 섞어 드로우 더미로 옮긴다."""
        if not self.draw_pile and self.discard_pile:
            random.shuffle(self.discard_pile)
            self.draw_pile = self.discard_pile
            self.discard_pile = []

    def _draw_cards(self, n: int):
        """카드를 n장 뽑아 손패에 추가한다. 드로우 더미가 비면 자동 보충한다."""
        for _ in range(n):
            if not self.draw_pile:
                self._reshuffle_discard_into_draw()
            if not self.draw_pile:
                return
            self.hand.append(self.draw_pile.pop())

    def _start_turn(self):
        """플레이어 턴 시작: 에너지/방어 갱신, 드로우, 적 의도 갱신 및 UI 갱신."""
        self.player.energy = 3
        self.player.block = 0
        self._draw_cards(GameScene.HAND_SIZE - len(self.hand))
        self.enemy.roll_intent()
        self._refresh_ui()

    def _start_combat(self, reset_hp: bool = False):
        """전투를 시작한다. 필요 시 플레이어 체력을 초기화하고 덱을 셔플한다."""
        if reset_hp:
            self.player.hp = self.player.max_hp
        self.player.block = 0
        self.enemy = EnemyState(self.level)
        # 새 전투: 덱 섞기
        self.draw_pile = self.master_deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile.clear()
        self.hand.clear()
        self._start_turn()

    def _refresh_ui(self):
        """상단 텍스트와 손패 버튼 등 UI 요소를 현재 상태로 갱신한다."""
        # 상단 텍스트
        self.player_text.text = f"플레이어 HP {self.player.hp}/{self.player.max_hp}  방어 {self.player.block}  에너지 {self.player.energy}"
        self.enemy_text.text = f"적 HP {self.enemy.hp}/{self.enemy.max_hp}  방어 {self.enemy.block}"
        i_type, i_val = self.enemy.intent
        intent_kor = "공격" if i_type == "attack" else "방어"
        self.intent_text.text = f"적 의도: {intent_kor} {i_val}"
        self.header_layout.adjustLayout()

        # 손패 버튼 재구성
        self._rebuild_hand_buttons()

    def _rebuild_hand_buttons(self):
        """현재 손패를 기반으로 카드 버튼 UI를 다시 만든다."""
        # 기존 손패 UI 제거
        self.hand_layout.clearChilds(0)

        for idx, card in enumerate(self.hand):
            title = f"{card.name} ({card.cost})"
            desc = card.description
            btn = textButton(title, pygame.Rect(0, 0, 190, 110), color=Cs.slateblue, textColor=Cs.white)
            # 카드 설명 텍스트(작게)
            sub = textObj(desc, size=20, color=Cs.white)
            sub.setParent(btn, depth=1)
            sub.centerx = btn.offsetRect.centerx
            sub.y = btn.offsetRect.centery+30

            def make_play(i):
                def _():
                    self.play_card(i)
                return _
            btn.connect(make_play(idx))
            btn.setParent(self.hand_layout)

        self.hand_layout.adjustLayout()

    # ====== Actions ======
    def play_card(self, hand_index: int):
        """손패의 인덱스에 해당하는 카드를 사용하고 효과를 적용한다.

        - hand_index: 손패 내 카드 인덱스(범위 이탈 시 무시)
        """
        if hand_index < 0 or hand_index >= len(self.hand):
            return
        card = self.hand[hand_index]
        if self.player.energy < card.cost:
            return

        self.player.energy -= card.cost
        # 효과 적용
        if card.damage:
            dmg = max(0, card.damage - self.enemy.block)
            self.enemy.block = max(0, self.enemy.block - card.damage)
            self.enemy.hp -= dmg
        if card.block:
            self.player.block += card.block

        # 카드 이동 (버림)
        self.discard_pile.append(card)
        del self.hand[hand_index]

        # 즉시 종료 체크
        if self.enemy.hp <= 0:
            self._on_victory()
            return

        self._refresh_ui()

    def end_turn(self):
        """플레이어 턴을 종료하고, 적 행동 처리 후 다음 턴을 준비한다."""
        # 적 행동
        i_type, i_val = self.enemy.intent
        if i_type == "attack":
            incoming = max(0, i_val - self.player.block)
            self.player.block = max(0, self.player.block - i_val)
            self.player.hp -= incoming
        elif i_type == "block":
            self.enemy.block += i_val

        # 패 정리: 손패 버림
        self.discard_pile.extend(self.hand)
        self.hand.clear()

        if self.player.hp <= 0:
            self._on_defeat()
            return

        self._start_turn()

    def _on_victory(self):
        """적 처치 시 보상 지급 및 다음 진행 선택 UI를 연다."""
        # 간단한 보상: 체력 소량 회복, 덱에 카드 1장 추가
        self.player.hp = min(self.player.max_hp, self.player.hp + 5)
        reward = random.choice([Card("Strike+", 1, damage=9), Card("Defend+", 1, block=8), Card("Bash", 2, damage=12)])
        self.master_deck.append(reward)
        # 진행(맵 선택) 다이얼로그 표시
        self._show_progression_dialog()

    def _show_progression_dialog(self):
        """다음 경로(쉬운 전투/정예 전투/휴식) 중 하나를 선택하는 다이얼로그를 표시한다."""
        # 다음 경로 선택: 쉬운 전투 / 정예 전투 / 휴식
        dlg = dialogObj(pygame.Rect(0, 0, 620, 320), title="다음 경로를 선택", content="다음 행선지를 고르세요.", buttons=["쉬운 전투", "정예 전투", "휴식"], color=Cs.black)
        dlg.center = Rs.screenRect().center

        def go_easy():
            Rs.removePopup(dlg)
            self.level += 1
            self._start_combat(reset_hp=False)

        def go_elite():
            Rs.removePopup(dlg)
            self.level += 2
            self._start_combat(reset_hp=False)
            self.enemy.block += 5  # 정예 보정
            self._refresh_ui()

        def rest():
            # 체력 회복(최대 체력의 25%, 최소 6)
            heal = max(6, int(self.player.max_hp * 0.25))
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            Rs.removePopup(dlg)
            self.level += 1
            self._start_combat(reset_hp=False)

        dlg["쉬운 전투"].connect(go_easy)
        dlg["정예 전투"].connect(go_elite)
        dlg["휴식"].connect(rest)
        dlg.show()

    def _on_defeat(self):
        """플레이어 패배 시 재시작/종료 다이얼로그를 표시한다."""
        # 간단한 재시작 다이얼로그
        dlg = dialogObj(pygame.Rect(0, 0, 520, 260), title="패배", content="다시 시도하시겠습니까?", buttons=["다시 시작", "종료"], color=Cs.black)
        dlg.center = Rs.screenRect().center

        def retry():
            Rs.removePopup(dlg)
            self.level = 1
            self.player = PlayerState()
            self.master_deck = (
                [Card("Strike", 1, damage=6) for _ in range(5)]
                + [Card("Defend", 1, block=5) for _ in range(5)]
            )
            self._start_combat(reset_hp=True)

        def quit_game():
            REMOGame.exit()

        dlg["다시 시작"].connect(retry)
        dlg["종료"].connect(quit_game)
        dlg.show()

    def update(self):
        """프레임 단위 업데이트: 버튼/손패 상호작용 상태를 갱신한다."""
        # 버튼/손패 상호작용 업데이트
        self.hand_layout.update()
        self.end_turn_btn.update()
        return

    def draw(self):
        """현재 프레임의 UI와 게임 상태를 화면에 그린다."""
        # 배경
        Rs.fillScreen(Cs.dark(Cs.indigo))
        # 상단 정보
        self.player_text.draw()
        self.enemy_text.draw()
        self.intent_text.draw()
        # 엔드턴 버튼
        self.end_turn_btn.draw()
        # 손패 렌더링
        self.hand_layout.draw()
        return


class Scenes:
    gameScene = GameScene()
# 게임 시작
if __name__ == "__main__":
    game = REMOGame(window_resolution=(1200, 800), screen_size=(1200, 800), 
                   fullscreen=False, caption="default")
    game.setCurrentScene(Scenes.gameScene)
    game.run()
