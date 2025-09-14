"""카드 업/다운 인디 게임 씬 구현

REMO 엔진(REMOLib)을 사용해 간단한 Higher/Lower 카드 게임을 구성합니다.
- 앵커 기반 포지셔닝으로 스와이프 누적 오프셋을 방지
- 버튼 UI와 HUD 연결, 라운드 준비/공개/프로모션 흐름
"""

from REMOLib import *
import random


class CardGameScene(Scene):
    """Higher/Lower 카드 게임용 씬

    핵심 개념
    - anchor_current/anchor_next: 각 라운드 시작 시 카드들의 기준(center) 위치
    - swipe_offset: 현재 카드를 왼쪽으로 보내는 스와이프 거리 벡터
    - 라운드 진행: 준비(prepare) -> 공개(reveal) -> 전환(after_reveal)
    """
    def initOnce(self):
        """씬 최초 1회 초기화

        화면 배경, 제목, HUD, 카드 영역/오브젝트, 버튼을 생성하고
        기준 앵커를 기록한 후 첫 라운드를 준비합니다.
        """
        self.bg = rectObj(pygame.Rect(0, 0, Rs.screen_size[0], Rs.screen_size[1]), color=Cs.black)
        self.bg.alpha = 255

        title = textObj("HIGHER or LOWER", pos=RPoint(0, 30), size=60, color=Cs.tiffanyBlue)
        title.centerx = Rs.screen_size[0] // 2
        title.setParent(self.bg)

        self.score = 0
        self.lives = 3
        self.round = 0

        # 점수 및 목숨을 보여주는 간단한 HUD 레이아웃
        self.hud = layoutObj(pos=RPoint(0, 0), isVertical=True, spacing=60)
        self.hud.setParent(self.bg, depth=1)
        self.scoreText = textObj(f"SCORE: {self.score}", size=40, color=Cs.white)
        self.lifeText = textObj(f"LIVES: {self.lives}", size=40, color=Cs.white)
        self.hud.setParent(self.bg)
        self.scoreText.setParent(self.hud)
        self.lifeText.setParent(self.hud)
        self.hud.centerx = Rs.screen_size[0] // 2 + 300
        self.hud.y = 240

        # 카드 영역: 현재/다음 카드가 놓일 컨테이너
        card_w, card_h = 260, 360
        self.cardArea = graphicObj(pygame.Rect(0, 0, card_w * 3, card_h))
        self.cardArea.center = RPoint(Rs.screen_size[0] // 2, Rs.screen_size[1] // 2 - 40)
        self.cardArea.setParent(self.bg)

        # 현재 카드
        self.currentCard = rectObj(pygame.Rect(0, 0, card_w, card_h), color=Cs.white, radius=18)
        self.currentCard.setParent(self.cardArea)
        self.currentCard.pos = RPoint(0, 0)
        self.currentText = textObj("", size=120, color=Cs.black)
        self.currentText.setParent(self.currentCard)
        self.currentText.center = self.currentCard.offsetRect.center

        # 다음 카드 (초기에는 뒷면 상태)
        self.nextCard = rectObj(pygame.Rect(0, 0, card_w, card_h), color=Cs.dark(Cs.grey), radius=18)
        self.nextCard.setParent(self.cardArea)
        self.nextCard.pos = RPoint(card_w + 60, 0)
        self.nextText = textObj("?", size=140, color=Cs.white)
        self.nextText.setParent(self.nextCard)
        self.nextText.center = self.nextCard.offsetRect.center

        # 고정 앵커(라운드 누적 오프셋 방지):
        # 각 카드의 기준 center를 저장해, 라운드 전환 시 항상 이 위치로 복원합니다.
        self.anchor_current = self.currentCard.center
        self.anchor_next = self.nextCard.center
        self.swipe_offset = RPoint(-200, 0)

        # 컨트롤 버튼: UP/DOWN 추측과 RESTART
        self.buttons = buttonLayout(["UP", "DOWN", "RESTART"], pos=RPoint(0, 0), isVertical=False,
                                    spacing=30, buttonSize=(220, 70), buttonAlpha=255)
        self.buttons.setParent(self.bg)
        self.buttons.centerx = Rs.screen_size[0] // 2
        self.buttons.y = self.cardArea.geometry.bottom + 60

        self.buttons.UP.connect(lambda: self._guess(True))
        self.buttons.DOWN.connect(lambda: self._guess(False))
        self.buttons.RESTART.connect(self._restart)

        self._prepare_round(first=True)
        return

    def init(self):
        """씬 재진입 시 호출 (이번 게임에서는 별도 처리 없음)"""
        return

    def _restart(self):
        """게임 상태 초기화 후 첫 라운드로 되돌립니다."""
        self.score = 0
        self.lives = 3
        self.round = 0
        self._update_hud()
        self._prepare_round(first=True)

    def _value_to_label(self, v: int) -> str:
        """카드 숫자(1~13)를 A/J/Q/K 라벨로 변환"""
        if v == 1:
            return "A"
        if v == 11:
            return "J"
        if v == 12:
            return "Q"
        if v == 13:
            return "K"
        return str(v)

    def _update_hud(self):
        """HUD 텍스트를 현재 점수/목숨으로 갱신"""
        self.scoreText.text = f"SCORE: {self.score}"
        self.lifeText.text = f"LIVES: {self.lives}"

    def _prepare_round(self, *, first=False):
        """다음 라운드를 준비

        - 현재/다음 카드 값을 뽑고(동일 값 회피),
        - 카드 두 장을 앵커 위치로 되돌린 뒤 뒷면/앞면 상태를 초기화
        - 살짝 튀어나오는(easeout) 연출로 피드백
        """
        self.round += 1
        if first:
            self.cur_val = random.randint(1, 13)
        self.nxt_val = random.randint(1, 13)
        while self.nxt_val == self.cur_val:
            self.nxt_val = random.randint(1, 13)

        # 카드 리셋 애니메이션
        # 위치/알파를 앵커로 초기화
        self.currentCard.center = self.anchor_current
        self.currentCard.alpha = 255
        self.nextCard.center = self.anchor_next
        self.nextCard.alpha = 255
        self.nextCard.color = Cs.dark(Cs.grey)
        self.nextText.color = Cs.white
        self.nextText.text = "?"
        self.currentText.text = self._value_to_label(self.cur_val)
        self.currentText.center = self.currentCard.offsetRect.center
        self.nextText.center = self.nextCard.offsetRect.center

        # 살짝 튀어나오는 효과
        for obj in [self.currentCard, self.nextCard]:
            obj.scale = 1.0
            obj.easeout(["scale"], [1.06], steps=12, revert=True)

    def _reveal_next(self):
        """다음 카드 공개 연출

        - 짧은 지연 후 색상과 텍스트를 교체(뒤집기 느낌)
        - 살짝 이동/페이드인으로 피드백 제공
        """
        # 뒤집힘 효과 (색상과 텍스트 교체, 슬라이드)
        def flip():
            self.nextCard.color = Cs.white
            self.nextText.color = Cs.black
            self.nextText.text = self._value_to_label(self.nxt_val)
        # 살짝 이동하며 밝아짐
        start = self.nextCard.center
        self.nextCard.alpha = 0
        self.nextCard.easeout(["alpha", "center"], [255, start + RPoint(10, 0)], steps=16, on_update=lambda: None)
        Rs.future(flip, 120)

    def _after_reveal(self):
        """공개 이후 전환 처리

        - 현재 카드를 왼쪽으로 스와이프(사라지듯), 다음 카드를 현재 위치로 이동
        - promote에서 오브젝트/텍스트를 스왑하고 앵커로 복귀해 누적 오프셋 방지
        """
        # 다음 라운드로 넘기며 현재 카드를 좌측으로 스와이프, 다음 카드는 현재 자리로 고정 기준 사용
        def promote():
            self.cur_val = self.nxt_val
            # 스왑하여 next가 current가 되도록 정리
            self.currentCard, self.nextCard = self.nextCard, self.currentCard
            self.currentText, self.nextText = self.nextText, self.currentText
            # 위치를 앵커로 복원
            self.currentCard.center = self.anchor_current
            self.nextCard.center = self.anchor_next
            self.currentText.center = self.currentCard.offsetRect.center
            self.nextText.center = self.nextCard.offsetRect.center
            self._prepare_round()

        # 스와이프 애니메이션 (기준: 앵커)
        self.currentCard.easeout(["center", "alpha"], [self.anchor_current + self.swipe_offset, 0], steps=16)
        self.nextCard.easeout(["center"], [self.anchor_current], steps=18, callback=promote)

    def _guess(self, higher: bool):
        """플레이어 입력 처리

        - higher=True면 다음 카드가 더 큰지, False면 더 작은지를 추측
        - 공개 후 결과에 따라 점수/목숨 갱신 및 다음 단계 예약
        """
        # 중복 입력 방지
        if interpolateManager.check_on_interpolation(self.nextCard):
            return

        self._reveal_next()
        correct = (self.nxt_val > self.cur_val) if higher else (self.nxt_val < self.cur_val)

        if correct:
            self.score += 1
            self._flash(self.nextCard, Cs.tiffanyBlue)
            self._update_hud()
            Rs.future(self._after_reveal, 350)
        else:
            self.lives -= 1
            self._flash(self.nextCard, Cs.red)
            self._update_hud()
            if self.lives <= 0:
                Rs.future(self._game_over, 350)
            else:
                Rs.future(self._after_reveal, 350)

    def _flash(self, obj: graphicObj, color):
        """정답/오답 피드백용 잠깐의 컬러 오버레이 연출"""
        # 잠깐 색상 덮기 효과
        flash = Rs.copy(obj)
        flash.graphic.fill((0, 0, 0, 0))
        overlay = rectObj(obj.offsetRect, color=color, radius=18)
        overlay.alpha = 80
        overlay.setParent(flash)
        flash.pos = obj.geometryPos
        Rs.fadeAnimation(flash, time=18, alpha=120)

    def _game_over(self):
        """게임 오버 다이얼로그 생성 및 버튼 연결"""
        dlg = dialogObj(pygame.Rect(0, 0, 600, 380), title="Game Over", content=f"Final Score: {self.score}",
                        buttons=["Restart", "Exit"], color=Cs.black, textColor=Cs.white)
        dlg.center = RPoint(Rs.screen_size[0] // 2, Rs.screen_size[1] // 2)
        dlg.show()
        dlg["Restart"].connect(lambda: (dlg.hide(), self._restart()))
        dlg["Exit"].connect(lambda: REMOGame.exit())

    def update(self):
        """매 프레임 호출되는 업데이트 루프 (버튼 상호작용 등)"""
        # 버튼 hover 등 업데이트
        self.buttons.update()
        return

    def draw(self):
        """씬 드로우 루프: 배경/카드/버튼을 그립니다."""
        self.bg.draw()
        return


class Scenes:
    CardGame = CardGameScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1280, 720), screen_size=(1280, 720), fullscreen=False, caption="Card Up/Down")
    window.setCurrentScene(Scenes.CardGame)
    window.run()


