from REMOLib import *
from REMOLib.particles import ParticleEmitter, particleDefaultPreset

import math
import random


class mainScene(Scene):
    def initOnce(self):
        self.background_color = (18, 14, 30)
        self.glow_layer_color = (50, 36, 72)

        panel_rect = pygame.Rect(40, 40, 520, 640)
        self.info_panel = rectObj(panel_rect, radius=24, edge=4, color=Cs.black, alpha=180)

        self.title = textObj("36. 신비한 연금술사", pos=(60, 60), size=40, color=Cs.white)
        self.subtitle = textObj("제스처로 재료를 추출해 조합하세요", pos=(60, 110), size=26, color=Cs.light(Cs.grey75))

        instruction_lines = [
            "- 마우스를 드래그해 제스처를 그립니다.",
            "- 원형: 화염 / 가로선: 광휘 / 세로선: 연기",
            "- 제시된 순서를 모두 맞히면 조합 성공!",
        ]
        self.instructions = [
            textObj(line, pos=(60, 170 + i * 34), size=24, color=Cs.white) for i, line in enumerate(instruction_lines)
        ]

        self.recipe_title = textObj("오늘의 조합", pos=(60, 280), size=30, color=Cs.light(Cs.skyblue))
        self.recipe_name = textObj("", pos=(60, 320), size=32, color=Cs.orange)
        self.recipe_steps_text = textObj("", pos=(60, 360), size=26, color=Cs.light(Cs.white))
        self.recipe_hint = longTextObj("", pos=RPoint(60, 400), size=22, color=Cs.grey75, textWidth=460)

        self.sequence_text = textObj("재료 입력: -", pos=(60, 500), size=26, color=Cs.white)
        self.feedback_text = textObj("마우스로 제스처를 그려보세요", pos=(60, 540), size=26, color=Cs.light(Cs.white))
        self.success_counter = textObj("성공 0", pos=(60, 600), size=24, color=Cs.light(Cs.turquoise))
        self.failure_counter = textObj("실패 0", pos=(200, 600), size=24, color=Cs.light(Cs.salmon))
        self.last_gesture_text = textObj("감지된 제스처: -", pos=(60, 640), size=22, color=Cs.grey75)

        self.recipes = [
            {
                "name": "태양 폭발약",
                "pattern": ["Flame", "Light", "Flame"],
                "hint": "빛으로 폭발을 봉인했다가 다시 해방하면 위력이 증폭됩니다.",
            },
            {
                "name": "성운의 안개",
                "pattern": ["Smoke", "Light", "Smoke"],
                "hint": "연기를 두 번 걸러낸 뒤 빛을 스며들게 하면 부드러운 안개가 완성됩니다.",
            },
            {
                "name": "용의 숨결",
                "pattern": ["Flame", "Smoke", "Flame"],
                "hint": "불꽃 사이에 연기를 섞어야만 고열이 폭주하지 않습니다.",
            },
        ]

        self.reagent_names = {"Flame": "화염", "Smoke": "연기", "Light": "광휘"}
        self.reagent_colors = {
            "Flame": Cs.orangered,
            "Smoke": Cs.lightsteelblue,
            "Light": Cs.turquoise,
        }
        self.step_label_objs: list[textObj] = []

        self.active_recipe = random.choice(self.recipes)
        self._refresh_recipe_view()

        self.current_sequence: list[str] = []
        self.success_count = 0
        self.failure_count = 0

        self.stroke_points: list[RPoint] = []
        self.stroke_active = False

        self.cauldron_center = RPoint(1020, 480)
        self.cauldron_radius = 160
        self.cauldron_energy = 0.0
        self.cauldron_tint = (120, 150, 200)

        self.trail_emitter = ParticleEmitter(RPoint(0, 0), max_particles=220, defaults=particleDefaultPreset.magic_glitter())
        self.cauldron_fumes = ParticleEmitter(
            self.cauldron_center,
            max_particles=200,
            defaults=particleDefaultPreset.light_smoke(),
        )
        self.reagent_emitters = {
            "Flame": ParticleEmitter(self.cauldron_center, max_particles=260, defaults=particleDefaultPreset.explosion_fireball()),
            "Smoke": ParticleEmitter(self.cauldron_center, max_particles=220, defaults=particleDefaultPreset.heavy_smoke()),
            "Light": ParticleEmitter(self.cauldron_center, max_particles=240, defaults=particleDefaultPreset.magic_glitter()),
        }
        self.success_emitter = ParticleEmitter(
            self.cauldron_center,
            max_particles=320,
            defaults=particleDefaultPreset.embers(),
        )

        self.emitters = [self.trail_emitter, self.cauldron_fumes, self.success_emitter]
        self.emitters.extend(self.reagent_emitters.values())

    def update(self):
        mouse_pos = Rs.mousePos()

        if Rs.userJustLeftClicked():
            self.stroke_points = [mouse_pos]
            self.stroke_active = True
            self.feedback_text.color = Cs.light(Cs.white)

        if self.stroke_active and Rs.userIsLeftClicking():
            last_point = self.stroke_points[-1]
            if mouse_pos.distance(last_point) > 4:
                self.stroke_points.append(mouse_pos)
            self.trail_emitter.emit(4, position=mouse_pos)
        elif self.stroke_active and Rs.userJustReleasedMouseLeft():
            self.stroke_active = False
            gesture = self._recognize_gesture(self.stroke_points)
            if gesture:
                self._handle_gesture(gesture)
            else:
                self._notify_unrecognized()
            self.stroke_points.clear()

        # Ambient fumes from the cauldron
        jitter = RPoint(random.randint(-18, 18), random.randint(-12, 0))
        self.cauldron_fumes.emit(2, position=self.cauldron_center + jitter)

        self.cauldron_energy = max(0.0, self.cauldron_energy * 0.95)

        for emitter in self.emitters:
            emitter.update()

    def draw(self):
        Rs.fillScreen(self.background_color)

        # Cauldron glow layer
        glow_strength = min(1.0, self.cauldron_energy)
        tint = self.cauldron_tint
        outer_color = (
            min(255, int(self.glow_layer_color[0] + tint[0] * 0.25 * (0.4 + glow_strength))),
            min(255, int(self.glow_layer_color[1] + tint[1] * 0.25 * (0.4 + glow_strength))),
            min(255, int(self.glow_layer_color[2] + tint[2] * 0.25 * (0.4 + glow_strength))),
        )
        pygame.draw.circle(Rs.screen, outer_color, self.cauldron_center.toTuple(), self.cauldron_radius + 34)
        pygame.draw.circle(Rs.screen, (28, 22, 46), self.cauldron_center.toTuple(), self.cauldron_radius + 12)
        inner_color = (
            min(255, int(60 + tint[0] * (0.3 + glow_strength * 0.7))),
            min(255, int(68 + tint[1] * (0.3 + glow_strength * 0.7))),
            min(255, int(76 + tint[2] * (0.3 + glow_strength * 0.7))),
        )
        pygame.draw.circle(Rs.screen, inner_color, self.cauldron_center.toTuple(), self.cauldron_radius - 20)

        self.cauldron_fumes.draw()
        for key in ("Smoke", "Flame", "Light"):
            self.reagent_emitters[key].draw()
        self.success_emitter.draw()

        if len(self.stroke_points) > 1:
            pygame.draw.lines(
                Rs.screen,
                (160, 220, 255),
                False,
                [p.toTuple() for p in self.stroke_points],
                4,
            )

        self.trail_emitter.draw()

        self.info_panel.draw()
        self.title.draw()
        self.subtitle.draw()
        for label in self.instructions:
            label.draw()
        self.recipe_title.draw()
        self.recipe_name.draw()
        self.recipe_steps_text.draw()
        self.recipe_hint.draw()
        self.sequence_text.draw()
        self.feedback_text.draw()
        self.success_counter.draw()
        self.failure_counter.draw()
        self.last_gesture_text.draw()

        self._draw_recipe_progress()

    def _draw_recipe_progress(self):
        pattern = self.active_recipe["pattern"]
        base_x = 60
        base_y = 450
        radius = 22
        for idx, reagent in enumerate(pattern):
            center = (base_x + idx * 80, base_y)
            color = self.reagent_colors[reagent]
            pygame.draw.circle(Rs.screen, Cs.black, center, radius + 4)
            pygame.draw.circle(Rs.screen, color, center, radius)
            if idx < len(self.step_label_objs):
                label_obj = self.step_label_objs[idx]
                label_obj.center = RPoint(center[0], center[1] + 44)
                label_obj.draw()

            if idx < len(self.current_sequence):
                if self.current_sequence[idx] == reagent:
                    pygame.draw.circle(Rs.screen, Cs.white, center, radius - 6, width=3)
                else:
                    pygame.draw.line(
                        Rs.screen,
                        Cs.salmon,
                        (center[0] - radius + 4, center[1] - radius + 4),
                        (center[0] + radius - 4, center[1] + radius - 4),
                        4,
                    )

    def _handle_gesture(self, gesture: str):
        self.last_gesture_text.text = f"감지된 제스처: {self.reagent_names[gesture]}"
        self.last_gesture_text.color = self.reagent_colors[gesture]

        self.current_sequence.append(gesture)
        sequence_display = " - ".join(self.reagent_names[g] for g in self.current_sequence)
        self.sequence_text.text = f"재료 입력: {sequence_display}"

        emitter = self.reagent_emitters[gesture]
        burst = 90 if gesture == "Flame" else 60
        emitter.emit(burst, position=self.cauldron_center)
        self.cauldron_energy = min(1.4, self.cauldron_energy + 0.45)
        self.cauldron_tint = self.reagent_colors[gesture]

        if not self._sequence_matches_prefix():
            self._handle_failure("순서가 어긋났습니다. 다시 시도!", hard_reset=True)
            return

        if len(self.current_sequence) == len(self.active_recipe["pattern"]):
            self._complete_recipe()
        else:
            self.feedback_text.text = f"{self.reagent_names[gesture]} 재료가 가마에 흡수됩니다."
            self.feedback_text.color = Cs.light(self.reagent_colors[gesture])

    def _sequence_matches_prefix(self) -> bool:
        pattern = self.active_recipe["pattern"]
        for idx, item in enumerate(self.current_sequence):
            if pattern[idx] != item:
                return False
        return True

    def _complete_recipe(self):
        self.success_count += 1
        self.success_counter.text = f"성공 {self.success_count}"
        self.feedback_text.text = f"{self.active_recipe['name']} 조합 성공!"
        self.feedback_text.color = Cs.yellow
        self.sequence_text.text = "재료 입력: -"
        self.last_gesture_text.text = "감지된 제스처: -"
        self.last_gesture_text.color = Cs.grey75
        self.current_sequence.clear()
        self.success_emitter.emit(180, position=self.cauldron_center)
        self.cauldron_energy = 1.5
        self.cauldron_tint = Cs.yellow
        self._pick_next_recipe()

    def _handle_failure(self, message: str, *, hard_reset: bool = False):
        self.failure_count += 1
        self.failure_counter.text = f"실패 {self.failure_count}"
        self.feedback_text.text = message
        self.feedback_text.color = Cs.salmon
        self.sequence_text.text = "재료 입력: -"
        self.last_gesture_text.text = "감지된 제스처: -"
        self.last_gesture_text.color = Cs.grey75
        self.current_sequence.clear()
        self.reagent_emitters["Smoke"].emit(90, position=self.cauldron_center)
        if hard_reset:
            self.cauldron_energy *= 0.4

    def _notify_unrecognized(self):
        if self.stroke_points:
            self._handle_failure("제스처를 알아볼 수 없어요. 더 크게 그려보세요!", hard_reset=False)
        else:
            self.feedback_text.text = "제스처가 너무 짧습니다."
            self.feedback_text.color = Cs.grey75

    def _pick_next_recipe(self):
        candidates = [r for r in self.recipes if r is not self.active_recipe]
        self.active_recipe = random.choice(candidates) if candidates else self.active_recipe
        self._refresh_recipe_view()

    def _refresh_recipe_view(self):
        self.recipe_name.text = self.active_recipe["name"]
        order = " → ".join(self.reagent_names[item] for item in self.active_recipe["pattern"])
        self.recipe_steps_text.text = f"순서: {order}"
        self.recipe_hint.text = self.active_recipe["hint"]
        self.step_label_objs = [
            textObj(self.reagent_names[item], size=20, color=Cs.white) for item in self.active_recipe["pattern"]
        ]

    def _recognize_gesture(self, points: list[RPoint]) -> str | None:
        if len(points) < 8:
            return None

        total_length = 0.0
        xs = []
        ys = []
        for idx in range(1, len(points)):
            prev = points[idx - 1]
            curr = points[idx]
            total_length += prev.distance(curr)
            xs.append(curr.x)
            ys.append(curr.y)
        if total_length < 120:
            return None

        xs.append(points[0].x)
        ys.append(points[0].y)
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        center_x = sum(p.x for p in points) / len(points)
        center_y = sum(p.y for p in points) / len(points)
        total_angle = 0.0
        prev_angle = math.atan2(points[0].y - center_y, points[0].x - center_x)
        for point in points[1:]:
            angle = math.atan2(point.y - center_y, point.x - center_x)
            delta = angle - prev_angle
            while delta > math.pi:
                delta -= 2 * math.pi
            while delta < -math.pi:
                delta += 2 * math.pi
            total_angle += delta
            prev_angle = angle

        swirl_score = abs(total_angle)
        if swirl_score > math.pi * 1.6 and width > 40 and height > 40:
            return "Flame"

        if width > height * 1.6:
            return "Light"
        if height > width * 1.6:
            return "Smoke"

        if swirl_score > math.pi:
            return "Flame"

        return None


class Scenes:
    mainScene = mainScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1600, 900),
        screen_size=(1600, 900),
        fullscreen=False,
        caption="36. 신비한 연금술사",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
