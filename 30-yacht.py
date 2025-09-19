from REMOLib import *
import random


class mainScene(Scene):
    def initOnce(self):
        self.background = rectObj(pygame.Rect(0, 0, 1280, 720), color=Cs.darkslategray)

        self.title = textObj("야추 로그라이크", pos=(120, 60), size=64, color=Cs.white)
        self.subtitle = textObj(
            "주사위 조합으로 피해를 주고 몬스터를 물리치세요!",
            pos=(120, 120),
            size=28,
            color=Cs.lightgrey,
        )

        self.rollInfo = textObj("남은 굴림: 3", pos=(120, 170), size=32, color=Cs.white)
        self.goldLabel = textObj("보유 골드: 0", pos=(120, 210), size=32, color=Cs.gold)

        self.dice_values = [1 for _ in range(5)]
        self.hold_flags = [False for _ in range(5)]

        self.dice_buttons = []
        base_x = 120
        for idx in range(5):
            rect = pygame.Rect(base_x + idx * 140, 240, 120, 120)
            button = textButton("1", rect, size=48, radius=24, color=Cs.dark(Cs.blue))
            button.textColor = Cs.white
            button.connect(lambda index=idx: self.toggleHold(index))
            self.dice_buttons.append(button)

        self.rollButton = textButton(
            "주사위 굴리기",
            pygame.Rect(120, 390, 260, 70),
            size=32,
            radius=20,
            color=Cs.orange,
            textColor=Cs.black,
        )
        self.rollButton.connect(self.rollDice)

        self.resetButton = textButton(
            "새 모험",
            pygame.Rect(400, 390, 180, 70),
            size=32,
            radius=20,
            color=Cs.mint,
            textColor=Cs.black,
        )
        self.resetButton.connect(self.resetGame)

        self.logPanel = longTextObj(
            "주사위를 굴려 공격 타이밍을 노리세요.",
            pos=(120, 490),
            size=26,
            textWidth=520,
            color=Cs.white,
        )

        panel_rect = pygame.Rect(780, 60, 380, 600)
        self.scorePanel = rectObj(panel_rect, color=Cs.dark(Cs.grey), radius=24, alpha=220)
        self.scoreTitle = textObj("공격 패턴", pos=(panel_rect.x + 30, panel_rect.y + 20), size=40, color=Cs.white)
        self.stageLabel = textObj("스테이지 1", pos=(panel_rect.x + 30, panel_rect.y + 80), size=30, color=Cs.white)
        self.playerHPLabel = textObj(
            "플레이어 HP: 100/100", pos=(panel_rect.x + 30, panel_rect.y + 120), size=30, color=Cs.white
        )
        self.enemyHPLabel = textObj(
            "적 HP: 0/0", pos=(panel_rect.x + 30, panel_rect.y + 160), size=30, color=Cs.white
        )

        self.categories = [
            ("에이스 (1)", lambda dice: self.score_numbers(dice, 1)),
            ("듀스 (2)", lambda dice: self.score_numbers(dice, 2)),
            ("트레이 (3)", lambda dice: self.score_numbers(dice, 3)),
            ("포 (4)", lambda dice: self.score_numbers(dice, 4)),
            ("파이브 (5)", lambda dice: self.score_numbers(dice, 5)),
            ("식스 (6)", lambda dice: self.score_numbers(dice, 6)),
            ("초이스", self.score_choice),
            ("포카드", self.score_four_of_a_kind),
            ("풀 하우스", self.score_full_house),
            ("스몰 스트레이트", self.score_small_straight),
            ("라지 스트레이트", self.score_large_straight),
            ("야추", self.score_yacht),
        ]

        self.category_buttons = {}
        pattern_top = panel_rect.y + 170
        pattern_spacing = 36
        pattern_height = 32
        for idx, (name, _) in enumerate(self.categories):
            rect = pygame.Rect(
                panel_rect.x + 20,
                pattern_top + idx * pattern_spacing,
                panel_rect.w - 40,
                pattern_height,
            )
            button = textButton(f"{name}: -", rect, size=20, radius=12, color=Cs.dark(Cs.grey))
            button.textColor = Cs.white
            button.connect(self.makeScoreHandler(name))
            self.category_buttons[name] = button

        self.rolls_left = 3
        self.hasRolled = False
        self.playerTurn = True
        self.gameOver = False
        self.gold = 0
        self.bonusDamage = 0
        self.used_categories = set()

        self.logLines = ["야추 주사위로 적과 싸우는 모험을 시작합니다!"]
        self.updateLog()

        self.resetGame(initial=True)
        return

    def init(self):
        return

    def score_numbers(self, dice, target):
        return sum(value for value in dice if value == target)

    def score_choice(self, dice):
        return sum(dice)

    def score_four_of_a_kind(self, dice):
        for value in set(dice):
            if dice.count(value) >= 4:
                return sum(dice)
        return 0

    def score_full_house(self, dice):
        counts = sorted([dice.count(value) for value in set(dice)])
        return sum(dice) if counts == [2, 3] else 0

    def score_small_straight(self, dice):
        unique = sorted(set(dice))
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        for straight in straights:
            if straight.issubset(unique):
                return 15
        return 0

    def score_large_straight(self, dice):
        sorted_dice = sorted(dice)
        return 30 if sorted_dice == [1, 2, 3, 4, 5] or sorted_dice == [2, 3, 4, 5, 6] else 0

    def score_yacht(self, dice):
        return 50 if len(set(dice)) == 1 else 0

    def makeScoreHandler(self, name):
        def handler():
            if self.gameOver:
                self.addLog("게임이 종료되었습니다. 새 모험을 시작하세요.")
                return
            if not self.playerTurn:
                return
            if not self.hasRolled:
                self.addLog("먼저 주사위를 굴려 주세요!")
                return
            if name in self.used_categories:
                self.addLog("이미 사용한 공격 패턴입니다.")
                return

            score_func = dict(self.categories)[name]
            damage = score_func(self.dice_values)
            self.resolvePlayerAttack(name, damage)
            return

        return handler

    def updateRollInfo(self):
        self.rollInfo.text = f"남은 굴림: {self.rolls_left}"
        can_roll = not self.gameOver and self.rolls_left > 0
        self.rollButton.enabled = can_roll
        if not can_roll:
            self.rollButton.hideChilds(0)

    def updateDiceDisplay(self):
        for idx, button in enumerate(self.dice_buttons):
            button.text = str(self.dice_values[idx])
            if self.hold_flags[idx]:
                button.color = Cs.dark(Cs.green)
            else:
                button.color = Cs.dark(Cs.blue)

    def updatePotentialScores(self):
        category_dict = dict(self.categories)
        for name, button in self.category_buttons.items():
            if name in self.used_categories:
                button.text = f"{name}: 사용됨"
                button.enabled = False
                button.hideChilds(0)
                button.color = Cs.dark(Cs.grey)
                continue
            if self.hasRolled and self.playerTurn and not self.gameOver:
                potential = category_dict[name](self.dice_values)
                button.text = f"{name}: {potential} 대미지"
                button.enabled = True
                button.color = Cs.dark(Cs.tiffanyBlue)
            else:
                button.text = f"{name}: -"
                button.enabled = False
                button.hideChilds(0)
                button.color = Cs.dark(Cs.grey)

    def updateGoldLabel(self):
        self.goldLabel.text = f"보유 골드: {self.gold}"

    def resetGame(self, initial=False):
        self.playerMaxHP = 100
        self.playerHP = self.playerMaxHP
        self.stage = 1
        self.playerTurn = True
        self.gameOver = False
        self.dice_values = [1 for _ in range(5)]
        self.hold_flags = [False for _ in range(5)]
        self.rolls_left = 3
        self.hasRolled = False
        self.gold = 0
        self.bonusDamage = 0
        self.used_categories = set()
        if not initial:
            self.logLines = []
            self.addLog("새로운 모험이 시작되었습니다!")
        self.spawnEnemy()
        self.updatePlayerHPLabel()
        self.updateRollInfo()
        self.updateDiceDisplay()
        self.updatePotentialScores()
        self.updateGoldLabel()
        return

    def spawnEnemy(self):
        base_hp = 40 + (self.stage - 1) * 15
        self.enemyMaxHP = base_hp
        self.enemyHP = base_hp
        self.enemyName = f"심연의 주사위 {self.stage}단계"
        self.stageLabel.text = f"스테이지 {self.stage}"
        self.updateEnemyHPLabel()
        self.addLog(f"{self.enemyName}이(가) 나타났다!")
        self.preparePlayerTurn()

    def preparePlayerTurn(self, reset_log=True):
        self.playerTurn = True
        self.rolls_left = 3
        self.hasRolled = False
        self.dice_values = [1 for _ in range(5)]
        self.hold_flags = [False for _ in range(5)]
        self.updateRollInfo()
        self.updateDiceDisplay()
        self.updatePotentialScores()
        if reset_log:
            self.addLog("주사위를 굴려 공격할 차례입니다!")

    def resolvePlayerAttack(self, name, damage):
        button = self.category_buttons[name]
        button.enabled = False
        button.hideChilds(0)
        button.color = Cs.dark(Cs.grey)
        self.used_categories.add(name)
        self.playerTurn = False
        self.rolls_left = 0
        self.hasRolled = False
        self.updateRollInfo()
        self.updatePotentialScores()

        if self.bonusDamage > 0 and damage > 0:
            damage += self.bonusDamage
            self.addLog(f"추가 피해 {self.bonusDamage}가 적용되었습니다!")
            self.bonusDamage = 0

        if damage <= 0:
            self.addLog(f"{name} 조합이 실패하여 피해를 주지 못했습니다...")
        else:
            self.enemyHP = max(0, self.enemyHP - damage)
            self.updateEnemyHPLabel()
            self.addLog(f"{name}으로(로) {damage} 피해!")

        if self.enemyHP <= 0:
            self.handleEnemyDefeated()
            return

        self.enemyTurn()

    def handleEnemyDefeated(self):
        self.addLog(f"{self.enemyName}을(를) 물리쳤습니다!")
        reward = 30 + (self.stage - 1) * 10
        self.gold += reward
        self.updateGoldLabel()
        self.addLog(f"전리품으로 {reward} 골드를 획득했습니다.")
        self.stage += 1
        Scenes.shopScene.open_shop(self)

    def rollDice(self):
        if self.gameOver:
            self.addLog("게임이 종료되었습니다. 새 모험을 시작하세요.")
            return
        if self.rolls_left <= 0:
            self.addLog("이번 턴에는 더 이상 주사위를 굴릴 수 없습니다. 공격 패턴을 선택하세요.")
            return
        if not self.playerTurn:
            return

        for idx, hold in enumerate(self.hold_flags):
            if not hold:
                self.dice_values[idx] = random.randint(1, 6)
        self.rolls_left -= 1
        self.hasRolled = True
        self.addLog("보류할 주사위를 고른 뒤 공격 패턴을 선택하세요.")
        self.updateDiceDisplay()
        self.updateRollInfo()
        self.updatePotentialScores()
        return

    def toggleHold(self, index):
        if self.gameOver:
            self.addLog("게임이 종료되었습니다. 새 모험을 시작하세요.")
            return
        if not self.playerTurn:
            return
        if not self.hasRolled:
            self.addLog("주사위를 굴린 뒤에 보류할 수 있습니다.")
            return

        self.hold_flags[index] = not self.hold_flags[index]
        self.updateDiceDisplay()
        return

    def enemyTurn(self):
        if self.gameOver:
            return

        dice = [random.randint(1, 6) for _ in range(5)]
        best_name, best_damage = self.evaluateEnemyAttack(dice)
        damage_multiplier = 1 + (self.stage - 1) * 0.1
        total_damage = int(best_damage * damage_multiplier)

        if total_damage <= 0:
            self.addLog(f"{self.enemyName}의 공격이 빗나갔습니다!")
        else:
            self.playerHP = max(0, self.playerHP - total_damage)
            self.updatePlayerHPLabel()
            self.addLog(
                f"{self.enemyName}이(가) {best_name}으로(로) {total_damage} 피해를 가했습니다!"
            )

        if self.playerHP <= 0:
            self.gameOver = True
            self.playerTurn = False
            self.addLog("당신은 쓰러졌습니다... 새 모험으로 재도전하세요.")
            self.rollButton.enabled = False
            self.rollButton.hideChilds(0)
            for button in self.category_buttons.values():
                button.enabled = False
                button.hideChilds(0)
                button.color = Cs.dark(Cs.grey)
            return

        self.preparePlayerTurn()

    def evaluateEnemyAttack(self, dice):
        category_dict = dict(self.categories)
        results = []
        for name, func in category_dict.items():
            if callable(func):
                results.append((name, func(dice)))
        results.sort(key=lambda item: item[1], reverse=True)
        best_name, best_damage = results[0]
        return best_name, best_damage

    def updatePlayerHPLabel(self):
        self.playerHPLabel.text = f"플레이어 HP: {self.playerHP}/{self.playerMaxHP}"

    def updateEnemyHPLabel(self):
        self.enemyHPLabel.text = f"적 HP: {self.enemyHP}/{self.enemyMaxHP}"

    def healPlayer(self, amount):
        if self.playerHP >= self.playerMaxHP:
            return False
        self.playerHP = min(self.playerMaxHP, self.playerHP + amount)
        self.updatePlayerHPLabel()
        return True

    def increaseMaxHP(self, amount):
        self.playerMaxHP += amount
        self.playerHP += amount
        self.updatePlayerHPLabel()
        return True

    def grantBonusDamage(self, amount):
        self.bonusDamage += amount
        return True

    def startNextStage(self):
        self.addLog("상점을 떠나 새로운 전투를 준비합니다.")
        self.spawnEnemy()

    def updateLog(self):
        self.logPanel.text = "\n".join(self.logLines[-6:])

    def addLog(self, text):
        self.logLines.append(text)
        self.updateLog()

    def update(self):
        self.rollButton.update()
        self.resetButton.update()
        for button in self.dice_buttons:
            button.update()
        for button in self.category_buttons.values():
            if button.enabled:
                button.update()
        return

    def draw(self):
        Rs.fillScreen(Cs.darkslategray)
        self.background.draw()
        self.title.draw()
        self.subtitle.draw()
        self.rollInfo.draw()
        for button in self.dice_buttons:
            button.draw()
        self.rollButton.draw()
        self.resetButton.draw()
        self.logPanel.draw()
        self.goldLabel.draw()
        self.scorePanel.draw()
        self.scoreTitle.draw()
        self.stageLabel.draw()
        self.playerHPLabel.draw()
        self.enemyHPLabel.draw()
        for button in self.category_buttons.values():
            button.draw()
        return


class shopScene(Scene):
    def initOnce(self):
        self.background = rectObj(pygame.Rect(0, 0, 1280, 720), color=Cs.darkslateblue)
        self.title = textObj("여행 상점", pos=(80, 60), size=64, color=Cs.white)
        self.subtitle = longTextObj(
            "전투에서 얻은 골드로 장비를 강화하세요!",
            pos=(80, 140),
            size=28,
            textWidth=520,
            color=Cs.lightgrey,
        )
        self.goldLabel = textObj("보유 골드: 0", pos=(80, 200), size=36, color=Cs.gold)
        self.stageLabel = textObj("다음 스테이지", pos=(80, 250), size=32, color=Cs.white)

        self.items = [
            {
                "name": "회복 물약 (+30 HP)",
                "cost": 40,
                "description": "플레이어의 체력을 30 회복합니다.",
                "effect": lambda main: main.healPlayer(30),
            },
            {
                "name": "강화 갑옷 (최대 HP +10)",
                "cost": 50,
                "description": "최대 체력을 10 올리고 현재 체력도 함께 증가합니다.",
                "effect": lambda main: main.increaseMaxHP(10),
            },
            {
                "name": "힘의 주문 (다음 공격 +15)",
                "cost": 45,
                "description": "다음 번 공격에 15의 추가 피해를 부여합니다.",
                "effect": lambda main: main.grantBonusDamage(15),
            },
        ]

        self.item_buttons = []
        for idx, _ in enumerate(self.items):
            rect = pygame.Rect(80, 300 + idx * 100, 520, 80)
            button = textButton(self.items[idx]["name"], rect, size=28, radius=24, color=Cs.dark(Cs.orange))
            button.connect(self.makePurchaseHandler(idx))
            self.item_buttons.append(button)

        self.infoBox = longTextObj(
            "각 장비는 한 번만 구매할 수 있습니다.",
            pos=(700, 200),
            size=26,
            textWidth=460,
            color=Cs.white,
        )
        self.messageBox = longTextObj("", pos=(700, 320), size=26, textWidth=460, color=Cs.white)
        self.continueButton = textButton(
            "다음 전투로",
            pygame.Rect(700, 520, 360, 90),
            size=36,
            radius=28,
            color=Cs.green,
            textColor=Cs.black,
        )
        self.continueButton.connect(self.leaveShop)

        self.purchased = set()
        self.main_scene = None

    def init(self):
        return

    def open_shop(self, main_scene):
        self.main_scene = main_scene
        self.purchased = set()
        REMOGame.setCurrentScene(self)
        self.messageBox.text = "적을 물리치고 잠시 쉬어갈 시간입니다."
        self.updateGoldLabel()
        self.updateStageLabel()
        self.refreshButtons()

    def makePurchaseHandler(self, index):
        def handler():
            if self.main_scene is None:
                return
            item = self.items[index]
            if index in self.purchased:
                self.messageBox.text = f"이미 구매한 장비입니다.\n{item['description']}"
                return
            if self.main_scene.gold < item["cost"]:
                self.messageBox.text = f"골드가 부족합니다!\n{item['description']}"
                return

            success = item["effect"](self.main_scene)
            if not success:
                self.messageBox.text = f"지금은 효과가 없습니다.\n{item['description']}"
                return

            self.main_scene.gold -= item["cost"]
            self.main_scene.updateGoldLabel()
            self.updateGoldLabel()
            self.purchased.add(index)
            self.messageBox.text = f"{item['name']}을 구매했습니다!"
            self.main_scene.addLog(f"상점에서 {item['name']}을 구매했습니다.")
            self.refreshButtons()

        return handler

    def refreshButtons(self):
        if self.main_scene is None:
            return
        for idx, button in enumerate(self.item_buttons):
            item = self.items[idx]
            status = ""
            if idx in self.purchased:
                status = " (구매 완료)"
            elif self.main_scene.gold < item["cost"]:
                status = " (골드 부족)"
            button.text = f"{item['name']} - {item['cost']}G{status}"
            can_buy = idx not in self.purchased and self.main_scene.gold >= item["cost"]
            button.enabled = can_buy
            if not can_buy:
                button.color = Cs.dark(Cs.grey)
                button.hideChilds(0)
            else:
                button.color = Cs.dark(Cs.orange)

    def updateGoldLabel(self):
        if self.main_scene is None:
            self.goldLabel.text = "보유 골드: 0"
        else:
            self.goldLabel.text = f"보유 골드: {self.main_scene.gold}"

    def updateStageLabel(self):
        if self.main_scene is None:
            self.stageLabel.text = "다음 스테이지"
        else:
            self.stageLabel.text = f"다음 스테이지: {self.main_scene.stage}"

    def leaveShop(self):

        Scenes.mainScene.startNextStage()
        REMOGame.setCurrentScene(Scenes.mainScene, skipInit=True)

    def update(self):
        for button in self.item_buttons:
            button.update()
        self.continueButton.update()
        return

    def draw(self):
        Rs.fillScreen(Cs.darkslateblue)
        self.background.draw()
        self.title.draw()
        self.subtitle.draw()
        self.goldLabel.draw()
        self.stageLabel.draw()
        for button in self.item_buttons:
            button.draw()
        self.infoBox.draw()
        self.messageBox.draw()
        self.continueButton.draw()
        return


class Scenes:
    mainScene = mainScene()
    shopScene = shopScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="30. Yacht Dice",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
