from REMOLib import *


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        temp = []
        for i in range(100):
            button = textButton(f"Hello {i}")
            temp.append(button)
            
        self.myLayout = layoutObj(pos=RPoint(50,50),childs=temp)
        return
    def init(self):
        return
    def update(self):
        self.myLayout.update()
        #self.myLayout._clearGraphicCache()
        return
    def draw(self):
        self.myLayout.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
