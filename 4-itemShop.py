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

        Rs.playMusic("piano_calm.mp3")
        print(self.item_db)
        return
    def init(self):
        return
    def update(self):
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        return
    def draw(self):
        self.clerk.draw()
        self.label.draw()
        self.moneyBg.draw()
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
