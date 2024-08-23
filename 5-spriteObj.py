from REMOLib import *

##TODO: dialogObj, inventoryObj,cardObj, cardLayout를 만들어보자.
##setCursor 메소드 만들어보자.



#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class charaMode(Enum):
    idle = 0
    walkRight = 1
    walkLeft = 2
    attack = 3

class mainScene(Scene):
    def initOnce(self):

        ##게임 종료 다이얼로그
        self.escDialog = dialogObj(pygame.Rect(200,200,600,250),"-주의-","게임을 종료합니까?",["Yes","No"],color=Cs.dark(Cs.grey),spacing=20)
        self.escDialog["Yes"].connect(lambda:REMOGame.exit())
        self.escDialog["Yes"].color = Cs.dark(Cs.red)
        def No():
            self.escDialog.hide()
        self.escDialog["No"].connect(No)        

        self.charaSetting = {"scale":3,"frameDuration":1000/10}
        self.charaSprite = spriteObj("Idle_KG_2.png",pos=(50,50),sheetMatrix=(1,4),scale=3,frameDuration=1000/10)
        self.charaSprite.colorize(Cs.red)
        self.charaSprite.center = Rs.screen.get_rect().center
        self.charaMode = charaMode.idle

        self.testImage = imageObj(["testItemSheet.png",(9,8),11],pos=(100,600),scale=3)

        return
    def init(self):
        return
    def update(self):
        speed = 5

        if Rs.userPressing(pygame.K_a):
            self.charaSprite.scale+=0.1
        elif Rs.userPressing(pygame.K_s):
            self.charaSprite.angle+=1
            print(self.charaSprite.angle)


        if Rs.userPressing(pygame.K_z):
            if self.charaMode != charaMode.attack:
                self.charaSprite = spriteObj("Attack_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,6),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.attack
        elif Rs.userPressing(pygame.K_RIGHT):
            self.charaSprite.pos += Rs.Point(speed,0)
            if self.charaMode != charaMode.walkRight:
                self.charaSprite = spriteObj("Walking_KG_2.png",pos=self.charaSprite.pos ,sheetMatrix=(1,7),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.walkRight
        elif Rs.userPressing(pygame.K_LEFT):
            self.charaSprite.pos -= Rs.Point(speed,0)
            if self.charaMode != charaMode.walkLeft:
                self.charaSprite = spriteObj("Walking_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,7),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.walkLeft
        else:
            if self.charaMode != charaMode.idle:
                self.charaSprite = spriteObj("Idle_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,4),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.idle

        self.charaSprite.update()

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
        self.charaSprite.draw()
        self.testImage.draw()
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
