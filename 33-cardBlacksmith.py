from REMOLib import *
import random


RARITY_INFO = {
    "일반": {
        "color": Cs.lightsteelblue,
        "price_scale": 1.0,
        "power_scale": 1.0,
        "base_rate": 0.9,
    },
    "희귀": {
        "color": Cs.deepskyblue,
        "price_scale": 1.3,
        "power_scale": 1.2,
        "base_rate": 0.85,
    },
    "영웅": {
        "color": Cs.mediumorchid,
        "price_scale": 1.65,
        "power_scale": 1.4,
        "base_rate": 0.8,
    },
    "전설": {
        "color": Cs.gold,
        "price_scale": 2.2,
        "power_scale": 1.65,
        "base_rate": 0.75,
    },
}


CARD_LIBRARY = [
    {
        "name": "별빛 검",
        "tier": "희귀",
        "base_value": 120,
        "base_power": 18,
        "growth": 9,
        "description": "별빛을 머금은 검. 강화할수록 빛이 더 강렬해집니다.",
        "color": Cs.dark(Cs.steelblue),
        "max_level": 9,
    },
    {
        "name": "용비늘 방패",
        "tier": "영웅",
        "base_value": 160,
        "base_power": 24,
        "growth": 11,
        "description": "고대 용의 비늘로 만들어진 방패. 실패에도 쉽게 부서지지 않습니다.",
        "color": Cs.dark(Cs.sienna),
        "max_level": 8,
    },
    {
        "name": "폭풍 지팡이",
        "tier": "희귀",
        "base_value": 110,
        "base_power": 16,
        "growth": 10,
        "description": "바람과 번개의 정령이 깃든 지팡이. 강화를 통해 마력을 폭발시켜보세요.",
        "color": Cs.dark(Cs.teal),
        "max_level": 10,
    },
    {
        "name": "에메랄드 활",
        "tier": "일반",
        "base_value": 80,
        "base_power": 12,
        "growth": 7,
        "description": "숲의 정기를 담은 활. 안정적인 성공률을 자랑합니다.",
        "color": Cs.dark(Cs.seagreen),
        "max_level": 12,
    },
    {
        "name": "황혼 단검",
        "tier": "전설",
        "base_value": 220,
        "base_power": 28,
        "growth": 15,
        "description": "황혼의 그림자에서 벼려낸 단검. 위험하지만 가치가 매우 높습니다.",
        "color": Cs.dark(Cs.rebeccapurple),
        "max_level": 7,
    },
]


class ForgeCard(rectObj):
    WIDTH = 220
    HEIGHT = 320

    def __init__(self, template: dict, on_select: callable, *, selectable: bool = True) -> None:
        self.template = dict(template)
        self.on_select = on_select
        self.selectable = selectable
        self.rarity = RARITY_INFO[self.template["tier"]]
        base_color = self.template.get("color", Cs.dark(Cs.darkslategray))
        super().__init__(
            pygame.Rect(0, 0, self.WIDTH, self.HEIGHT),
            color=base_color,
            edge=6,
            radius=26,
        )
        self._base_color = base_color
        self._hover_color = Cs.light(base_color)
        self._selected_color = Cs.light(self.rarity["color"])
        self.level = int(self.template.get("level", 0))
        self.max_level = int(self.template.get("max_level", 10))
        self.selected = False

        self.selection_outline = rectObj(
            self.offsetRect.inflate(28, 28),
            color=Cs.light(self.rarity["color"]),
            edge=4,
            radius=self.radius + 12,
        )
        self.selection_outline.alpha = 0
        self.selection_outline.setParent(self, depth=-2)
        self.selection_outline.center = self.offsetRect.center

        self.title_text = textObj(self.template["name"], size=28, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 24)

        self.tier_text = textObj(self.template["tier"], size=22, color=self.rarity["color"])
        self.tier_text.setParent(self, depth=1)
        self.tier_text.midtop = self.title_text.midbottom + RPoint(0, 8)

        self.level_text = textObj("", size=24, color=Cs.yellow)
        self.level_text.setParent(self, depth=1)
        self.level_text.midtop = self.tier_text.midbottom + RPoint(0, 18)

        self.power_text = textObj("", size=24, color=Cs.light(Cs.orangered))
        self.power_text.setParent(self, depth=1)
        self.power_text.midtop = self.level_text.midbottom + RPoint(0, 18)

        self.value_text = textObj("", size=22, color=Cs.light(Cs.gold))
        self.value_text.setParent(self, depth=1)
        self.value_text.midtop = self.power_text.midbottom + RPoint(0, 16)

        self.detail_text = longTextObj(
            "",
            pos=RPoint(24, self.offsetRect.h - 116),
            size=20,
            color=Cs.white,
            textWidth=self.offsetRect.w - 48,
        )
        self.detail_text.setParent(self, depth=1)

        if not self.selectable:
            self.selection_outline.alpha = 0

        self.refresh()

    def set_selectable(self, selectable: bool) -> None:
        self.selectable = selectable
        if not selectable and self.selected:
            self.set_selected(False)

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        self.selection_outline.alpha = 120 if selected else 0

    def can_upgrade(self) -> bool:
        return self.level < self.max_level

    def get_success_rate(self) -> float:
        if not self.can_upgrade():
            return 0.0
        base = self.rarity["base_rate"]
        penalty = 0.11 * self.level
        return max(0.18, base - penalty)

    def get_upgrade_cost(self) -> int:
        if not self.can_upgrade():
            return 0
        base = self.template["base_value"] * self.rarity["price_scale"]
        growth = 0.55 + 0.45 * self.level
        return int(base * (0.6 + growth))

    def get_sell_price(self) -> int:
        base = self.template["base_value"] * self.rarity["price_scale"]
        bonus = 0.95 + self.level * 0.65
        return int(base * (0.85 + bonus))

    def power_value(self) -> int:
        base = self.template["base_power"] * self.rarity["power_scale"]
        growth = self.template["growth"] * (0.5 + 0.5 * self.rarity["power_scale"])
        return int(base + self.level * growth)

    def refresh(self) -> None:
        self.level_text.text = f"강화 단계 +{self.level} / 최대 {self.max_level}"
        self.power_text.text = f"전투력 {self.power_value()}"
        self.value_text.text = f"판매가 {self.get_sell_price()}G"
        if self.can_upgrade():
            rate = int(self.get_success_rate() * 100)
            cost = self.get_upgrade_cost()
            self.detail_text.text = (
                f"다음 강화 비용 {cost}G / 성공률 {rate}%\n{self.template['description']}"
            )
        else:
            self.detail_text.text = f"이미 최대 강화 단계입니다.\n{self.template['description']}"

    def get_summary(self) -> str:
        lines = [
            f"{self.template['name']} (+{self.level})", 
            f"전투력 {self.power_value()} | 판매가 {self.get_sell_price()}G",
        ]
        if self.can_upgrade():
            lines.append(
                f"다음 강화: {self.get_upgrade_cost()}G / 성공률 {int(self.get_success_rate() * 100)}%"
            )
        else:
            lines.append("이미 최대 강화에 도달했습니다.")
        lines.append(self.template["description"])
        return "\n".join(lines)

    def update(self) -> None:
        hovered = self.collideMouse()
        if self.selected:
            target = self._selected_color
        elif hovered:
            target = self._hover_color
        else:
            target = self._base_color
        if self.color != target:
            self.color = target
        if hovered and self.selectable and Rs.userJustLeftClicked():
            self.on_select(self)


class BlacksmithScene(Scene):
    def initOnce(self) -> None:
        self.coins = 260
        self.inventory_cards: list[ForgeCard] = []
        self.selected_card: ForgeCard | None = None
        self.total_profit = 0
        self.best_sale_value = 0
        self.upgrade_attempts = 0
        self.upgrade_success = 0
        self.restock_price = 25
        self.current_offer: dict | None = None
        self.offer_card: ForgeCard | None = None

        self.background = rectObj(pygame.Rect(0, 0, 1920, 1080), color=Cs.dark(Cs.darkslategray))

        self.title_text = textObj("별의 대장간", pos=RPoint(60, 36), size=52, color=Cs.white)
        self.subtitle = textObj(
            "카드를 사서 강화하고, 최고의 가치를 노려보세요!",
            pos=RPoint(60, 104),
            size=28,
            color=Cs.grey75,
        )

        self.status_labels: list[textObj] = []
        self.status_origin = RPoint(60, 154)
        self.status_spacing = 28
        self.gold_text = textObj("", size=32, color=Cs.gold)
        self.inventory_count_text = textObj("", size=30, color=Cs.white)
        self.profit_text = textObj("", size=30, color=Cs.light(Cs.mint))
        self.success_text = textObj("", size=30, color=Cs.light(Cs.orange))
        self.best_sale_text = textObj("", size=30, color=Cs.light(Cs.skyblue))
        self.status_labels.extend(
            (
                self.gold_text,
                self.inventory_count_text,
                self.profit_text,
                self.success_text,
                self.best_sale_text,
            )
        )

        panel_rect = pygame.Rect(40, 220, 1140, 820)
        self.inventory_panel = rectObj(panel_rect, color=Cs.dark(Cs.darkslategray), edge=6, radius=32, alpha=220)
        self.inventory_title = textObj("보유 카드", pos=self.inventory_panel.pos + RPoint(28, 24), size=38, color=Cs.white)
        self.inventory_hint = longTextObj(
            "카드를 클릭하면 강화와 판매 버튼이 활성화됩니다. 성공 확률과 비용을 잘 살펴보세요!",
            pos=self.inventory_panel.pos + RPoint(28, 74),
            size=22,
            color=Cs.grey75,
            textWidth=self.inventory_panel.rect.w - 56,
        )

        self.inventory_layout = cardLayout(
            RPoint(self.inventory_panel.rect.x + 32, self.inventory_panel.rect.y + 160),
            spacing=28,
            maxWidth=self.inventory_panel.rect.w - 64,
            isVertical=False,
        )

        shop_rect = pygame.Rect(1220, 80, 560, 340)
        self.shop_panel = rectObj(shop_rect, color=Cs.dark(Cs.darkslategray), edge=6, radius=32, alpha=230)
        self.shop_title = textObj("신규 카드 제안", size=34, color=Cs.white)
        self.shop_title.setParent(self.shop_panel)
        self.shop_title.pos = RPoint(28, 26)
        self.offer_desc = longTextObj("", pos=RPoint(28, 90), size=22, color=Cs.white, textWidth=240)
        self.offer_desc.setParent(self.shop_panel, depth=1)
        self.offer_price_text = textObj("", size=24, color=Cs.yellow)
        self.offer_price_text.setParent(self.shop_panel, depth=1)
        self.offer_price_text.pos = RPoint(28, 210)
        self.offer_rate_text = textObj("", size=22, color=Cs.light(Cs.skyblue))
        self.offer_rate_text.setParent(self.shop_panel, depth=1)
        self.offer_rate_text.pos = RPoint(28, 244)

        self.buy_button = textButton("카드 구매", pygame.Rect(0, 0, 260, 64), color=Cs.mint, textColor=Cs.black)
        self.buy_button.setParent(self.shop_panel, depth=1)
        self.buy_button.pos = RPoint(28, self.shop_panel.offsetRect.h - 84)
        self.buy_button.connect(self.buy_offer)

        self.refresh_button = textButton(
            "제안 갱신", pygame.Rect(0, 0, 220, 64), color=Cs.dark(Cs.deepskyblue), textColor=Cs.white
        )
        self.refresh_button.setParent(self.shop_panel, depth=1)
        self.refresh_button.pos = RPoint(self.shop_panel.offsetRect.w - self.refresh_button.offsetRect.w - 28, self.shop_panel.offsetRect.h - 84)
        self.refresh_button.connect(self.refresh_offer)

        detail_rect = pygame.Rect(1220, 440, 560, 300)
        self.detail_panel = rectObj(detail_rect, color=Cs.dark(Cs.darkslategray), edge=6, radius=28, alpha=230)
        self.detail_title = textObj("선택된 카드", size=32, color=Cs.white)
        self.detail_title.setParent(self.detail_panel)
        self.detail_title.pos = RPoint(28, 24)
        self.detail_text = longTextObj(
            "카드를 선택하면 상세 정보가 표시됩니다.",
            pos=RPoint(28, 80),
            size=22,
            color=Cs.white,
            textWidth=self.detail_panel.offsetRect.w - 56,
        )
        self.detail_text.setParent(self.detail_panel, depth=1)

        self.upgrade_button = textButton("강화", pygame.Rect(0, 0, 240, 64), color=Cs.orange, textColor=Cs.black)
        self.upgrade_button.setParent(self.detail_panel, depth=1)
        self.upgrade_button.pos = RPoint(28, self.detail_panel.offsetRect.h - 84)
        self.upgrade_button.connect(self.upgrade_selected_card)

        self.sell_button = textButton("판매", pygame.Rect(0, 0, 240, 64), color=Cs.dark(Cs.limegreen), textColor=Cs.black)
        self.sell_button.setParent(self.detail_panel, depth=1)
        self.sell_button.pos = RPoint(
            self.detail_panel.offsetRect.w - self.sell_button.offsetRect.w - 28,
            self.detail_panel.offsetRect.h - 84,
        )
        self.sell_button.connect(self.sell_selected_card)

        log_rect = pygame.Rect(1220, 780, 560, 260)
        self.log_panel = rectObj(log_rect, color=Cs.dark(Cs.darkslategray), edge=4, radius=24, alpha=220)
        self.log_title = textObj("대장간 기록", size=30, color=Cs.white)
        self.log_title.setParent(self.log_panel)
        self.log_title.pos = RPoint(28, 24)
        self.log_box = longTextObj("", pos=RPoint(28, 80), size=22, color=Cs.white, textWidth=self.log_panel.offsetRect.w - 56)
        self.log_box.setParent(self.log_panel, depth=1)
        self.hotkey_text = longTextObj(
            "단축키: B=구매 / U=강화 / S=판매 / R=제안 갱신",
            pos=RPoint(28, self.log_panel.offsetRect.h - 56),
            size=20,
            color=Cs.grey75,
            textWidth=self.log_panel.offsetRect.w - 56,
        )
        self.hotkey_text.setParent(self.log_panel, depth=1)

        self.log_lines: list[str] = []

        self._refresh_status()
        self._refresh_selected_detail()
        self._roll_offer()
        self._log("별의 대장간에 오신 것을 환영합니다. 신규 카드를 살펴보세요!")

    def init(self) -> None:
        return

    def _refresh_status(self) -> None:
        self.gold_text.text = f"보유 골드: {self.coins}G"
        self.inventory_count_text.text = f"보유 카드: {len(self.inventory_cards)}장"
        self.profit_text.text = f"누적 수익: {self.total_profit}G"
        if self.upgrade_attempts:
            rate = int((self.upgrade_success / self.upgrade_attempts) * 100)
            self.success_text.text = f"강화 성공률: {self.upgrade_success}/{self.upgrade_attempts} ({rate}%)"
        else:
            self.success_text.text = "강화 성공률: -"
        self.best_sale_text.text = f"최고 판매가: {self.best_sale_value}G"
        self._layout_status_labels()

    def _layout_status_labels(self) -> None:
        x = self.status_origin.x
        y = self.status_origin.y
        for label in self.status_labels:
            label.pos = RPoint(x, y)
            x += label.rect.w + self.status_spacing

    def _refresh_selected_detail(self) -> None:
        if self.selected_card:
            summary = self.selected_card.get_summary()
            self.detail_text.text = summary
            if self.selected_card.can_upgrade():
                self.upgrade_button.text = f"강화 ({self.selected_card.get_upgrade_cost()}G)"
            else:
                self.upgrade_button.text = "강화 완료"
            self.sell_button.text = f"판매 ({self.selected_card.get_sell_price()}G)"
        else:
            self.detail_text.text = "카드를 선택하면 상세 정보가 표시됩니다."
            self.upgrade_button.text = "강화 (선택 없음)"
            self.sell_button.text = "판매 (선택 없음)"

    def _clone_template(self, template: dict) -> dict:
        new_template = dict(template)
        new_template.pop("level", None)
        return new_template

    def _on_card_selected(self, card: ForgeCard) -> None:
        if self.selected_card and self.selected_card is not card:
            self.selected_card.set_selected(False)
        self.selected_card = card
        if self.selected_card:
            self.selected_card.set_selected(True)
        self._refresh_selected_detail()

    def _log(self, message: str) -> None:
        self.log_lines.append(message)
        self.log_lines = self.log_lines[-8:]
        self.log_box.text = "\n".join(self.log_lines)

    def _roll_offer(self) -> None:
        template = random.choice(CARD_LIBRARY)
        rarity = RARITY_INFO[template["tier"]]
        base_price = template["base_value"] * rarity["price_scale"]
        modifier = random.uniform(0.85, 1.25)
        price = int(base_price * modifier)
        price = max(40, (price // 5) * 5)
        self.current_offer = {
            "template": self._clone_template(template),
            "price": price,
            "modifier": modifier,
        }

        if self.offer_card:
            self.offer_card.setParent(None)
            self.offer_card = None

        self.offer_card = ForgeCard(self.current_offer["template"], lambda card: None, selectable=False)
        self.offer_card.setParent(self.shop_panel, depth=0)
        self.offer_card.pos = RPoint(
            self.shop_panel.offsetRect.w - self.offer_card.offsetRect.w - 32,
            48,
        )
        self.offer_card.refresh()
        self.offer_card.set_selectable(False)
        self._refresh_offer_ui()

    def _refresh_offer_ui(self) -> None:
        if not self.current_offer or not self.offer_card:
            self.offer_desc.text = "현재 제안이 없습니다."
            self.offer_price_text.text = ""
            self.offer_rate_text.text = ""
            self.buy_button.text = "카드 구매"
            return
        template = self.current_offer["template"]
        price = self.current_offer["price"]
        self.offer_desc.text = template["description"]
        self.offer_price_text.text = f"구매가: {price}G"
        self.offer_rate_text.text = (
            f"기본 전투력 {self.offer_card.power_value()} / 예상 판매가 {self.offer_card.get_sell_price()}G"
        )
        self.buy_button.text = f"카드 구매 ({price}G)"
        self.refresh_button.text = f"제안 갱신 (-{self.restock_price}G)"

    def buy_offer(self) -> None:
        if not self.current_offer:
            self._log("구매할 카드 제안이 없습니다.")
            return
        price = self.current_offer["price"]
        if self.coins < price:
            self._log("골드가 부족합니다. 먼저 카드를 팔거나 강화에 성공해 보세요.")
            return
        self.coins -= price
        new_card = ForgeCard(self.current_offer["template"], self._on_card_selected)
        new_card.setParent(self.inventory_layout)
        self.inventory_cards.append(new_card)
        self.inventory_layout.adjustLayout()
        self._on_card_selected(new_card)
        self._log(f"'{new_card.template['name']}' 카드를 구매했습니다. 이제 강화해보세요!")
        self._refresh_status()
        self._roll_offer()

    def refresh_offer(self) -> None:
        if self.coins < self.restock_price:
            self._log("제안을 새로 고치기 위한 골드가 부족합니다.")
            return
        self.coins -= self.restock_price
        self._log("새로운 재료를 찾아 제안을 갱신했습니다.")
        self._refresh_status()
        self._roll_offer()

    def upgrade_selected_card(self) -> None:
        if not self.selected_card:
            self._log("먼저 카드를 선택하세요.")
            return
        if not self.selected_card.can_upgrade():
            self._log("이 카드는 이미 최대 강화 단계입니다.")
            return
        cost = self.selected_card.get_upgrade_cost()
        if self.coins < cost:
            self._log("강화 비용이 부족합니다. 다른 카드를 판매하거나 골드를 모으세요.")
            return
        self.coins -= cost
        self.upgrade_attempts += 1
        success = random.random() <= self.selected_card.get_success_rate()
        if success:
            self.selected_card.level += 1
            self.upgrade_success += 1
            self.selected_card.refresh()
            self._log(f"강화 성공! {self.selected_card.template['name']}이(가) +{self.selected_card.level}이 되었습니다.")
        else:
            if self.selected_card.level > 0:
                self.selected_card.level -= 1
                self._log("강화 실패! 카드의 강화 단계가 한 단계 하락했습니다.")
            else:
                self._log("강화 실패! 다행히 단계는 유지되었습니다.")
            self.selected_card.refresh()
        self._refresh_status()
        self._refresh_selected_detail()

    def sell_selected_card(self) -> None:
        if not self.selected_card:
            self._log("판매할 카드를 먼저 선택하세요.")
            return
        sell_price = self.selected_card.get_sell_price()
        self.coins += sell_price
        self.total_profit += sell_price
        self.best_sale_value = max(self.best_sale_value, sell_price)
        name = self.selected_card.template["name"]
        self.selected_card.setParent(None)
        self.inventory_cards.remove(self.selected_card)
        self.selected_card = None
        self.inventory_layout.adjustLayout()
        self._log(f"'{name}' 카드를 {sell_price}G에 판매했습니다.")
        self._refresh_status()
        self._refresh_selected_detail()

    def update(self) -> None:
        self.inventory_layout.adjustLayout()
        self.inventory_layout.update()
        if self.offer_card:
            self.offer_card.update()
        self.buy_button.update()
        self.refresh_button.update()
        self.upgrade_button.update()
        self.sell_button.update()

        if Rs.userJustPressed(pygame.K_b):
            self.buy_offer()
        if Rs.userJustPressed(pygame.K_u):
            self.upgrade_selected_card()
        if Rs.userJustPressed(pygame.K_s):
            self.sell_selected_card()
        if Rs.userJustPressed(pygame.K_r):
            self.refresh_offer()

    def draw(self) -> None:
        self.background.draw()
        self.title_text.draw()
        self.subtitle.draw()
        for label in self.status_labels:
            label.draw()
        self.inventory_panel.draw()
        self.inventory_title.draw()
        self.inventory_hint.draw()
        self.inventory_layout.draw()
        self.shop_panel.draw()
        self.detail_panel.draw()
        self.log_panel.draw()


class Scenes:
    mainScene = BlacksmithScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1920, 1080),
        screen_size=(1920, 1080),
        fullscreen=False,
        caption="카드 대장간",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
