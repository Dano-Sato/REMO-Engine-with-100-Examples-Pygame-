from REMOLib import *

##TODO: dialogObj, inventoryObj,cardObj, cardLayout를 만들어보자.
##setCursor 메소드 만들어보자.


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):

        ##게임 종료 다이얼로그
        self.escDialog = dialogObj(pygame.Rect(200,200,600,250),"-주의-","게임을 종료합니까?",["Yes","No"],color=Cs.dark(Cs.grey),spacing=20)
        self.escDialog["Yes"].connect(lambda:REMOGame.exit())
        self.escDialog["Yes"].color = Cs.dark(Cs.red)
        def No():
            self.escDialog.hide()
        self.escDialog["No"].connect(No)        



        return
    def init(self):
        return
    def update(self):

        #ESC키를 누르면 게임 종료 다이얼로그가 나타난다.
        if Rs.userJustPressed(pygame.K_ESCAPE):
            if not self.escDialog.isShown():
                self.escDialog.center = Rs.Point(Rs.screen.get_rect().center)
                self.escDialog.show()
            else:
                self.escDialog.hide()

        #게임 종료 다이얼로그를 드래그할 수 있다.
        if self.escDialog.isShown():
            Rs.dragEventHandler(self.escDialog)

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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
