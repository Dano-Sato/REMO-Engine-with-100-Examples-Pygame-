from __future__ import annotations

import math
import random
import time

from REMOLib import *


class IdleMiningScene(Scene):
    ENCHANT_TYPES = [
        ("gold_pct", "초당 골드", 50.0),
        ("crit_gold_pct", "초당 크리티컬 골드", 200.0),
        ("success_pct", "강화 성공률", 20.0),
        ("crit_chance_pct", "크리티컬 확률", 100.0),
    ]

    def initOnce(self):
        self.gold = 5000.0
        self.enhance_level = 1
        self.protect_destroy = False

        self.enchant_slots = [self._roll_enchant_slot() for _ in range(5)]
        self.selected_slot = 0

        self.spell_attempts_used = 0
        self.spell_bonus_percent = 0.0

        self.logs: list[str] = []

        self.last_update_time = time.time()
        self.second_accumulator = 0.0

        self.title = textObj("50. REMO 방치 광부", pos=(50, 25), size=44, color=Cs.white)
        self.subtitle = textObj("강화 · 인챈트 · 주문으로 초당 골드를 폭증시키세요", pos=(52, 78), size=24, color=Cs.light(Cs.skyblue))

        self.info_text = longTextObj("", pos=RPoint(50, 130), size=24, color=Cs.white, textWidth=900)
        self.enchant_text = longTextObj("", pos=RPoint(50, 360), size=22, color=Cs.light(Cs.lightgoldenrodyellow), textWidth=1020)
        self.log_text = longTextObj("", pos=RPoint(1180, 180), size=20, color=Cs.light(Cs.white), textWidth=620)

        self.left_panel = rectObj(pygame.Rect(35, 115, 1080, 920), color=(32, 38, 52), radius=20)
        self.right_panel = rectObj(pygame.Rect(1140, 115, 730, 920), color=(34, 44, 40), radius=20)

        self.buttons: dict[str, pygame.Rect] = {
            "enhance": pygame.Rect(550, 290, 220, 56),
            "protect": pygame.Rect(790, 290, 250, 56),
            "roll_all": pygame.Rect(50, 720, 290, 52),
            "roll_one": pygame.Rect(360, 720, 300, 52),
            "spell_10": pygame.Rect(50, 860, 300, 52),
            "spell_50": pygame.Rect(370, 860, 300, 52),
            "spell_reset": pygame.Rect(690, 860, 360, 52),
        }

        self.slot_buttons = [pygame.Rect(50 + i * 190, 650, 170, 52) for i in range(5)]

        self._push_log("게임 시작! 방치 수익이 발생합니다.")

    def _roll_weighted_value(self, max_value: float) -> float:
        # x in [0, 1], exponential rarity toward high-end values.
        lam = 4.5
        u = random.random()
        normalized = -math.log(1.0 - u * (1.0 - math.exp(-lam))) / lam
        return max_value * normalized

    def _roll_enchant_slot(self) -> dict[str, str | float]:
        stat_key, stat_label, stat_max = random.choice(self.ENCHANT_TYPES)
        return {
            "key": stat_key,
            "label": stat_label,
            "value": self._roll_weighted_value(stat_max),
        }

    def _push_log(self, message: str) -> None:
        self.logs.append(message)
        self.logs = self.logs[-12:]
        self.log_text.text = "\n".join(f"- {line}" for line in reversed(self.logs))

    def _base_success_chance(self) -> float:
        return max(5.0, 100.0 - (self.enhance_level - 1) * 5.0)

    def _destroy_chance(self) -> float:
        if self.enhance_level < 10:
            return 0.0
        return float(self.enhance_level - 9)

    def _enhance_cost(self) -> int:
        return int(100 * (1.3 ** (self.enhance_level - 1)))

    def _total_enchant_bonus(self) -> dict[str, float]:
        totals = {
            "gold_pct": 0.0,
            "crit_gold_pct": 0.0,
            "success_pct": 0.0,
            "crit_chance_pct": 0.0,
        }
        for slot in self.enchant_slots:
            totals[slot["key"]] += float(slot["value"])

        return {
            "gold_pct": min(100.0, totals["gold_pct"]),
            "crit_gold_pct": min(1000.0, totals["crit_gold_pct"]),
            "success_pct": min(20.0, totals["success_pct"]),
            "crit_chance_pct": min(100.0, totals["crit_chance_pct"]),
        }

    def _gold_per_second_preview(self) -> float:
        bonus = self._total_enchant_bonus()
        base = 1.0 + float(self.enhance_level ** 2.5)
        after_enchant = base * (1.0 + bonus["gold_pct"] / 100.0)
        after_spell = after_enchant * (1.0 + self.spell_bonus_percent / 100.0)
        expected_crit_factor = 1.0 + (bonus["crit_chance_pct"] / 100.0) * (bonus["crit_gold_pct"] / 100.0)
        return after_spell * expected_crit_factor

    def _produce_gold_for_one_second(self) -> None:
        bonus = self._total_enchant_bonus()
        amount = 1.0 + float(self.enhance_level ** 2.5)
        amount *= 1.0 + bonus["gold_pct"] / 100.0
        amount *= 1.0 + self.spell_bonus_percent / 100.0

        if random.random() * 100.0 < bonus["crit_chance_pct"]:
            amount *= 1.0 + bonus["crit_gold_pct"] / 100.0

        self.gold += amount

    def _try_enhance(self) -> None:
        base_cost = self._enhance_cost()
        cost = base_cost * (3 if self.protect_destroy else 1)
        if self.gold < cost:
            self._push_log("강화 골드 부족!")
            return

        self.gold -= cost
        bonus = self._total_enchant_bonus()
        success_chance = min(100.0, self._base_success_chance() + bonus["success_pct"])

        if random.random() * 100.0 < success_chance:
            self.enhance_level += 1
            self._push_log(f"강화 성공! -> +{self.enhance_level} 레벨")
            return

        destroy = False
        destroy_chance = self._destroy_chance()
        if (not self.protect_destroy) and destroy_chance > 0 and random.random() * 100.0 < destroy_chance:
            destroy = True

        if destroy:
            self.enhance_level = 1
            self._push_log("강화 실패 + 장비 파괴! 1레벨로 복구")
        else:
            self.enhance_level = max(1, self.enhance_level - 1)
            self._push_log(f"강화 실패... {self.enhance_level} 레벨로 하락")

    def _roll_all_slots(self) -> None:
        if self.gold < 1000:
            self._push_log("전체 인챈트 비용(1000G) 부족")
            return
        self.gold -= 1000
        self.enchant_slots = [self._roll_enchant_slot() for _ in range(5)]
        self._push_log("인챈트 5슬롯 전체 재추첨 완료")

    def _roll_selected_slot(self) -> None:
        if self.gold < 10000:
            self._push_log("단일 슬롯 인챈트 비용(10000G) 부족")
            return
        self.gold -= 10000
        self.enchant_slots[self.selected_slot] = self._roll_enchant_slot()
        self._push_log(f"슬롯 {self.selected_slot + 1} 인챈트 재추첨 완료")

    def _cast_spell(self, chance: float, gain_percent: float) -> None:
        if self.spell_attempts_used >= 10:
            self._push_log("주문 횟수 초과! 초기화가 필요합니다.")
            return
        if self.gold < 10000:
            self._push_log("주문 비용(10000G) 부족")
            return

        self.gold -= 10000
        self.spell_attempts_used += 1

        if random.random() * 100.0 < chance:
            self.spell_bonus_percent += gain_percent
            self._push_log(f"주문 성공! 초당 골드 +{gain_percent:.0f}%")
        else:
            self._push_log("주문 실패... (횟수 차감)")

    def _reset_spells(self) -> None:
        if self.gold < 100000:
            self._push_log("주문 초기화 비용(100000G) 부족")
            return
        self.gold -= 100000
        self.spell_attempts_used = 0
        self.spell_bonus_percent = 0.0
        self._push_log("주문 초기화 완료: 주문 효과 제거 / 횟수 0회")

    def _handle_clicks(self) -> None:
        if not Rs.userJustLeftClicked():
            return

        mouse = Rs.mousePos().toTuple()

        for i, rect in enumerate(self.slot_buttons):
            if rect.collidepoint(mouse):
                self.selected_slot = i
                self._push_log(f"인챈트 슬롯 {i + 1} 선택")
                return

        if self.buttons["enhance"].collidepoint(mouse):
            self._try_enhance()
        elif self.buttons["protect"].collidepoint(mouse):
            self.protect_destroy = not self.protect_destroy
            state = "ON" if self.protect_destroy else "OFF"
            self._push_log(f"파괴 방지 {state}")
        elif self.buttons["roll_all"].collidepoint(mouse):
            self._roll_all_slots()
        elif self.buttons["roll_one"].collidepoint(mouse):
            self._roll_selected_slot()
        elif self.buttons["spell_10"].collidepoint(mouse):
            self._cast_spell(10.0, 100.0)
        elif self.buttons["spell_50"].collidepoint(mouse):
            self._cast_spell(50.0, 10.0)
        elif self.buttons["spell_reset"].collidepoint(mouse):
            self._reset_spells()

    def _draw_button(self, rect: pygame.Rect, label: str, color: tuple[int, int, int]) -> None:
        hovered = rect.collidepoint(Rs.mousePos().toTuple())
        draw_color = Cs.light(color) if hovered else color
        button_rect = rectObj(rect, color=draw_color, edge=3, radius=12)
        button_rect.edgeColor = Cs.black
        button_rect.draw()
        label_obj = textObj(label, size=22, color=Cs.white)
        label_obj.center = RPoint(rect.center)
        label_obj.draw()

    def update(self):
        now = time.time()
        delta = max(0.0, now - self.last_update_time)
        self.last_update_time = now

        self.second_accumulator += delta
        while self.second_accumulator >= 1.0:
            self._produce_gold_for_one_second()
            self.second_accumulator -= 1.0

        self._handle_clicks()

        bonus = self._total_enchant_bonus()
        current_cost = self._enhance_cost() * (3 if self.protect_destroy else 1)

        self.info_text.text = (
            f"보유 골드: {self.gold:,.1f}G\n"
            f"강화 레벨: +{self.enhance_level} | 강화 비용: {current_cost:,}G\n"
            f"기본 강화 성공률: {self._base_success_chance():.1f}% + 인챈트 {bonus['success_pct']:.1f}%\n"
            f"파괴 확률(10렙+): {self._destroy_chance():.1f}% | 파괴방지: {'ON(비용x3)' if self.protect_destroy else 'OFF'}\n"
            f"기대 초당 골드: {self._gold_per_second_preview():.1f}\n"
            f"주문 시도: {self.spell_attempts_used}/10 | 주문 누적 보너스: +{self.spell_bonus_percent:.1f}%"
        )

        slot_lines = []
        for i, slot in enumerate(self.enchant_slots):
            marker = "▶" if i == self.selected_slot else " "
            slot_lines.append(f"{marker} 슬롯{i+1} | {slot['label']} +{float(slot['value']):.1f}%")

        slot_total = (
            f"합계(캡 적용): 골드+{bonus['gold_pct']:.1f}% / 크리골드+{bonus['crit_gold_pct']:.1f}% / "
            f"강화성공+{bonus['success_pct']:.1f}% / 크리확률+{bonus['crit_chance_pct']:.1f}%"
        )
        self.enchant_text.text = "\n".join(slot_lines + ["", slot_total])

    def draw(self):
        Rs.fillScreen((16, 20, 30))
        self.left_panel.draw()
        self.right_panel.draw()

        self.title.draw()
        self.subtitle.draw()
        self.info_text.draw()
        self.enchant_text.draw()

        self._draw_button(self.buttons["enhance"], "깡 강화", Cs.dark(Cs.orange))
        protect_label = "파괴 방지: ON" if self.protect_destroy else "파괴 방지: OFF"
        self._draw_button(self.buttons["protect"], protect_label, Cs.dark(Cs.teal))

        for i, rect in enumerate(self.slot_buttons):
            color = Cs.dark(Cs.tomato) if i == self.selected_slot else Cs.dark(Cs.steelblue)
            self._draw_button(rect, f"슬롯 {i+1}", color)

        self._draw_button(self.buttons["roll_all"], "5슬롯 전체 인챈트 (1000G)", Cs.dark(Cs.purple))
        self._draw_button(self.buttons["roll_one"], "선택 슬롯 인챈트 (10000G)", Cs.dark(Cs.rebeccapurple))

        self._draw_button(self.buttons["spell_10"], "10% 주문 (+100%)", Cs.dark(Cs.darkgreen))
        self._draw_button(self.buttons["spell_50"], "50% 주문 (+10%)", Cs.dark(Cs.forestgreen))
        self._draw_button(self.buttons["spell_reset"], "주문 초기화 (100000G)", Cs.dark(Cs.firebrick))

        log_title = textObj("최근 로그", pos=(1170, 130), size=28, color=Cs.light(Cs.gold))
        log_title.draw()
        self.log_text.draw()


class Scenes:
    mainScene = IdleMiningScene()


if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920, 1080), screen_size=(1920, 1080), fullscreen=False, caption="REMO Idle Mining")
    window.setCurrentScene(Scenes.mainScene)
    window.run()
