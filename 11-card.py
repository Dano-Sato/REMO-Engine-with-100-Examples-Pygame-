from REMOLib import *




# 카드를 일렬로 배치하기 위해 존재하는 레이아웃 오브젝트입니다.
class cardLayout(layoutObj):

    def __init__(self,pos,spacing=10,maxWidth=500, isVertical=False):
        super().__init__(pos=pos,spacing=spacing,isVertical=isVertical)
        self.maxWidth = maxWidth # 카드를 배치하는 최대 길이


    def cardLength(self,child:graphicObj) -> int:
        if self.isVertical:
            return child.rect.h
        else:
            return child.rect.w

    def makeVector(self,l):
        if self.isVertical:
            return RPoint(0,l)
        else:
            return RPoint(l,0)
    #카드들의 간격을 정하는 함수
    def delta(self,c:graphicObj,isCollide):
        if len(self)<=1:
            return RPoint(0,0)
        else:
            if c.collideMouse():
                return self.makeVector(self.cardLength(c))
            else:
                if isCollide:
                    _spacing = (self.maxWidth-2*self.cardLength(c)) / (len(self)-1)
                else:
                    _spacing = (self.maxWidth-self.cardLength(c)) / (len(self)-1)


                _spacing = min(_spacing,self.spacing+self.cardLength(c))
                return self.makeVector(_spacing)
            
    #레이아웃 내부 객체 위치 조정 (override)
    def adjustLayout(self,smoothness=3):
        lastChild = None
        isCollide = False
        for child in self.getChilds():
            if child.collideMouse():
                isCollide = True
                break
        

        for child in self.getChilds():
            if lastChild != None:
                if child.collideMouse():
                    child.pos = child.pos.moveTo(lastChild.pos+self.makeVector(self.cardLength(child)),smoothness=smoothness)
                else:
                    child.pos = child.pos.moveTo(lastChild.pos+self.delta(lastChild,isCollide),smoothness=smoothness)
            else:
                child.pos = self.pad
            lastChild = child
        self._clearGraphicCache()


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def makeTestCard(self,i):
        card = rectObj(pygame.Rect(0,0,160,240),color=Cs.grey,edge=8)
        cardLabel = textObj(f"Card {i}",size=30)
        cardLabel.midtop = card.rect.midtop + RPoint(0,10)
        cardLabel.setParent(card)
        card.merge()
        return card
    def initOnce(self):
        width = 700
        self.cards = cardLayout(RPoint(100,100),spacing=10,maxWidth=width,isVertical=True)
        self.cardBg = rectObj(pygame.Rect(0,0,200,width).inflate(10,10),color=Cs.red,edge=8)
        self.cardBg.setParent(self.cards,depth=-1)
        self.testCounter = 0
        for i in range(3):
            card = self.makeTestCard(i)
            card.setParent(self.cards)
            self.testCounter+=1
        return
    def init(self):
        return
    def update(self):
        self.cards.adjustLayout()
        if Rs.userJustPressed(pygame.K_z):
            card = self.makeTestCard(self.testCounter)
            card.setParent(self.cards)
            self.testCounter+=1
        return
    def draw(self):
        self.cards.draw()
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
