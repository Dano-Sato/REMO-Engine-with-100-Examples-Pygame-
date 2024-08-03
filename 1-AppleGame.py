from REMOLib import *



##REMO Engine은 pygame 라이브러리 위에 얹어진 효율 좋고 컴팩트한 2D 게임 엔진입니다.
##2D 게임에 관련된 다양한 객체를 활용할 수 있습니다!

##애플 게임은, 땅에 놓여진 사과를 먹는 게임입니다.
##이 예제를 통해 기본적인 게임의 그래픽 객체와 User I/O 처리 등을 확인할 수 있습니다!


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        ### 플레이어 객체.(사각형 오브젝트) radius->모서리의 둥글기. edge-모서리의 살짝 어두운 부분의 굵기(미적인 요소)
        mainScene.player = rectObj(pygame.Rect(500,200,60,60),color=Cs.white,radius=10,edge=3) 
        ###

        ### 플레이어의 머리에 붙는 라벨 객체입니다. (텍스트 오브젝트)
        ## 텍스트 오브젝트의 폰트, 사이즈, 컬러, 각도(angle)을 지정가능합니다.
        ## 여기서 playerLabel은 player의 자식이 되는데, 자식 객체는 부모 객체의 상대적인 위치(부모 객체의 위치로부터 (-20,-30). 즉 x축으로 -20, y축으로 -30)에 존재하게 됩니다.
        ## 자식 객체는 부모 객체의 위에 그려집니다.
        mainScene.playerLabel = textObj("This is You",pos=(-10,-30),size=15)
        mainScene.playerLabel.setParent(mainScene.player)
        ###

        ###플레이어가 돌아다니면서 먹을 애플 객체입니다. 플레이어와 같은 방식으로 구현되었습니다.
        mainScene.apple = rectObj(pygame.Rect(200,100,30,30),color=Cs.red,radius=10,edge=3)
        mainScene.appleLabel = textObj("I'm apple!",pos=(-10,-30),size=15)
        mainScene.appleLabel.setParent(mainScene.apple)
        ###

        return
    def init(self):
        return
    def update(self):

        ###WASD 조작 블록

        speed = 5

        ##키보드의 W키를 유저가 누르고 있을 경우, player가 위로(-y방향) 이동합니다.
        if Rs.userPressing(pygame.K_w):
            mainScene.player.pos += RPoint(0,-speed)
        if Rs.userPressing(pygame.K_a):
            mainScene.player.pos += RPoint(-speed,0)
        if Rs.userPressing(pygame.K_s):
            mainScene.player.pos += RPoint(0,speed)
        if Rs.userPressing(pygame.K_d):
            mainScene.player.pos += RPoint(speed,0)
        ###

        return
    def draw(self):
        Rs.fillScreen(Cs.black)
        mainScene.apple.draw()
        mainScene.player.draw()
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
