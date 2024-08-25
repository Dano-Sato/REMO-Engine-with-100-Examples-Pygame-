##아이템 샵에서 물건을 구매하는 예제

from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):

    ##Money I/O
    def setMoney(self,_money):
        self.money.text = str(_money)
        self.money.bottomright=RPoint(self.moneyBg.rect.w,self.moneyBg.rect.h)-RPoint(10,10)

    def getMoney(self):
        return int(self.money.text)

    def initOnce(self):

        ##보유한 돈을 보여주기 위한 GUI 오브젝트 모음
        self.moneyBg = rectObj(pygame.Rect(1500,60,200,50),color=Cs.dark(Cs.grey))
        self.coinIcon = imageObj("coin.png",pos=RPoint(0,0),scale=0.37) ## 코인 아이콘
        self.coinIcon.centery = self.moneyBg.rect.h//2
        self.coinIcon.setParent(self.moneyBg)
        self.money = textObj("",pos=(0,0),size=35) ## 돈을 보여주는 텍스트
        self.money.setParent(self.moneyBg)
        self.setMoney(10000)

        ##여고생쟝
        self.clerk = imageObj("schoolGirl1_default.png",pos=(-150,0))

        self.label = textObj("Mirai's Shop",size=40,pos=(0,0))
        self.label.midtop = (960,20)

        self.clerkTalk = textBubbleObj("어서오세요! 무엇을 도와드릴까요?",pos=(630,200),size=30,liveTimer=200,bgColor=Cs.dark(Cs.grey))


        ##스크롤 레이아웃 테스트
        ##테스트케이스: 객체가 적을때, 많을때, 아주 많을때
        ##스크롤레이아웃이 무엇인가의 자식 객체가 되었을 때
        self.testlayout = scrollLayout(pygame.Rect(20,80,220,500),isVertical=True)
        self.testBg = rectObj(pygame.Rect(100,100,300,700),color=Cs.dark(Cs.grey))
        self.testDrag = rectObj(pygame.Rect(0,0,300,50),color=Cs.grey)
        for i in range(20):
            testObj = textButton("Yeah "+str(i),rect=pygame.Rect(0,0,100,50),size=30)
            def func(i):
                def _():
                    if self.testlayout.collideMouse():
                        print("Yeah",i)
                return _
            testObj.connect(func(i))
            testObj.setParent(self.testlayout)

        self.testlayout.setParent(self.testBg)
        self.testDrag.setParent(self.testBg)
        return
    def init(self):
        return
    
    def update(self):
        Rs.acquireDrawLock()
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        if Rs.userJustPressed(pygame.K_a):
            obj = textButton("Good good",rect=pygame.Rect(0,0,100,50),size=30)
            obj.setParent(self.testlayout)
        if Rs.userJustPressed(pygame.K_z):
            None


        if Rs.userJustPressed(pygame.K_s):
            obj = self.testlayout.childs[0]
            obj.setParent(None)

        self.clerkTalk.updateText()
        Rs.dragEventHandler(self.testDrag,draggedObj=self.testBg)
        self.testlayout.update()
        Rs.releaseDrawLock()
        return
    def draw(self):
        self.clerk.draw()
        self.clerkTalk.draw()
        self.label.draw()
        self.moneyBg.draw()
        self.testBg.draw()
        #self.testlayout.scrollBar.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="Item Shop")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
