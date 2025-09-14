from REMOLib.core import *
import random, pygame, math


class DodgeScene(Scene):
    def initOnce(self):
        self.score = 0
        self.best = 0
        self.gameover = False
        self.spawnTimer = RTimer(600)
        self.speed = 6

        # 플레이어
        self.player = rectObj(pygame.Rect(0, 0, 48, 48), color=Cs.tiffanyBlue)
        self.player.center = Rs.screenRect().center

        # 텍스트
        self.txt_score = textObj("점수 0", pos=RPoint(24, 20), size=28, color=Cs.white)
        self.txt_best = textObj("최고 0", pos=RPoint(24, 56), size=22, color=Cs.light(Cs.white))

        # 장애물 컨테이너
        self.enemies: list[rectObj] = []

        # 안내
        self.help = textObj("WASD/화살표 이동", size=22, color=Cs.white)
        self.help.centerx = Rs.screenRect().centerx
        self.help.y = 20

    def init(self):
        return

    def _spawn_enemy(self):
        rect = pygame.Rect(0, 0, random.randint(24, 64), random.randint(24, 64))
        side = random.choice(["top", "bottom", "left", "right"]) 
        enemy = rectObj(rect, color=Cs.crimson)

        # 시작 위치(화면 외곽) 설정
        scr = Rs.screenRect()
        if side == "top":
            enemy.centerx = random.randint(0, scr.width)
            enemy.y = -enemy.height
        elif side == "bottom":
            enemy.centerx = random.randint(0, scr.width)
            enemy.y = scr.height + enemy.height
        elif side == "left":
            enemy.centery = random.randint(0, scr.height)
            enemy.x = -enemy.width
        else:
            enemy.centery = random.randint(0, scr.height)
            enemy.x = scr.width + enemy.width

        # 임의의 내부 목표 지점으로 향하는 속도 벡터 생성
        inside_target = RPoint(random.randint(scr.width//8, scr.width*7//8),
                               random.randint(scr.height//8, scr.height*7//8))
        delta = inside_target - enemy.center
        dist = math.hypot(delta.x, delta.y)
        # 기본 속도(난이도 반영)
        base = 3 + int(self.speed * 0.5)
        base += random.randint(0, 2)
        if dist == 0:
            vx, vy = base, 0
        else:
            vx = int(base * (delta.x / dist))
            vy = int(base * (delta.y / dist))
            if vx == 0 and vy == 0:
                vx = max(1, base)

        enemy._vel = (vx, vy)
        self.enemies.append(enemy)

    def _despawn_enemy(self, enemy: rectObj):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def _reset(self):
        self.best = max(self.best, self.score)
        self.score = 0
        self.speed = 6
        self.gameover = False
        self.enemies.clear()
        self.player.center = Rs.screenRect().center
        if hasattr(self, "dlg"):
            del self.dlg

    def _handle_input(self):
        vel = RPoint(0, 0)
        if Rs.userPressing(pygame.K_LEFT) or Rs.userPressing(pygame.K_a):
            vel += RPoint(-1, 0)
        if Rs.userPressing(pygame.K_RIGHT) or Rs.userPressing(pygame.K_d):
            vel += RPoint(1, 0)
        if Rs.userPressing(pygame.K_UP) or Rs.userPressing(pygame.K_w):
            vel += RPoint(0, -1)
        if Rs.userPressing(pygame.K_DOWN) or Rs.userPressing(pygame.K_s):
            vel += RPoint(0, 1)

        if vel != RPoint(0, 0):
            step = int(7 + self.speed)
            self.player.pos = self.player.pos + vel * step
            # 화면 내 클램프
            r = Rs.screenRect()
            pr = self.player.rect
            self.player.x = max(0, min(r.w - pr.w, self.player.x))
            self.player.y = max(0, min(r.h - pr.h, self.player.y))

    def update(self):

        if self.gameover:
            return
        self._handle_input()

        # 스폰/난이도
        if self.spawnTimer.isOver():
            self._spawn_enemy()
            self.spawnTimer.reset()
            self.speed = min(18, self.speed + 0.05)
            # 점수는 스폰 시가 아니라 벽 반사 시에만 증가

        # 이동/반사/충돌 체크
        scr = Rs.screenRect()
        for e in list(self.enemies):
            if hasattr(e, "_vel"):
                vx, vy = e._vel
                e.pos = e.pos + RPoint(vx, vy)
                bounced = False
                g = e.rect
                # X 경계 체크
                if g.left < 0:
                    e.x = 0
                    vx = -vx
                    bounced = True
                elif g.right > scr.width:
                    e.x = scr.width - g.w
                    vx = -vx
                    bounced = True
                # Y 경계 체크
                g = e.rect
                if g.top < 0:
                    e.y = 0
                    vy = -vy
                    bounced = True
                elif g.bottom > scr.height:
                    e.y = scr.height - g.h
                    vy = -vy
                    bounced = True
                if bounced:
                    e._vel = (vx, vy)
                    self.score += 1
                else:
                    e._vel = (vx, vy)
            # 플레이어와 충돌
            if e.geometry.colliderect(self.player.geometry):
                self.gameover = True
                self.best = max(self.best, self.score)
                break

        # UI
        self.txt_score.text = f"점수 {self.score}"
        self.txt_best.text = f"최고 {self.best}"

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.indigo))
        self.txt_score.draw()
        self.txt_best.draw()
        self.help.draw()

        # 장애물/플레이어 그리기
        for e in self.enemies:
            e.draw()
        self.player.draw()

        if self.gameover:
            if not hasattr(self,"dlg"):
                self.dlg = dialogObj(pygame.Rect(0, 0, 520, 260), title="게임 오버", content=f"점수 {self.score}", buttons=["리셋", "종료"], color=Cs.black)
                self.dlg.center = Rs.screenRect().center
                def quit_game():
                    REMOGame.exit()
                self.dlg["리셋"].connect(lambda: (self.dlg.hide(),self._reset()))
                self.dlg["종료"].connect(quit_game)
            self.dlg.show()


class Scenes:
    game = DodgeScene()


if __name__ == "__main__":
    game = REMOGame(window_resolution=(1024, 768), screen_size=(1024, 768), fullscreen=False, caption="Dodge")
    game.setCurrentScene(Scenes.game)
    game.run()


