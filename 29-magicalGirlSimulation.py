from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from REMOLib.core import *


@dataclass
class MagicalGirl:
    name: str
    element: str
    attack: int
    support: int
    charm: int
    cool_down: int = 0
    fatigue: int = 0
    level: int = 1
    experience: int = 0

    def is_available(self) -> bool:
        return self.cool_down == 0

    def readiness_multiplier(self) -> float:
        fatigue_penalty = max(0.55, 1.0 - self.fatigue / 130.0)
        morale_boost = 1.0 + self.charm * 0.015
        return fatigue_penalty * morale_boost

    def performance_score(self) -> float:
        base = self.attack * 1.4 + self.support * 1.05 + self.level * 3.2
        synergy = self.charm * 0.45
        return (base + synergy) * self.readiness_multiplier()

    def support_score(self) -> float:
        base = self.support * 1.25 + self.charm * 0.75 + self.level * 2.0
        return base * self.readiness_multiplier()

    def mission_fatigue(self, difficulty: int) -> None:
        self.fatigue = min(120, self.fatigue + 12 + difficulty * 8)
        self.cool_down = max(self.cool_down, max(1, difficulty // 2))

    def advance_day(self) -> bool:
        recovered = False
        if self.cool_down > 0:
            self.cool_down -= 1
            recovered = self.cool_down == 0
        self.fatigue = max(0, self.fatigue - 18)
        return recovered

    def gain_experience(self, amount: int) -> bool:
        self.experience += amount
        leveled_up = False
        while self.experience >= self._threshold():
            self.experience -= self._threshold()
            self.level += 1
            leveled_up = True
            self.attack += 1 + (self.level % 2)
            self.support += 1 if self.level % 3 != 0 else 2
            if self.level % 2 == 0:
                self.charm += 1
        return leveled_up

    def _threshold(self) -> int:
        return 40 + self.level * 12


@dataclass
class Mission:
    name: str
    focus: str
    difficulty: int
    threat: int
    description: str
    reward_safety: int
    reward_morale: int
    reward_fans: int


class MagicalGirlCard(rectObj):
    ELEMENT_COLORS: dict[str, tuple[int, int, int]] = {
        "빛": Cs.deeppink,
        "별": Cs.skyblue,
        "어둠": Cs.indigo,
        "숲": Cs.seagreen,
        "물": Cs.turquoise,
        "불꽃": Cs.orangered,
    }

    def __init__(self, girl: MagicalGirl, on_select):
        base_color = Cs.dark(self.ELEMENT_COLORS.get(girl.element, Cs.mediumpurple))
        super().__init__(pygame.Rect(0, 0, 190, 270), color=base_color, edge=5, radius=18)
        self.girl = girl
        self._on_select = on_select
        self._base_color = base_color
        self._hover_color = Cs.light(base_color)
        self._rest_color = Cs.dark(Cs.slategray)
        self._selected = False

        self.name_text = textObj(girl.name, size=26, color=Cs.white)
        self.name_text.setParent(self, depth=1)
        self.name_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 18)

        self.element_badge = rectObj(pygame.Rect(0, 0, 120, 34), radius=14, edge=2,
                                     color=Cs.bright(self.ELEMENT_COLORS.get(girl.element, Cs.mediumpurple)))
        self.element_badge.setParent(self, depth=1)
        self.element_badge.midtop = self.name_text.rect.midbottom + RPoint(0, 12)

        self.element_text = textObj(f"{girl.element} 속성", size=18, color=Cs.white)
        self.element_text.setParent(self.element_badge, depth=1)
        self.element_text.center = self.element_badge.offsetRect.center

        self.level_text = textObj("", size=20, color=Cs.white)
        self.level_text.setParent(self, depth=1)
        self.level_text.midtop = self.element_badge.rect.midbottom + RPoint(0, 10)

        self.stats_text = textObj("", size=18, color=Cs.white)
        self.stats_text.setParent(self, depth=1)
        self.stats_text.y = self.level_text.rect.bottom + 6

        self.power_text = textObj("", size=18, color=Cs.yellow)
        self.power_text.setParent(self, depth=1)
        self.power_text.y = self.stats_text.rect.bottom + 6

        self.condition_text = textObj("", size=18, color=Cs.white)
        self.condition_text.setParent(self, depth=1)
        self.condition_text.y = self.power_text.rect.bottom + 6

        self.status_text = textObj("", size=18, color=Cs.white)
        self.status_text.setParent(self, depth=1)
        self.status_text.y = self.offsetRect.height - 18

        self.refresh()

    def refresh(self) -> None:
        girl = self.girl
        self.level_text.text = f"Lv.{girl.level} 경험치 {girl.experience}/{girl._threshold()}"
        self.stats_text.text = f"공격 {girl.attack} · 지원 {girl.support} · 매력 {girl.charm}"
        self.power_text.text = f"임무 적성 {girl.performance_score():.1f}"
        fatigue_state = "안정" if girl.fatigue <= 20 else "피곤" if girl.fatigue <= 60 else "과로"
        self.condition_text.text = f"피로 {girl.fatigue} ({fatigue_state})"
        if girl.is_available():
            self.status_text.text = "상태: 출동 가능"
            self.status_text.color = Cs.white
        else:
            self.status_text.text = f"휴식 {girl.cool_down}일 남음"
            self.status_text.color = Cs.light(Cs.salmon)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def update(self) -> None:
        hovered = self.collideMouse()
        if Rs.userJustLeftClicked() and hovered:
            self._on_select(self)

        if not self.girl.is_available():
            target = self._rest_color
        else:
            target = self._hover_color if hovered else self._base_color

        if self._selected:
            target = Cs.bright(target)

        if self.color != target:
            self.color = target

        return


class MissionWidget(rectObj):
    DIFFICULTY_COLORS = {
        1: Cs.dark(Cs.lightgreen),
        2: Cs.dark(Cs.turquoise),
        3: Cs.dark(Cs.dodgerblue),
        4: Cs.dark(Cs.mediumorchid),
        5: Cs.dark(Cs.crimson),
    }

    def __init__(self, mission: Mission, on_assign, on_ready):
        base_color = self.DIFFICULTY_COLORS.get(mission.difficulty, Cs.dark(Cs.steelblue))
        super().__init__(pygame.Rect(0, 0, 380, 170), color=base_color, edge=4, radius=18)
        self._on_assign = on_assign
        self._on_ready = on_ready
        self._base_color = base_color
        self._hover_color = Cs.light(base_color)
        self._assign_enabled = True
        self._pending_refresh = False
        self._refresh_tick = 0

        self.title_text = textObj("", size=24, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 16)

        self.focus_text = textObj("", size=18, color=Cs.white)
        self.focus_text.setParent(self, depth=1)
        self.focus_text.midtop = self.title_text.rect.midbottom + RPoint(0, 8)

        self.desc_text = longTextObj("", pos=RPoint(0, 0), size=18, color=Cs.white, textWidth=320)
        self.desc_text.setParent(self, depth=1)
        self.desc_text.x = 28
        self.desc_text.y = self.focus_text.rect.bottom + 6

        self.status_text = textObj("", size=18, color=Cs.white)
        self.status_text.setParent(self, depth=1)
        self.status_text.x = 28
        self.status_text.y = self.desc_text.rect.bottom + 8

        self.reward_text = textObj("", size=18, color=Cs.yellow)
        self.reward_text.setParent(self, depth=1)
        self.reward_text.midbottom = RPoint(self.offsetRect.midbottom) - RPoint(0, 18)

        self.set_mission(mission)

    def set_mission(self, mission: Mission) -> None:
        self.mission = mission
        self._base_color = self.DIFFICULTY_COLORS.get(mission.difficulty, Cs.dark(Cs.steelblue))
        self._hover_color = Cs.light(self._base_color)
        self.color = self._base_color
        self.title_text.text = mission.name
        self.focus_text.text = f"추천 속성: {mission.focus}"
        self.desc_text.text = mission.description
        self.desc_text.x = 2800
        self.desc_text.y = self.focus_text.rect.bottom + 6
        self.status_text.text = f"위협도 {mission.threat} · 난이도 {mission.difficulty}"
        self.status_text.color = Cs.white
        self.status_text.x = 28
        self.status_text.y = self.desc_text.rect.bottom + 8
        self.reward_text.text = (
            f"보상: 안전도 +{mission.reward_safety}, 사기 +{mission.reward_morale}, 팬 +{mission.reward_fans}"
        )
        self._assign_enabled = True
        self._pending_refresh = False

    def flash_result(self, message: str, success: bool) -> None:
        self.status_text.text = message
        self.status_text.color = Cs.light(Cs.green) if success else Cs.light(Cs.salmon)
        self._assign_enabled = False
        self._pending_refresh = True
        self._refresh_tick = pygame.time.get_ticks() + 1500

    def update(self) -> None:
        hovered = self.collideMouse()
        if hovered and self._assign_enabled and Rs.userJustLeftClicked():
            self._on_assign(self)

        if self._pending_refresh and pygame.time.get_ticks() >= self._refresh_tick:
            self._pending_refresh = False
            self._on_ready(self)

        target = self._hover_color if hovered and self._assign_enabled else self._base_color
        if self.color != target:
            self.color = target

        return


class SimulationScene(Scene):
    def initOnce(self):
        self.day = 1
        self.city_safety = 62
        self.team_morale = 58
        self.fan_support = 45
        self.selected_card: MagicalGirlCard | None = None
        self.log_messages: list[str] = []

        self.status_layout = layoutObj(pos=RPoint(60, 40), spacing=12, isVertical=True)
        self.day_text = textObj("", size=30, color=Cs.white)
        self.city_text = textObj("", size=24, color=Cs.tiffanyBlue)
        self.morale_text = textObj("", size=24, color=Cs.light(Cs.pink))
        self.fan_text = textObj("", size=24, color=Cs.light(Cs.lightgoldenrodyellow))
        for label in (self.day_text, self.city_text, self.morale_text, self.fan_text):
            label.setParent(self.status_layout)
        self.status_layout.adjustLayout()

        self.selection_text = textObj("선택된 마법소녀: 없음", size=22, color=Cs.white)
        self.selection_text.pos = RPoint(160, 612)

        self.tip_box = longTextObj(
            "카드를 선택한 뒤 임무를 클릭하여 배치하세요. 하루가 지나면 휴식을 마친 소녀가 복귀합니다.",
            pos=RPoint(60, 220),
            size=20,
            color=Cs.white,
            textWidth=440,
        )

        self.log_box = longTextObj("", pos=RPoint(60, 300), size=20, color=Cs.white, textWidth=440)

        self.card_background = rectObj(pygame.Rect(0, 0, 1040, 280), color=Cs.dark(Cs.slategray), edge=6, radius=26)
        self.card_background.pos = RPoint(120, 720)

        self.mission_panel = rectObj(pygame.Rect(0, 0, 600, 440), color=Cs.dark(Cs.darkslateblue), edge=6, radius=24)
        self.mission_panel.pos = RPoint(520, 100)

        self.next_day_button = textButton(
            "다음 날 시작",
            pygame.Rect(0, 0, 220, 60),
            color=Cs.tiffanyBlue,
            textColor=Cs.white,
        )
        self.next_day_button.pos = RPoint(960, 40)
        self.next_day_button.connect(self._start_next_day)

        self.girls = self._create_magical_girls()
        self.card_layout = cardLayout(RPoint(160, 760), spacing=26, maxWidth=960, isVertical=False)
        self.card_widgets: list[MagicalGirlCard] = []
        for girl in self.girls:
            widget = MagicalGirlCard(girl, self._handle_card_selection)
            widget.setParent(self.card_layout)
            self.card_widgets.append(widget)
        self.card_layout.adjustLayout()

        self.mission_layout = layoutObj(pos=RPoint(540, 140), spacing=24, isVertical=True)
        self.mission_widgets: list[MissionWidget] = []
        for _ in range(3):
            mission_widget = MissionWidget(self._generate_mission(), self._assign_selected_to_mission, self._refresh_mission)
            mission_widget.setParent(self.mission_layout)
            self.mission_widgets.append(mission_widget)
        self.mission_layout.adjustLayout()

        self._refresh_status_labels()
        self._log("마법소녀 지휘본부가 가동되었습니다.")

    def init(self):
        return

    def _create_magical_girls(self) -> list[MagicalGirl]:
        roster = [
            ("루미나", "빛", 7, 5, 6),
            ("스텔라", "별", 6, 6, 7),
            ("녹터", "어둠", 8, 4, 5),
            ("실비", "물", 5, 7, 6),
            ("플레어", "불꽃", 9, 3, 5),
            ("베르데", "숲", 6, 7, 5),
        ]
        return [MagicalGirl(*info) for info in roster]

    def _generate_mission(self) -> Mission:
        focus = random.choice(["빛", "별", "어둠", "숲", "물", "불꽃"])
        names = [
            "밤하늘 순찰",
            "도심 위로 콘서트",
            "시공 균열 봉인",
            "어둠의 흔적 정화",
            "시민 안전 귀환",
            "별빛 축제 지원",
        ]
        descriptions = [
            "{focus} 에너지가 요동쳐 주변을 안정시켜야 합니다.",
            "시민들의 공포를 달래기 위한 섬세한 대응이 필요합니다.",
            "강력한 마물이 출현해 즉각적인 전투가 요구됩니다.",
            "팀워크와 치유 마법으로 부상자를 보살펴야 합니다.",
        ]
        difficulty = random.randint(1, 5)
        threat = random.randint(12, 28)
        reward_safety = 5 + difficulty * 3 + threat // 6
        reward_morale = 2 + max(1, difficulty // 2)
        reward_fans = random.randint(1, 4) + (1 if focus in ("빛", "별") else 0)
        description = random.choice(descriptions).format(focus=focus)
        name = random.choice(names)
        return Mission(name, focus, difficulty, threat, description, reward_safety, reward_morale, reward_fans)

    def _refresh_status_labels(self) -> None:
        self.day_text.text = f"{self.day}일차 작전"
        self.city_text.text = f"도시 안전도: {self.city_safety}"
        self.morale_text.text = f"팀 사기: {self.team_morale}"
        self.fan_text.text = f"팬 호감도: {self.fan_support}"
        self.status_layout.adjustLayout()

    def _log(self, message: str) -> None:
        self.log_messages.append(message)
        self.log_messages = self.log_messages[-7:]
        self.log_box.text = "\n".join(self.log_messages)

    def _handle_card_selection(self, widget: MagicalGirlCard) -> None:
        if self.selected_card is widget:
            widget.set_selected(False)
            self.selected_card = None
        else:
            if self.selected_card:
                self.selected_card.set_selected(False)
            self.selected_card = widget
            widget.set_selected(True)
        self._update_selection_text()

    def _update_selection_text(self) -> None:
        if self.selected_card:
            girl = self.selected_card.girl
            self.selection_text.text = f"선택된 마법소녀: {girl.name} ({girl.element})"
        else:
            self.selection_text.text = "선택된 마법소녀: 없음"

    def _assign_selected_to_mission(self, mission_widget: MissionWidget) -> None:
        if not self.selected_card:
            self._log("먼저 출동시킬 마법소녀 카드를 선택하세요.")
            return

        card = self.selected_card
        girl = card.girl
        if not girl.is_available():
            self._log(f"{girl.name}은(는) 아직 휴식 중입니다.")
            card.set_selected(False)
            self.selected_card = None
            self._update_selection_text()
            return

        mission = mission_widget.mission
        success, summary, detail_lines, rest_days = self._resolve_mission(mission, girl)
        girl.cool_down = rest_days
        girl.mission_fatigue(mission.difficulty)
        card.refresh()
        mission_widget.flash_result(summary, success)
        self._log(summary)
        for line in detail_lines:
            self._log(line)
        if success:
            self._log(f"'{mission.name}' 임무가 완료되었습니다.")
        else:
            self._log(f"'{mission.name}' 임무가 실패했습니다. 대책이 필요합니다.")

        card.set_selected(False)
        self.selected_card = None
        self._update_selection_text()
        self._refresh_status_labels()

    def _refresh_mission(self, mission_widget: MissionWidget) -> None:
        mission_widget.set_mission(self._generate_mission())
        self.mission_layout.adjustLayout()

    def _resolve_mission(self, mission: Mission, girl: MagicalGirl) -> tuple[bool, str, list[str], int]:
        performance = girl.performance_score()
        support = girl.support_score()
        synergy = 1.0
        if mission.focus == girl.element:
            synergy += 0.25
        elif mission.focus in ("빛", "별") and girl.element in ("빛", "별"):
            synergy += 0.1
        elif mission.focus in ("숲", "물") and girl.element in ("숲", "물"):
            synergy += 0.1

        random_factor = random.uniform(-6, 6)
        threat_scale = mission.threat * 0.6
        final_score = (performance * 1.1 + support * 0.7) * synergy + random_factor
        difficulty_target = mission.difficulty * 14 + threat_scale
        success = final_score >= difficulty_target

        rest_days = max(1, mission.difficulty // 2)
        exp_gain = 10 + mission.difficulty * 4
        leveled = girl.gain_experience(exp_gain)

        detail_lines: list[str] = []
        detail_lines.append(
            f"{girl.name}의 수행 평가: {final_score:.1f} (목표 {difficulty_target:.1f})"
        )

        if success:
            self.city_safety = min(100, self.city_safety + mission.reward_safety)
            morale_gain = mission.reward_morale + max(1, girl.charm // 3)
            self.team_morale = min(100, self.team_morale + morale_gain)
            self.fan_support = min(100, self.fan_support + mission.reward_fans)
            summary = f"{girl.name}이(가) '{mission.name}' 임무를 성공시켰습니다!"
            detail_lines.append(
                f"도시 안전도 +{mission.reward_safety}, 팀 사기 +{morale_gain}, 팬 호감도 +{mission.reward_fans}"
            )
        else:
            safety_loss = max(3, mission.reward_safety // 2)
            morale_loss = max(2, mission.reward_morale + mission.difficulty - 1)
            fan_loss = max(1, mission.reward_fans // 2)
            self.city_safety = max(0, self.city_safety - safety_loss)
            self.team_morale = max(0, self.team_morale - morale_loss)
            self.fan_support = max(0, self.fan_support - fan_loss)
            summary = f"{girl.name}이(가) '{mission.name}' 임무에서 고전했습니다."
            detail_lines.append(
                f"도시 안전도 -{safety_loss}, 팀 사기 -{morale_loss}, 팬 호감도 -{fan_loss}"
            )

        if leveled:
            detail_lines.append(f"{girl.name}이(가) 레벨 {girl.level}로 성장했습니다!")

        return success, summary, detail_lines, rest_days

    def _start_next_day(self) -> None:
        self.day += 1
        overnight_threat = sum(widget.mission.difficulty for widget in self.mission_widgets)
        safety_decay = max(1, overnight_threat // 2)
        self.city_safety = max(0, self.city_safety - safety_decay)
        self.team_morale = max(0, self.team_morale - 1)
        recovered_names = []
        for card in self.card_widgets:
            if card.girl.advance_day():
                recovered_names.append(card.girl.name)
            card.refresh()
        if recovered_names:
            self._log(f"{', '.join(recovered_names)}이(가) 휴식을 마치고 복귀했습니다.")
        self._log(f"{self.day}일차가 시작되었습니다. 밤새 도시 안전도가 {safety_decay} 감소했습니다.")
        self._refresh_status_labels()

    def update(self):
        self.card_layout.adjustLayout()
        self.card_layout.update()
        self.mission_layout.update()
        self.next_day_button.update()
        return

    def draw(self):
        Rs.fillScreen(Cs.dark(Cs.midnightblue))
        self.mission_panel.draw()
        self.card_background.draw()
        self.status_layout.draw()
        self.tip_box.draw()
        self.log_box.draw()
        self.selection_text.draw()
        self.mission_layout.draw()
        self.card_layout.draw()
        self.next_day_button.draw()
        return


class Scenes:
    simulation = SimulationScene()


if __name__ == "__main__":
    game = REMOGame(
        window_resolution=(1280, 1080),
        screen_size=(1280, 1080),
        fullscreen=False,
        caption="Magical Girl Command",
    )
    game.setCurrentScene(Scenes.simulation)
    game.run()
