from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        texts = []
        for i in range(10):
            obj = textObj(f"text{i}")
            texts.append(obj)
        self.layout = layoutObj(pos=RPoint(100,100),childs=texts,spacing=15)

        self.button = textButton("TEST")
        self.button.pos = RPoint(300,100)

        self.bLayout = buttonLayout(["Game Start Start","Exit","C","D"],RPoint(600,100),buttonAlpha=255,spacing=15)
    
        return
    def init(self):
        return
    def update(self):
        self.button.update()
        self.bLayout.update()
        return
    def draw(self):
        self.layout.draw()
        self.button.draw()
        self.bLayout.draw()
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
