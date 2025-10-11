from __future__ import annotations

import math
import pygame

from REMOLib import *
from REMOLib.graphic_effects import (
    GraphicEffect,
    FloatingEffect,
    SwayEffect,
    PulseAlphaEffect,
    OrbitPulseEffect,
)


class Obj:
    """Container for game-wide singletons."""

    pass


class mainScene(Scene):
    def initOnce(self):
        screen_rect = Rs.screen.get_rect()
        center = RPoint(screen_rect.center)

        self.title = textObj("Graphic effects for graphicObj", size=52, color=Cs.white)
        self.title.centerx = center.x
        self.title.y = 60

        self.float_text = textObj("Floating text", size=40, color=Cs.tiffanyBlue)
        self.float_text.center = RPoint((center.x, center.y - 140))

        self.card = imageObj(Icons.CARD, scale=0.85)
        self.card.center = RPoint((center.x, center.y + 20))

        self.coin = imageObj(Icons.COIN, scale=0.55)
        self.coin.center = RPoint((center.x + 110, center.y + 20))

        self.pulse_panel = rectObj(pygame.Rect(0, 0, 520, 110), color=Cs.darkslateblue)
        self.pulse_panel.center = RPoint((center.x, center.y + 210))
        self.pulse_label = textObj(
            "Alpha pulsing effect keeps attention",
            size=30,
            color=Cs.white,
        )
        self.pulse_label.center = self.pulse_panel.center

        self.instructions = textObj(
            "Left click: move floating text | Right click: move card | R: reset | SPACE: pause",
            size=24,
            color=Cs.white,
        )
        self.instructions.centerx = center.x
        self.instructions.y = screen_rect.h - 80

        self.status = textObj("Status: Running", size=24, color=Cs.lightgreen)
        self.status.centerx = center.x
        self.status.y = screen_rect.h - 50

        self.effect_handles: list[GraphicEffect] = []
        self.float_effect = self.float_text.apply_effect(FloatingEffect, amplitude=28, period=2600)
        self.sway_effect = self.card.apply_effect(
            SwayEffect, amplitude=36, max_angle=7, period=2100, phase=math.pi / 2
        )
        self.panel_effect = self.pulse_panel.apply_effect(
            PulseAlphaEffect, min_alpha=90, max_alpha=220, period=2000
        )
        self.label_effect = self.pulse_label.apply_effect(
            PulseAlphaEffect, min_alpha=180, max_alpha=255, period=2000, phase=math.pi
        )
        self.coin_effect = self.coin.apply_effect(
            OrbitPulseEffect,
            radius=110,
            angular_speed=90,
            radial_amplitude=18,
            radial_period=1800,
            rotate_with_motion=True,
            anchor_getter=lambda: self.card.center.toTuple(),
        )

        self.effect_handles.extend(
            [
                self.float_effect,
                self.sway_effect,
                self.panel_effect,
                self.label_effect,
                self.coin_effect,
            ]
        )

        self._default_positions = {
            "float": RPoint(self.float_text.center.toTuple()),
            "card": RPoint(self.card.center.toTuple()),
            "panel": RPoint(self.pulse_panel.center.toTuple()),
        }
        self.paused = False

    def _set_paused(self, paused: bool) -> None:
        for effect in self.effect_handles:
            effect.set_enabled(not paused)

    def _snap_coin_to_orbit(self) -> None:
        anchor = self.card.center.toTuple()
        self.coin.center = RPoint((int(anchor[0] + self.coin_effect.radius), int(anchor[1])))

    def _reset_positions(self) -> None:
        self.float_text.center = RPoint(self._default_positions["float"].toTuple())
        self.card.center = RPoint(self._default_positions["card"].toTuple())
        self.card.angle = 0
        self.pulse_panel.center = RPoint(self._default_positions["panel"].toTuple())
        self.pulse_label.center = self.pulse_panel.center
        self._snap_coin_to_orbit()
        for effect in self.effect_handles:
            effect.reset_anchor()

    def init(self):
        return

    def update(self):
        for event in Rs.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    self._set_paused(self.paused)
                if event.key == pygame.K_r:
                    self._reset_positions()

        if Rs.userJustLeftClicked():
            self.float_text.center = Rs.mousePos()
            self.float_effect.reset_anchor()
        if Rs.userJustRightClicked():
            self.card.center = Rs.mousePos()
            self.sway_effect.reset_anchor()
            self.coin_effect.reset_anchor()
            self._snap_coin_to_orbit()

        status_text = "Status: Paused" if self.paused else "Status: Running"
        self.status.text = f"{status_text}"
        self.status.color = Cs.salmon if self.paused else Cs.lightgreen

    def draw(self):
        Rs.fillScreen(Cs.midnightblue)
        self.pulse_panel.draw()
        self.card.draw()
        self.coin.draw()
        self.float_text.draw()
        self.pulse_label.draw()
        self.title.draw()
        self.instructions.draw()
        self.status.draw()


class Scenes:
    mainScene = mainScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="38. Graphic effects showcase",
        flags=pygame.RESIZABLE,
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
