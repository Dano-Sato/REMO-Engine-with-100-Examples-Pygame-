from REMOLib import *



##REMO Engine은 pygame 라이브러리 위에 얹어진 효율 좋고 컴팩트한 2D 게임 엔진입니다.
##2D 게임에 관련된 다양한 객체를 활용할 수 있습니다!

##애플 게임은, 땅에 놓여진 사과를 먹는 게임입니다.
##이 예제를 통해 기본적인 게임의 그래픽 객체와 User I/O 처리 등을 확인할 수 있습니다!

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
        mainScene.apple = rectObj(pygame.Rect(200,100,20,20),color=Cs.red,radius=6,edge=3)
        mainScene.appleLabel = textObj("I'm apple!",pos=(-10,-30),size=15)
        mainScene.appleLabel.setParent(mainScene.apple)
        ###

        mainScene.score = 0
        mainScene.scoreLabel = textObj("SCORE:0",pos=(550,50),size=30)

        return

    def updateScore(self,_score):
        mainScene.score = _score
        mainScene.scoreLabel.text = 'SCORE:'+str(mainScene.score)
    
    def putApple(self):
        x = random.randint(100,1100)
        y = random.randint(100,700)
        mainScene.apple.pos = RPoint(x,y)

    def init(self):
        return
    def update(self):

        ###WASD (또는 화살표) 조작 블록

        speed = 5

        ##키보드의 W키를 유저가 누르고 있을 경우, player가 위로(-y방향) 이동합니다.
        ##RPoint는 REMO Engine의 2D Point 객체입니다.
        if Rs.userPressing(pygame.K_w) or Rs.userPressing(pygame.K_UP):
            mainScene.player.pos += RPoint(0,-speed)
        if Rs.userPressing(pygame.K_a) or Rs.userPressing(pygame.K_LEFT):
            mainScene.player.pos += RPoint(-speed,0)
        if Rs.userPressing(pygame.K_s) or Rs.userPressing(pygame.K_DOWN):
            mainScene.player.pos += RPoint(0,speed)
        if Rs.userPressing(pygame.K_d) or Rs.userPressing(pygame.K_RIGHT):
            mainScene.player.pos += RPoint(speed,0)
        ###
            

        
        ###충돌 판정
        
        if mainScene.player.collidepoint(mainScene.apple.center):
            self.updateScore(mainScene.score+10)
            self.putApple()
            
    


        return
    def draw(self):
        Rs.fillScreen(Cs.black)
        mainScene.apple.draw()
        mainScene.player.draw()
        mainScene.scoreLabel.draw()
        return

class Scenes:
    mainScene = mainScene()


if __name__=="__main__":
    #Screen Setting
    ##게임의 윈도우 해상도, 게임내 픽셀수(screen_size), 타이틀명 등을 정합니다.
    window = REMOGame(window_resolution=(1200,800),screen_size=(1200,800),fullscreen=False,caption="1.Apple Game")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
