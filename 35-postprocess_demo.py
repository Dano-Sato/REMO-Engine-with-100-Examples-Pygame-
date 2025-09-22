import math
import pygame

from REMOLib.core import *


class PostProcessScene(Scene):
    def initOnce(self):
        self.background = rectObj(pygame.Rect(0, 0, 1920, 1080), color=(12, 9, 20), radius=0)
        self.background.alpha = 255

        palette = [Cs.cyan, Cs.purple, Cs.orange, Cs.tiffanyBlue]
        self.neon_blocks: list[rectObj] = []
        start_x = 560
        for i, color in enumerate(palette):
            block = rectObj(pygame.Rect(start_x + i * 220, 360, 200, 280), color=color, radius=60, edge=6)
            block.alpha = 200
            block.base_color = color
            self.neon_blocks.append(block)

        self.caption = textObj("Post Effects", pos=(680, 180), size=82, color=Cs.white)
        self.caption.center = RPoint(960, 240)
        self.captionShadow = textObj("Post Effects", pos=(690, 190), size=82, color=Cs.black)
        self.captionShadow.center = RPoint(970, 250)

        self.subtitle = textObj("Bloom + CRT + Color Grade", pos=(0, 0), size=48, color=Cs.light(Cs.cyan))
        self.subtitle.center = RPoint(960, 360)

        self.t = 0.0

    def update(self):
        self.t = pygame.time.get_ticks() / 1000.0
        for idx, block in enumerate(self.neon_blocks):
            wave = math.sin(self.t * 1.6 + idx)
            block.alpha = int(170 + 60 * (wave * 0.5 + 0.5))
            block.color = Cs.apply(block.base_color, 0.9 + 0.1 * (wave * 0.5 + 0.5))

        glow = 0.4 + 0.2 * math.sin(self.t * 1.2)
        self.caption.color = Cs.apply(Cs.white, 0.9 + glow * 0.2)

    def draw(self):
        Rs.fillScreen((8, 6, 14))
        self.background.draw()
        for block in self.neon_blocks:
            block.draw()
        self.captionShadow.draw()
        self.caption.draw()
        self.subtitle.draw()


class Scenes:
    postprocess = PostProcessScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1280, 720), screen_size=(1280, 720), fullscreen=False, caption="35. Post-process demo")
    Rs.postprocess.use(
        Rs.postprocess.bloom(intensity=1.35, bloomThreshold=0.55, bloomRadius=1.6),
        Rs.postprocess.crt(crtVignette=0.35, crtCurvature=0.08),
        Rs.postprocess.color_grade(colorExposure=1.05, colorSaturation=1.18)
    )
    window.setCurrentScene(Scenes.postprocess)
    window.run()
