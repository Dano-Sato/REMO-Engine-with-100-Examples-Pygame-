##아이템 샵에서 물건을 구매하는 예제

from REMOLib import *



##스크롤바를 통해 스크롤링이 가능한 레이아웃. rect영역 안에 레이아웃이 그려집니다.
##TODO: 지정한 rect 영역보다 객체 길이가 짧으면 스크롤바가 안 보여야 한다.
##Bug: 객체 추가시 물체가 이동한다.
class scrollLayout(layoutObj):
    scrollbar_offset = 10

    #object의 차일드들의 영역을 포함한 전체 영역을 계산
    @property
    def boundary(self):
        r = self.geometry
        for c in self.childs:
            r = r.union(c.boundary)
        return r
    #오브젝트의 캐시 이미지를 만든다.
    ##뷰포트를 벗어나는 이미지는 그리지 않는다.
    def _getCache(self):
        if id(self) in Rs.graphicCache:
            try:
                return Rs.graphicCache[id(self)]
            except:
                pass

        r = self.boundary
        bp = RPoint(r.x,r.y) #position of boundary
        cache = pygame.Surface((self.rect.w,self.rect.h),pygame.SRCALPHA,32).convert_alpha()
        viewport = cache.get_rect()
        for c in self.childs:
            if not c.rect.colliderect(viewport):
                continue
            ccache,cpos = c._getCache()
            p = cpos-bp+self.pad
            cache.blit(ccache,p.toTuple(),special_flags=pygame.BLEND_ALPHA_SDL2)
        
        ##스크롤바 그리기
        ccache,cpos = self.scrollBar._getCache()
        p = cpos-self.geometryPos
        cache.blit(ccache,p.toTuple(),special_flags=pygame.BLEND_ALPHA_SDL2)

        cache.set_alpha(self.alpha)


        return [cache,self.geometryPos]


    def getScrollbarPos(self):
        if self.isVertical:
            s_pos = RPoint(self.rect.w-2*self.scrollBar.thickness,scrollLayout.scrollbar_offset)            
        else:
            s_pos = RPoint(scrollLayout.scrollbar_offset,self.rect.h-2*self.scrollBar.thickness)
        return s_pos

    ##스크롤바의 위치를 레이아웃에 맞게 조정합니다.
    def adjustScrollbar(self):
        
        self.scrollBar.pos = self.getScrollbarPos()+self.geometryPos

    def __init__(self,rect=pygame.Rect(0,0,0,0),*,pos=None,spacing=10,childs=[],isVertical=True,scrollColor = Cs.white):

        super().__init__(rect=rect,pos=pos,spacing=spacing,childs=childs,isVertical=isVertical)
        if isVertical:
            s_length = self.rect.h
        else:
            s_length = self.rect.w
        self.scrollBar = sliderObj(pos=RPoint(0,0),length=s_length-2*scrollLayout.scrollbar_offset,isVertical=isVertical,color=scrollColor) ##스크롤바 오브젝트
        self.adjustScrollbar()
        self.curValue = self.scrollBar.value


    ##setParent 함수 오버로드
    def setParent(self,p):
        super().setParent(p)
        self.adjustLayout()

    ##스크롤 영역이 마우스와 충돌하는지 확인합니다.
    def collideMouse(self):
        return pygame.Rect(self.geometryPos.x(),self.geometryPos.y(),self.rect.w,self.rect.h).collidepoint(Rs.mousePos().toTuple())

    def update(self):
        viewport = pygame.Rect(0,0,self.rect.w,self.rect.h)

        if Rs.userJustLeftClicked() and self.collideMouse():
            print("DEBUG")

        ##마우스 클릭에 대한 업데이트
        for child in self.childs:
            # child가 update function이 있을 경우 실행한다.
            if hasattr(child, 'update') and callable(getattr(child, 'update')) and viewport.colliderect(child.rect):
                child.update()
        if hasattr(self,"scrollBar"):
            self.adjustScrollbar()
            self.scrollBar.update()
            ##스크롤바를 움직일 때, 레이아웃의 위치를 조정해야 합니다. (self.pad 조정)
            if self.curValue != self.scrollBar.value:
                if self.isVertical:
                    l = -self.boundary.h+self.rect.h
                    self.pad = RPoint(0,self.scrollBar.value*l)
                    self.adjustLayout()
                else:
                    l = -self.boundary.w+self.rect.w
                    self.pad = RPoint(self.scrollBar.value*l,0)
                    self.adjustLayout()
                self.curValue = self.scrollBar.value

        return


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
        self.item_db = REMODatabase.loadExcel('item.xlsx')

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


        ##스크롤 레이아웃 테스트
        ##테스트케이스: 객체가 적을때, 많을때, 아주 많을때
        ##스크롤레이아웃이 무엇인가의 자식 객체가 되었을 때
        self.testlayout = scrollLayout(pygame.Rect(30,130,200,500),isVertical=True)
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
        self.testlayout.adjustLayout()
        self.testDrag.setParent(self.testBg)
        print(self.item_db)
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


        if Rs.userJustPressed(pygame.K_s):
            obj = self.testlayout.childs[0]
            obj.setParent(None)

        Rs.dragEventHandler(self.testDrag,self.testBg)
        self.testlayout.update()
        Rs.releaseDrawLock()
        return
    def draw(self):
        self.clerk.draw()
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
