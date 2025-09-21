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

        self.trail_emitter = ParticleEmitter(
            RPoint(600, 400),
            max_particles=240,
            defaults=particleDefaultPreset.magic_glitter(),
        )

        self.explosion_emitter = ParticleEmitter(
            RPoint(0, 0),
            max_particles=320,
            defaults=particleDefaultPreset.explosion_fireball(),
        )
        self.smoke_emitter = ParticleEmitter(
            RPoint(0, 0),
            max_particles=260,
            defaults=particleDefaultPreset.heavy_smoke(),
        )

    def update(self):


        mouse_pos = Rs.mousePos()

        self.trail_emitter.emit(5, position=mouse_pos)

        if Rs.userJustLeftClicked():
            self.explosion_emitter.emit(90, position=mouse_pos)

        if Rs.userJustRightClicked():
            self.smoke_emitter.emit(55, position=mouse_pos)

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
