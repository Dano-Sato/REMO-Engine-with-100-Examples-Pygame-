
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
        ##게임 종료 다이얼로그 선언
        self.escDialog = dialogObj(pygame.Rect(200,200,800,250),"","대화를 종료하고 메인 화면으로 돌아가시겠습니까?",["네","아니오"],color=Cs.dark(Cs.grey),spacing=20)
        def goMain():
            REMOGame.setCurrentScene(Scenes.mainScene)
            self.escDialog.hide()
            self.renderer.clear()
            Rs.clearAnimation()
        self.escDialog["네"].connect(goMain) ##네를 누르면 메인화면으로 돌아간다.
        self.escDialog["네"].color = Cs.dark(Cs.red)
        self.escDialog["아니오"].connect(lambda:self.escDialog.hide())
        ###

        return
    def init(self):
        self.renderer = scriptRenderer(scriptScene.currentScript)
        self.renderer.endFunc = lambda:REMOGame.setCurrentScene(Scenes.mainScene) ##스크립트가 끝나면 메인화면으로 돌아간다.
        #self.renderer.setFont("japanese_script.ttf")
        return
    def update(self):
        ##ESC키를 누르면 대화를 종료하는 다이얼로그가 나타난다.
        if Rs.userJustPressed(pygame.K_ESCAPE):
            if not self.escDialog.isShown():
                self.escDialog.center = Rs.Point(Rs.screen.get_rect().center)
                self.escDialog.show()
                self.escDialog.update()
            else:
                self.escDialog.hide()

        Rs.acquireDrawLock()
        self.renderer.update()
        Rs.releaseDrawLock()
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
