from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class myMethods:
    @classmethod
    def initCursor(cls):
        pygame.mouse.set_visible(False)
        cls.cursor = imageObj(Icons.CURSOR,scale=0.5)
    None

class mainScene(Scene):
    def initOnce(self):
        Rs.initCursor()
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
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
