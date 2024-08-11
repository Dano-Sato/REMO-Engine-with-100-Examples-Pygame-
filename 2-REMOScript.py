
##게임 메뉴로부터 비주얼노벨 스크립트에 진입하고, 다시 되돌아오는 가장 간단한 형식의 비주얼노벨

from REMOLib import *







#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None


##TODO:
#처음 게임 시작 배경에 먼가 이쁜 (미소녀?) 배경 넣기.
#미소녀와 대화하기 버튼 누르면 왼쪽에 씬 나열 + 오른쪽에 신 클릭시 신에 대한 설명문 + 아래쪽에 대화하기 버튼 누른다.
#각 신을 누르면 대화가 진행되고, 끝나면 다시 해당 장면으로 돌아온다.
class mainScene(Scene):
    def initOnce(self):
        ##buttonLayout: 간단하게 텍스트 버튼 GUI를 만든다.
        self.menus = buttonLayout(["미소녀와 대화하기","게임 종료"],pos=RPoint(240,440),fontSize=40,buttonSize=RPoint(300,80))

        def exit():
            REMOGame.exit()
        self.menus["게임 종료"].connect(exit) # connect -> 버튼에 함수를 연결. 버튼 좌클릭시 함수가 작동함.
        #게임 종료 버튼을 누르면 게임이 꺼진다.
        self.menus["게임 종료"].color = Cs.red #버튼의 색깔을 바꿀 수 있음.

        REMODatabase.zipScript("2-scripts",prefix="2")
        REMODatabase.loadScripts("2-scripts")

        def test():
            self.runScript("2-script2")

        self.menus["미소녀와 대화하기"].connect(test)

        

        return

##해당 비주얼노벨 스크립트를 실행한다.
    def runScript(self,scriptName):
        scriptScene.currentScript=scriptName
        REMOGame.setCurrentScene(Scenes.scriptScene)
        None

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


##비주얼 노벨 스크립트를 출력하는 신
class scriptScene(Scene):
    currentScript = ""
    def initOnce(self):
        return
    def init(self):
        self.renderer = scriptRenderer(scriptScene.currentScript)
        def goBackToMain():
            REMOGame.setCurrentScene(Scenes.mainScene)
        self.renderer.endFunc = goBackToMain
        #self.renderer.setFont("japanese_script.ttf")
        return
    def update(self):
        self.renderer.update()
        return
    def draw(self):
        if hasattr(self,"renderer"):
            self.renderer.draw()
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
    scriptScene = scriptScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
