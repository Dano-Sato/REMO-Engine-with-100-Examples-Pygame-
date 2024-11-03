from REMOLib import *
from fontTools.ttLib import TTFont





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    font_for_test = "korean_button.ttf"
    None

class mainScene(Scene):
    def initOnce(self):
        test_text = "这是一段示例文本。昨日 の試験は非常に難解な漢字が 多くて、読解に苦労しました。 Test. 나는 유니코드야. 를를. As you know this is a simple test. LibertéДобры дзень! مرحبا! 안녕하세요! สวัสดี! Bonjour! Hallo! Здравствуйте! مرحبا بك! नमस्ते! Χαίρετε! Olá!"
        self.longText = longTextObj(test_text,font=Obj.font_for_test,textWidth=400)
        self.buttonLayout = buttonLayout(["示例文本。に験は","Game Start","게임 시작","読解に苦労","示是非常Te나는","日本語","bertéДобры"],RPoint(500,100),font=Obj.font_for_test)

        return
    def init(self):
        return
    def update(self):
        self.buttonLayout.update()
        return
    def draw(self):
        self.longText.draw()
        self.buttonLayout.draw()
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
