from REMOLib import *

'''
cardLayout, monoTextButton 테스트
'''




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
        self.cards = cardLayout(RPoint(100,100),spacing=10,maxWidth=width,isVertical=False)
        self.cardBg = rectObj(pygame.Rect(0,0,width,200).inflate(10,10),color=Cs.red,edge=8)
        self.cardBg.setParent(self.cards,depth=-1)
        self.testCounter = 0
        for i in range(3):
            card = self.makeTestCard(i)
            card.setParent(self.cards)
            self.testCounter+=1


        self.button = monoTextButton("Add Card",pos=(100,400),size=30,color=Cs.grey)
        self.button.connect(lambda:print("Button Clicked!"))
        self.button2 = monoTextButton("Blabla Card",pos=(100,400),size=30,color=Cs.grey)

        self.buttons = layoutObj(pos=RPoint(100,400),spacing=30,isVertical=True,childs=[self.button,self.button2])

        return
    def init(self):
        return
    def update(self):
        self.cards.adjustLayout()
        if Rs.userJustPressed(pygame.K_z):
            card = self.makeTestCard(self.testCounter)
            card.setParent(self.cards)
            self.testCounter+=1
        self.buttons.update()
        return
    def draw(self):
        self.cards.draw()
        self.buttons.draw()
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
