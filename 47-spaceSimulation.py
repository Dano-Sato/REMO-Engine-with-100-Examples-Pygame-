from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from REMOLib.core import *


@dataclass
class Planet:
    name: str
    biome: str
    distance: int
    danger: int
    science_reward: int
    credit_reward: int


class SpaceButton(rectObj):
    def __init__(self, label: str, size: tuple[int, int], color: tuple[int, int, int], on_click):
        super().__init__(pygame.Rect(0, 0, size[0], size[1]), color=color, edge=3, radius=16)
        self._base_color = color
        self._hover_color = Cs.light(color)
        self._on_click = on_click
        self.enabled = True

        self.label = textObj(label, size=24, color=Cs.white)
        self.label.setParent(self, depth=1)
        self.label.center = self.offsetRect.center

    def update(self):
        hovered = self.collideMouse() and self.enabled
        self.color = self._hover_color if hovered else self._base_color
        alpha = 255 if self.enabled else 120
        self.alpha = alpha
        self.label.alpha = alpha

        if hovered and Rs.userJustLeftClicked():
            self._on_click()


class PlanetCard(rectObj):
    def __init__(self, planet: Planet, on_select):
        super().__init__(pygame.Rect(0, 0, 280, 210), color=Cs.dark(Cs.steelblue), edge=3, radius=18)
        self.planet = planet
        self._on_select = on_select
        self._selected = False

        self.title = textObj(planet.name, size=28, color=Cs.white)
        self.title.setParent(self, depth=1)
        self.title.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 14)

        self.info = longTextObj("", pos=RPoint(20, 58), size=19, color=Cs.white, textWidth=240)
        self.info.setParent(self, depth=1)
        self._refresh_text()

    def _refresh_text(self) -> None:
        p = self.planet
        self.info.text = (
            f"환경: {p.biome}\n"
            f"거리: {p.distance} 연료\n"
            f"위험도: {p.danger}/10\n"
            f"예상 과학: +{p.science_reward}\n"
            f"예상 크레딧: +{p.credit_reward}"
        )

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def update(self):
        hovered = self.collideMouse()
        base = Cs.dark(Cs.steelblue)
        if self._selected:
            base = Cs.dark(Cs.mediumpurple)
        self.color = Cs.light(base) if hovered else base

        if hovered and Rs.userJustLeftClicked():
            self._on_select(self)


class SpaceSimulationScene(Scene):
    def initOnce(self):
        self.random = random.Random()
        self.day = 1
        self.action_points = 2
        self.fuel = 22
        self.hull = 100
        self.morale = 70
        self.science = 0
        self.credits = 18
        self.sectors_explored = 0
        self.selected_card: PlanetCard | None = None
        self.log_lines: list[str] = []

        self.planets = [
            Planet("에코스", "바다형", 5, 2, 5, 4),
            Planet("벨트라", "사막형", 7, 4, 9, 8),
            Planet("노바-IX", "빙하형", 8, 5, 12, 6),
            Planet("칼리고", "화산형", 10, 7, 16, 12),
        ]

        self._build_ui()
        self._start_day_event()
        self._refresh_ui()

    def _build_ui(self):
        self.title = textObj("REMO Space Expedition", size=44, color=Cs.white)
        self.title.pos = RPoint(40, 24)

        self.status_panel = rectObj(pygame.Rect(36, 92, 1240, 126), color=Cs.dark(Cs.midnightblue), edge=3, radius=14)
        self.status_text = longTextObj("", pos=RPoint(56, 112), size=25, color=Cs.white, textWidth=1200)

        self.cards = [PlanetCard(planet, self._select_planet) for planet in self.planets]
        self.card_layout = layoutObj(pygame.Rect(36, 250, 1240, 220), spacing=18, isVertical=False)
        for card in self.cards:
            card.setParent(self.card_layout)

        self.action_panel = rectObj(pygame.Rect(36, 490, 1240, 250), color=Cs.dark(Cs.black), edge=3, radius=14)
        self.selected_planet_text = textObj("선택된 행성: 없음", size=28, color=Cs.white)
        self.selected_planet_text.pos = RPoint(58, 512)

        self.explore_button = SpaceButton("탐사 출발", (220, 68), Cs.dark(Cs.royalblue), self._explore_selected)
        self.repair_button = SpaceButton("선체 수리", (220, 68), Cs.dark(Cs.seagreen), self._repair_ship)
        self.research_button = SpaceButton("연구 분석", (220, 68), Cs.dark(Cs.orchid), self._analyze_science)
        self.next_day_button = SpaceButton("다음 날", (220, 68), Cs.dark(Cs.peru), self._next_day)

        self.explore_button.pos = RPoint(58, 560)
        self.repair_button.pos = RPoint(300, 560)
        self.research_button.pos = RPoint(542, 560)
        self.next_day_button.pos = RPoint(784, 560)

        self.tip_text = longTextObj(
            "목표: 12일 안에 과학 점수 80점과 탐사 구역 8개를 달성하세요.",
            pos=RPoint(58, 646),
            size=20,
            color=Cs.light(Cs.gold),
            textWidth=1160,
        )

        self.log_panel = rectObj(pygame.Rect(36, 760, 1240, 280), color=Cs.dark(Cs.slategray), edge=3, radius=14)
        self.log_title = textObj("항해 로그", size=30, color=Cs.white)
        self.log_title.pos = RPoint(56, 778)
        self.log_text = longTextObj("", pos=RPoint(56, 822), size=21, color=Cs.white, textWidth=1180)

    def _select_planet(self, card: PlanetCard):
        self.selected_card = card
        for each in self.cards:
            each.set_selected(each is card)
        self.selected_planet_text.text = f"선택된 행성: {card.planet.name}"

    def _use_ap(self, amount: int = 1) -> bool:
        if self.action_points < amount:
            self._log("행동 포인트가 부족합니다.")
            return False
        self.action_points -= amount
        return True

    def _explore_selected(self):
        if self.selected_card is None:
            self._log("먼저 탐사할 행성을 선택하세요.")
            return
        if not self._use_ap():
            return

        target = self.selected_card.planet
        if self.fuel < target.distance:
            self._log("연료가 부족해 출발할 수 없습니다.")
            self.action_points += 1
            return

        self.fuel -= target.distance
        risk_roll = self.random.randint(1, 10) + self.random.randint(0, 3)
        success = risk_roll >= target.danger

        if success:
            science_gain = target.science_reward + self.random.randint(0, 3)
            credit_gain = target.credit_reward + self.random.randint(0, 2)
            morale_gain = 1 if target.danger >= 5 else 2
            self.science += science_gain
            self.credits += credit_gain
            self.morale = min(100, self.morale + morale_gain)
            self.sectors_explored += 1
            self._log(f"{target.name} 탐사 성공! 과학 +{science_gain}, 크레딧 +{credit_gain}")
        else:
            hull_loss = 7 + target.danger
            morale_loss = 4 + target.danger // 2
            self.hull = max(0, self.hull - hull_loss)
            self.morale = max(0, self.morale - morale_loss)
            self._log(f"{target.name} 탐사 중 폭풍 조우! 선체 -{hull_loss}, 사기 -{morale_loss}")

        self._check_endings()
        self._refresh_ui()

    def _repair_ship(self):
        if not self._use_ap():
            return
        if self.credits < 4:
            self._log("수리에 필요한 크레딧(4)이 부족합니다.")
            self.action_points += 1
            return
        self.credits -= 4
        recovered = self.random.randint(10, 18)
        self.hull = min(100, self.hull + recovered)
        self._log(f"긴급 수리 완료. 선체 +{recovered}")
        self._refresh_ui()

    def _analyze_science(self):
        if not self._use_ap():
            return
        if self.science < 6:
            self._log("분석할 과학 데이터가 부족합니다. (최소 6)")
            self.action_points += 1
            return

        self.science -= 6
        bonus = self.random.randint(5, 10)
        fuel_gain = self.random.randint(1, 3)
        self.credits += bonus
        self.fuel += fuel_gain
        self._log(f"연구 분석 성공. 크레딧 +{bonus}, 연료 +{fuel_gain}")
        self._refresh_ui()

    def _next_day(self):
        self.day += 1
        self.action_points = 2
        self.fuel += 2
        self.hull = max(0, self.hull - 2)
        self.morale = max(0, self.morale - 1)
        self._start_day_event()
        self._check_endings()
        self._refresh_ui()

    def _start_day_event(self):
        roll = self.random.randint(1, 100)
        if roll <= 22:
            gain = self.random.randint(3, 6)
            self.fuel += gain
            self._log(f"태양풍 충전 성공: 연료 +{gain}")
        elif roll <= 42:
            cost = self.random.randint(2, 5)
            self.credits = max(0, self.credits - cost)
            self._log(f"우주먼지 손상 보수비 발생: 크레딧 -{cost}")
        elif roll <= 58:
            morale_boost = self.random.randint(3, 6)
            self.morale = min(100, self.morale + morale_boost)
            self._log(f"승무원 이벤트 성공: 사기 +{morale_boost}")
        elif roll <= 73:
            hull_damage = self.random.randint(4, 9)
            self.hull = max(0, self.hull - hull_damage)
            self._log(f"소형 운석 충돌: 선체 -{hull_damage}")
        else:
            self._log("특이사항 없음. 항로 안정.")

    def _check_endings(self):
        if self.hull <= 0:
            self._log("선체가 붕괴했습니다. 탐사 실패.")
            self.action_points = 0
        elif self.day > 12:
            if self.science >= 80 and self.sectors_explored >= 8:
                self._log("원정 성공! 은하 과학 협약에 합류했습니다.")
            else:
                self._log("기간 종료. 목표 달성에 실패했습니다.")
            self.action_points = 0

    def _log(self, message: str):
        self.log_lines.append(f"[Day {self.day}] {message}")
        self.log_lines = self.log_lines[-8:]
        self.log_text.text = "\n".join(reversed(self.log_lines))

    def _refresh_ui(self):
        self.status_text.text = (
            f"Day {self.day}  |  행동 {self.action_points}/2  |  연료 {self.fuel}  |  선체 {self.hull}%  |  "
            f"사기 {self.morale}  |  과학 {self.science}  |  크레딧 {self.credits}  |  탐사구역 {self.sectors_explored}"
        )
        ended = self.action_points == 0 and (self.hull <= 0 or self.day > 12)
        enabled = not ended
        self.explore_button.enabled = enabled
        self.repair_button.enabled = enabled
        self.research_button.enabled = enabled
        self.next_day_button.enabled = enabled

    def update(self):
        self.card_layout.adjustLayout()
        self.card_layout.update()
        self.explore_button.update()
        self.repair_button.update()
        self.research_button.update()
        self.next_day_button.update()

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.black))
        self.title.draw()
        self.status_panel.draw()
        self.status_text.draw()
        self.card_layout.draw()
        self.action_panel.draw()
        self.selected_planet_text.draw()
        self.explore_button.draw()
        self.repair_button.draw()
        self.research_button.draw()
        self.next_day_button.draw()
        self.tip_text.draw()
        self.log_panel.draw()
        self.log_title.draw()
        self.log_text.draw()


class Scenes:
    simulation = SpaceSimulationScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1280, 1080),
        screen_size=(1280, 1080),
        fullscreen=False,
        caption="REMO Space Expedition",
    )
    game.setCurrentScene(Scenes.simulation)
    game.run()
