from REMOLib import *
import random


class mainScene(Scene):
    def initOnce(self):
        self.background = rectObj(pygame.Rect(0, 0, 1280, 720), color=Cs.darkslategray)

        self.title = textObj("야추", pos=(120, 60), size=64, color=Cs.white)
        self.subtitle = textObj(
            "5개의 주사위를 굴려 최고의 조합을 완성하세요!",
            pos=(120, 120),
            size=28,
            color=Cs.lightgrey,
        )

        self.turnNumber = 1
        self.turnLabel = textObj("라운드 1 / 12", pos=(120, 170), size=32, color=Cs.white)
        self.rollInfo = textObj("남은 굴림: 3", pos=(120, 210), size=28, color=Cs.white)

        self.dice_values = [1 for _ in range(5)]
        self.hold_flags = [False for _ in range(5)]

        self.dice_buttons = []
        base_x = 120
        for idx in range(5):
            rect = pygame.Rect(base_x + idx * 140, 270, 120, 120)
            button = textButton("1", rect, size=48, radius=24, color=Cs.dark(Cs.blue))
            button.textColor = Cs.white
            button.connect(lambda index=idx: self.toggleHold(index))
            self.dice_buttons.append(button)

        self.rollButton = textButton(
            "주사위 굴리기", pygame.Rect(120, 420, 260, 70), size=32, radius=20, color=Cs.orange, textColor=Cs.black
        )
        self.rollButton.connect(self.rollDice)

        self.resetButton = textButton(
            "새 게임", pygame.Rect(400, 420, 180, 70), size=32, radius=20, color=Cs.mint, textColor=Cs.black
        )
        self.resetButton.connect(self.resetGame)

        self.statusLabel = longTextObj(
            "주사위를 굴린 뒤 보류할 주사위를 선택하고, 원하는 카테고리에 점수를 기록하세요.",
            pos=(120, 520),
            size=26,
            textWidth=520,
            color=Cs.white,
        )

        panel_rect = pygame.Rect(780, 60, 380, 600)
        self.scorePanel = rectObj(panel_rect, color=Cs.dark(Cs.grey), radius=24, alpha=220)
        self.scoreTitle = textObj("점수표", pos=(panel_rect.x + 30, panel_rect.y + 20), size=40, color=Cs.white)
        self.totalScore = 0
        self.totalLabel = textObj(
            "총점: 0", pos=(panel_rect.x + 30, panel_rect.bottom - 50), size=34, color=Cs.white
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

        self.category_scores = {name: None for name, _ in self.categories}
        self.category_buttons = {}
        for idx, (name, _) in enumerate(self.categories):
            rect = pygame.Rect(
                panel_rect.x + 20,
                panel_rect.y + 80 + idx * 42,
                panel_rect.w - 40,
                40,
            )
            button = textButton(f"{name}: -", rect, size=22, radius=14, color=Cs.dark(Cs.grey))
            button.textColor = Cs.white
            button.connect(self.makeScoreHandler(name))
            self.category_buttons[name] = button

        self.totalRounds = len(self.categories)
        self.rolls_left = 3
        self.hasRolled = False
        self.gameOver = False

        self.updateDiceDisplay()
        self.updateRollInfo()
        self.updatePotentialScores()
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
                self.statusLabel.text = "게임이 종료되었습니다. 새 게임을 시작하세요."
                return
            if self.category_scores[name] is not None:
                return
            if not self.hasRolled:
                self.statusLabel.text = "먼저 주사위를 굴려 주세요!"
                return

            score_func = dict(self.categories)[name]
            score = score_func(self.dice_values)
            self.category_scores[name] = score
            self.totalScore += score
            button = self.category_buttons[name]
            button.text = f"{name}: {score}"
            button.enabled = False
            button.hideChilds(0)
            button.color = Cs.dark(Cs.mint)

            self.statusLabel.text = f"{name}에 {score}점을 기록했습니다."
            self.updateTotalLabel()
            self.prepareNextRound()
            return

        return handler

    def prepareNextRound(self):
        finished = sum(1 for value in self.category_scores.values() if value is not None)
        if finished >= self.totalRounds:
            self.gameOver = True
            self.hasRolled = False
            self.rolls_left = 0
            self.updateRollInfo()
            self.statusLabel.text = f"모든 카테고리를 채웠습니다! 최종 점수: {self.totalScore}점"
            return

        self.turnNumber += 1
        self.hold_flags = [False for _ in range(5)]
        self.rolls_left = 3
        self.hasRolled = False
        self.updateTurnLabel()
        self.updateRollInfo()
        self.updateDiceDisplay()
        self.updatePotentialScores()
        self.statusLabel.text += " 다음 라운드를 시작하세요!"
        return

    def updateTurnLabel(self):
        self.turnLabel.text = f"라운드 {self.turnNumber} / {self.totalRounds}"

    def updateRollInfo(self):
        self.rollInfo.text = f"남은 굴림: {self.rolls_left}"
        can_roll = not self.gameOver and self.rolls_left > 0
        self.rollButton.enabled = can_roll
        if not can_roll:
            self.rollButton.hideChilds(0)

    def updateTotalLabel(self):
        self.totalLabel.text = f"총점: {self.totalScore}"

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
            score = self.category_scores[name]
            if score is None:
                if self.hasRolled:
                    potential = category_dict[name](self.dice_values)
                    button.text = f"{name}: {potential}"
                else:
                    button.text = f"{name}: -"
                button.enabled = self.hasRolled and not self.gameOver
                if not button.enabled:
                    button.hideChilds(0)
                if button.enabled:
                    button.color = Cs.dark(Cs.tiffanyBlue)
                else:
                    button.color = Cs.dark(Cs.grey)
            else:
                button.text = f"{name}: {score}"
                button.enabled = False
                button.hideChilds(0)
                button.color = Cs.dark(Cs.mint)

    def resetGame(self):
        self.turnNumber = 1
        self.totalScore = 0
        self.category_scores = {name: None for name, _ in self.categories}
        self.hold_flags = [False for _ in range(5)]
        self.dice_values = [1 for _ in range(5)]
        self.rolls_left = 3
        self.hasRolled = False
        self.gameOver = False
        self.statusLabel.text = "주사위를 굴린 뒤 보류할 주사위를 선택하고, 원하는 카테고리에 점수를 기록하세요."
        self.updateTurnLabel()
        self.updateRollInfo()
        self.updateTotalLabel()
        self.updateDiceDisplay()
        self.updatePotentialScores()
        return

    def rollDice(self):
        if self.gameOver:
            self.statusLabel.text = "게임이 종료되었습니다. 새 게임을 시작하세요."
            return
        if self.rolls_left <= 0:
            self.statusLabel.text = "이번 라운드에서 더 이상 주사위를 굴릴 수 없습니다. 점수를 선택하세요."
            return

        for idx, hold in enumerate(self.hold_flags):
            if not hold:
                self.dice_values[idx] = random.randint(1, 6)
        self.rolls_left -= 1
        self.hasRolled = True
        self.statusLabel.text = "보류할 주사위를 고른 뒤 점수를 결정하세요."
        self.updateDiceDisplay()
        self.updateRollInfo()
        self.updatePotentialScores()
        return

    def toggleHold(self, index):
        if self.gameOver:
            self.statusLabel.text = "게임이 종료되었습니다. 새 게임을 시작하세요."
            return
        if not self.hasRolled:
            self.statusLabel.text = "주사위를 굴린 뒤에 보류할 수 있습니다."
            return

        self.hold_flags[index] = not self.hold_flags[index]
        self.updateDiceDisplay()
        return

    def update(self):
        self.rollButton.update()
        self.resetButton.update()
        for button in self.dice_buttons:
            button.update()
        for name, button in self.category_buttons.items():
            if button.enabled:
                button.update()
        return

    def draw(self):
        Rs.fillScreen(Cs.darkslategray)
        self.background.draw()
        self.title.draw()
        self.subtitle.draw()
        self.turnLabel.draw()
        self.rollInfo.draw()
        for button in self.dice_buttons:
            button.draw()
        self.rollButton.draw()
        self.resetButton.draw()
        self.statusLabel.draw()
        self.scorePanel.draw()
        self.scoreTitle.draw()
        for button in self.category_buttons.values():
            button.draw()
        self.totalLabel.draw()
        return


class Scenes:
    mainScene = mainScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1280, 720),
        screen_size=(1280, 720),
        fullscreen=False,
        caption="30. Yacht Dice",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
