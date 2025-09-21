from REMOLib import *
from REMOLib.particles import ParticleEmitter

import time


class mainScene(Scene):
    def initOnce(self):
        self._last_time = time.time()

        panel_rect = pygame.Rect(40, 40, 440, 170)
        self.info_panel = rectObj(panel_rect, radius=12, edge=2, color=Cs.black, alpha=160)

        self.title = textObj("22. Particle Showcase", pos=(60, 60), size=36, color=Cs.white)
        self.description = textObj(
            "파티클 방출기를 활용한 3가지 효과를 확인해보세요.",
            pos=(60, 100),
            size=22,
            color=Cs.light(Cs.gray),
        )
        self.help_lines = [
            textObj("- 마우스를 움직이면 빛나는 잔상을 남깁니다.", pos=(60, 140), size=20, color=Cs.white),
            textObj("- 좌클릭: 폭발 파티클", pos=(60, 170), size=20, color=Cs.white),
            textObj("- 우클릭: 연기 파티클", pos=(60, 200), size=20, color=Cs.white),
        ]

        self.trail_emitter = ParticleEmitter(RPoint(600, 400), max_particles=240)
        self.trail_emitter.set_defaults(
            speed_range=(120.0, 220.0),
            direction_range=(200.0, 340.0),
            lifetime_range=(0.25, 0.45),
            size_range=(4.0, 8.0),
            color_range=((220, 255), (180, 240), (120, 200)),
            alpha_range=(140, 255),
            gravity=420.0,
            position_jitter=((-12.0, 12.0), (-12.0, 12.0)),
        )

        self.explosion_emitter = ParticleEmitter(RPoint(0, 0), max_particles=320)
        self.smoke_emitter = ParticleEmitter(RPoint(0, 0), max_particles=260)

    def update(self):


        mouse_pos = Rs.mousePos()

        self.trail_emitter.emit(5, position=mouse_pos)

        if Rs.userJustLeftClicked():
            self.explosion_emitter.emit(
                90,
                position=mouse_pos,
                speed_range=(180.0, 360.0),
                direction_range=(0.0, 360.0),
                lifetime_range=(0.6, 1.0),
                size_range=(10.0, 22.0),
                color_range=((220, 255), (120, 200), (40, 120)),
                alpha_range=(200, 255),
                gravity=420.0,
                position_jitter=((-12.0, 12.0), (-12.0, 12.0)),
            )

        if Rs.userJustRightClicked():
            self.smoke_emitter.emit(
                55,
                position=mouse_pos,
                velocity_range=((-40.0, 40.0), (-120.0, -40.0)),
                lifetime_range=(1.1, 1.6),
                size_range=(18.0, 30.0),
                color_range=((110, 160), (110, 160), (110, 160)),
                alpha_range=(70, 140),
                gravity=-60.0,
                fade=True,
                shrink=False,
                position_jitter=((-20.0, 20.0), (-10.0, 10.0)),
            )

        self.trail_emitter.update()
        self.explosion_emitter.update()
        self.smoke_emitter.update()

    def draw(self):
        Rs.fillScreen(Cs.black)

        self.info_panel.draw()
        self.title.draw()
        self.description.draw()
        for line in self.help_lines:
            line.draw()

        self.smoke_emitter.draw()
        self.explosion_emitter.draw()
        self.trail_emitter.draw()


class Scenes:
    mainScene = mainScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="35. Particle Showcase",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
