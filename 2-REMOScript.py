
##게임 메뉴로부터 비주얼노벨 스크립트에 진입하고, 다시 되돌아오는 가장 간단한 형식의 비주얼노벨

from REMOLib import *







#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        ##buttonLayout: 간단하게 텍스트 버튼 GUI를 만든다.
        self.menus = buttonLayout(["미소녀와 대화하기","게임 종료"],pos=RPoint(240,440),fontSize=40,buttonSize=RPoint(300,80))

        def exit():
            REMOGame.exit()
        self.menus["게임 종료"].connect(exit)
        self.menus["게임 종료"].color = Cs.red
        return
    def init(self):
        return
    def update(self):
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        self.menus.update()
        return
    def draw(self):
        self.menus.draw()
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
    window = REMOGame(window_resolution=(1280,720),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
