from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    font_for_test = "unifont_script.ttf"
    None

class mainScene(Scene):
    def initOnce(self):
        test_text = "这是一段示例文本。昨日 の試験は非常に難解な漢字が 多くて、読解に苦労しました。 Test. 나는 유니코드야. 를를. As you know this is a simple test. Liberté"
        test_button_text = "这是非常Te나는"
        self.longText = longTextObj(test_text,font=Obj.font_for_test,textWidth=400)
        self.button = textButton(test_button_text,font=Obj.font_for_test)
        self.button.pos = RPoint(700,100)
        self.button2 = textButton("Game Start",font=Obj.font_for_test)
        self.button2.pos = RPoint(700,200)
        return
    def init(self):
        return
    def update(self):
        self.button.update()
        self.button2.update()
        return
    def draw(self):
        self.longText.draw()
        self.button.draw()
        self.button2.draw()
        return


class defaultScene(Scene):
    def initOnce(self):
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        return

class Scenes:
    mainScene = mainScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
