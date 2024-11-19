from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    helpSheet = {
        "기본 설명":"이 프로젝트는 REMO Game Engine을 사용하여 제작되었습니다.",
        "조작법":"ESC키를 누르면 게임을 종료합니다.",
        "라이센스":"이 프로젝트는 MIT 라이센스를 따릅니다.",
    }
    None

class mainScene(Scene):
    def initOnce(self):
        self.title = textObj("도움말",size=50,pos=(100,100))
        self.title.midtop = Rs.screenRect().midtop + RPoint(0,50)
        self.layout = Rs.makeOptionLayout(Obj.helpSheet,None,lambda option:setattr(self.description,"text",option),isVertical=True)
        self.layout.pos = RPoint(100,200)
        self.description_bg = rectObj(pygame.Rect(400,200,1900,800),color=Cs.dark(Cs.grey),edge=5,alpha=200)
        self.description = longTextObj("",pos=(500,300),textWidth=1600)
        return
    def init(self):
        return
    def update(self):
        self.layout.update()
        return
    def draw(self):
        self.title.draw()
        self.layout.draw()
        self.description_bg.draw()
        self.description.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
