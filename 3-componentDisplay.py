###레모 엔진의 기본적인 그래픽 컴포넌트들을 보여주는 예제
##주석 작업은 하기 전.
##최대한 많은 컴포넌트를 때려넣고, 그것들을 이동시키거나 하면서 조작 확인해보는 것이 목적.

from REMOLib import *




class scrollLayout2(layoutObj):
    scrollbar_offset = 10
    '''
    스크롤이 가능한 레이아웃입니다.
    '''

    def getScrollbarPos(self):
        if self.isVertical:
            s_pos = RPoint(self.rect.w+2*self.scrollBar.thickness,scrollLayout.scrollbar_offset)            
        else:
            s_pos = RPoint(scrollLayout.scrollbar_offset,self.rect.h+2*self.scrollBar.thickness)
        return s_pos

    def __init__(self,rect=pygame.Rect(0,0,0,0),*,spacing=10,childs=[],isVertical=True,scrollColor = Cs.white,isViewport=True):

        super().__init__(rect=rect,spacing=spacing,childs=childs,isVertical=isVertical)
        self.setAsViewport(isViewport)
        if isVertical:
            s_length = self.rect.h
        else:
            s_length = self.rect.w
        self.scrollBar = sliderObj(pos=RPoint(0,0),length=s_length-2*scrollLayout.scrollbar_offset,isVertical=isVertical,color=scrollColor) ##스크롤바 오브젝트

        self.scrollBar.setParent(self,depth=1) ##스크롤바는 레이아웃의 뎁스 1 자식으로 설정됩니다.
        self.scrollBar.pos =self.getScrollbarPos()

        ##스크롤바를 조작했을 때 레이아웃을 조정합니다.
        def __ScrollHandle():
            if self.isVertical:
                l = -self.getBoundary().h+self.rect.h
                self.pad = RPoint(0,self.scrollBar.value*l)
                self.adjustLayout()
            else:
                l = -self.getBoundary().w+self.rect.w
                self.pad = RPoint(self.scrollBar.value*l,0)
                self.adjustLayout()
        self.scrollBar.connect(__ScrollHandle)

        self.curValue = self.scrollBar.value

    def collideMouse(self):
        return self.geometry.collidepoint(Rs.mousePos().toTuple())

    def update(self):

        ##마우스 클릭에 대한 업데이트
        for child in self.childs[0]:
            # child가 update function이 있을 경우 실행한다.
            if hasattr(child, 'update') and callable(getattr(child, 'update')):
                child.update()
        
        ##스크롤바에 대한 업데이트
        if hasattr(self,"scrollBar"):
            self.scrollBar.update()


        return

#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.image = imageObj("vampire1_default.png",pos=RPoint(1100,200))
        self.imageShadow = Rs.copyImage(self.image)
        self.imageShadow.colorize(Cs.grey,alpha=100)
        self.imageShadow.setParent(self.image,depth=-1) ##그림자는 이미지의 뒤에 그려진다.
        self.imageShadow.pos = RPoint(50,10)

        self.text = textObj("Vampire Radia",pos=(300,-20),size=40,color=Cs.red)
        self.text.setParent(self.image)
        self.longTextBg = rectObj(pygame.Rect(140,140,1100,800),color=Cs.dark(Cs.grey),edge=5,alpha=225)
        self.longTextBg.setAsViewport()
        self.name = textObj("Name: Radia",size=50)
        self.description = longTextObj("Radia is so cute, but she is 500 years old. She loves chess. 에라 모르겠다 그냥 아무글이나 좀 써보자 내가 아는 사람 얘기해 줄게 며칠전 사랑하던 그녀와 헤어진 그냥 아는 사람",
                                       textWidth=850,size=25)
        self.stats = textObj("공격력:1235,방어력:352,어쩌고 저쩌고",size=25)        
        self.textLayout = layoutObj(pos=(520,120),childs=[self.name,self.description,self.stats],spacing=30)
        self.textLayout.setParent(self.longTextBg)

        self.button = textButton("Play Game",pygame.Rect(120,400,200,50),func=lambda:print("싸운다"),radius=20)
        self.button.text = "Test Test"
        self.button.color = Cs.red
        self.button.setParent(self.longTextBg)

        self.buttons = buttonLayout(["싸운다","도망친다","쓰다듬는다","게임 종료"],pos=RPoint(120,600),isVertical=False)
        self.buttons.setParent(self.longTextBg)
        self.buttons["싸운다"].connect(lambda:print("싸운다"))
        self.buttons.싸운다.color = Cs.red
        self.buttons.게임_종료.connect(lambda:REMOGame.exit())

        self.slider = sliderObj(pygame.Rect(70,200,200,50),length=500,color=Cs.orange)
        self.slider.setParent(self.longTextBg)

        self.book = imageButton("testIcon.png",pos=(1450,330))
        self.book.setParent(self.longTextBg)

        self.testScrollLayout = scrollLayout2(pygame.Rect(100,100,300,700),isVertical=True,isViewport=True)
        for i in range(20):
            testObj = textButton("Yeah "+str(i),rect=pygame.Rect(0,0,100,50),size=30,alpha=225)
            def func(i):
                def _():
                    print("Yeah",i)
                return _
            testObj.connect(func(i))
            testObj.setParent(self.testScrollLayout)
        self.testScrollLayout.setParent(self.longTextBg)
        self.testScrollLayoutBg = rectObj(self.testScrollLayout.offsetRect.inflate(80,80),color=Cs.dark(Cs.grey),edge=5,alpha=225)
        self.testScrollLayoutBg.pos += RPoint(20,0)
        self.testScrollLayoutBg.setParent(self.testScrollLayout,depth=-1)
        return
    def init(self):
        return
    def update(self):
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        if Rs.userIsRightClicking():
            self.longTextBg.pos = Rs.mousePos()

        self.button.update()
        self.buttons.update()
        self.slider.update()
        self.book.update()
        self.testScrollLayout.update()
        return
    def draw(self):
        self.imageShadow.draw()
        self.image.draw()
        self.longTextBg.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DP")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
