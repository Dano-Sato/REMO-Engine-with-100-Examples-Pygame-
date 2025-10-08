from __future__ import annotations

import math
import pygame

from REMOLib import *


TAU = getattr(math, "tau", math.pi * 2)


class GraphicEffect:
    """Base class for simple runtime-driven graphicObj effects."""

    def __init__(self, obj: graphicObj):
        self.obj = obj
        self._start_time = pygame.time.get_ticks()

    def update(self, time_ms: int) -> None:
        raise NotImplementedError

    def reset_anchor(self) -> None:
        self._start_time = pygame.time.get_ticks()


class FloatingEffect(GraphicEffect):
    """Makes a graphic object float up and down around an anchor point."""

    def __init__(
        self,
        obj: graphicObj,
        *,
        amplitude: float = 25,
        period: int = 2400,
        phase: float = 0.0,
    ) -> None:
        super().__init__(obj)
        self.amplitude = amplitude
        self.period = period
        self.phase = phase
        self._anchor = pygame.Vector2(obj.center.x, obj.center.y)

    def reset_anchor(self) -> None:
        super().reset_anchor()
        self._anchor = pygame.Vector2(self.obj.center.x, self.obj.center.y)

    def update(self, time_ms: int) -> None:
        elapsed = (time_ms - self._start_time) / self.period
        offset = math.sin(self.phase + elapsed * TAU) * self.amplitude
        center = pygame.Vector2(self._anchor.x, self._anchor.y + offset)
        self.obj.center = RPoint((int(center.x), int(center.y)))


class SwayEffect(GraphicEffect):
    """Applies a subtle horizontal sway and rotation."""

    def __init__(
        self,
        obj: graphicObj,
        *,
        amplitude: float = 35,
        max_angle: float = 6,
        period: int = 2000,
        phase: float = 0.0,
    ) -> None:
        super().__init__(obj)
        self.amplitude = amplitude
        self.max_angle = max_angle
        self.period = period
        self.phase = phase
        self._anchor = pygame.Vector2(obj.center.x, obj.center.y)
        self._base_angle = getattr(obj, "angle", 0)

    def reset_anchor(self) -> None:
        super().reset_anchor()
        self._anchor = pygame.Vector2(self.obj.center.x, self.obj.center.y)
        self._base_angle = getattr(self.obj, "angle", 0)

    def update(self, time_ms: int) -> None:
        elapsed = (time_ms - self._start_time) / self.period
        wave = math.sin(self.phase + elapsed * TAU)
        center = pygame.Vector2(self._anchor.x + wave * self.amplitude, self._anchor.y)
        self.obj.center = RPoint((int(center.x), int(center.y)))
        if hasattr(self.obj, "angle"):
            self.obj.angle = self._base_angle + wave * self.max_angle


class PulseAlphaEffect(GraphicEffect):
    """Animates the alpha value to create a breathing glow."""

    def __init__(
        self,
        obj: graphicObj,
        *,
        min_alpha: int = 120,
        max_alpha: int = 255,
        period: int = 1600,
        phase: float = 0.0,
    ) -> None:
        super().__init__(obj)
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.period = period
        self.phase = phase

    def update(self, time_ms: int) -> None:
        elapsed = (time_ms - self._start_time) / self.period
        wave = (math.sin(self.phase + elapsed * TAU) + 1) * 0.5
        alpha = int(round(self.min_alpha + (self.max_alpha - self.min_alpha) * wave))
        self.obj.alpha = max(0, min(255, alpha))


class GraphicEffectController:
    """Simple container that updates multiple effects in one call."""

    def __init__(self) -> None:
        self._effects: list[GraphicEffect] = []

    def add(self, effect: GraphicEffect) -> GraphicEffect:
        self._effects.append(effect)
        return effect

    def update(self, time_ms: int) -> None:
        for effect in self._effects:
            effect.update(time_ms)

    def reset_all(self) -> None:
        for effect in self._effects:
            effect.reset_anchor()


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

        self.effects = GraphicEffectController()
        self.float_effect = self.effects.add(FloatingEffect(self.float_text, amplitude=28, period=2600))
        self.sway_effect = self.effects.add(SwayEffect(self.card, amplitude=36, max_angle=7, period=2100, phase=math.pi / 2))
        self.panel_effect = self.effects.add(PulseAlphaEffect(self.pulse_panel, min_alpha=90, max_alpha=220, period=2000))
        self.label_effect = self.effects.add(PulseAlphaEffect(self.pulse_label, min_alpha=180, max_alpha=255, period=2000, phase=math.pi))

        self._default_positions = {
            "float": RPoint(self.float_text.center.toTuple()),
            "card": RPoint(self.card.center.toTuple()),
            "panel": RPoint(self.pulse_panel.center.toTuple()),
        }
        self.paused = False

    def _reset_positions(self) -> None:
        self.float_text.center = RPoint(self._default_positions["float"].toTuple())
        self.card.center = RPoint(self._default_positions["card"].toTuple())
        self.card.angle = 0
        self.pulse_panel.center = RPoint(self._default_positions["panel"].toTuple())
        self.pulse_label.center = self.pulse_panel.center
        self.effects.reset_all()

    def init(self):
        return

    def update(self):
        for event in Rs.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                if event.key == pygame.K_r:
                    self._reset_positions()

        if Rs.userJustLeftClicked():
            self.float_text.center = Rs.mousePos()
            self.float_effect.reset_anchor()
        if Rs.userJustRightClicked():
            self.card.center = Rs.mousePos()
            self.sway_effect.reset_anchor()

        if not self.paused:
            self.effects.update(pygame.time.get_ticks())

        status_text = "Status: Paused" if self.paused else "Status: Running"
        self.status.text = f"{status_text}"
        self.status.color = Cs.salmon if self.paused else Cs.lightgreen

    def draw(self):
        Rs.fillScreen(Cs.midnightblue)
        self.pulse_panel.draw()
        self.card.draw()
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
