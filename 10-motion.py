from REMOLib import *









#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    d = 300
    def initOnce(self):
        self.t = textObj("Hello",size=30)
        self.t.center = Rs.screen.get_rect().center
        #RMotion.move(self.t,RPoint(mainScene.d,0))
        self.j = RPoint(0,50)
        RMotion.jump(self.t,self.j,gravity=16)
        self.red = rectObj(pygame.Rect(0,0,10,10),color=Cs.red) 
        self.red.center = self.t.pos+self.j  
        RMotion.shake(self.t,intensity=RPoint(10,10),count=30,frameDuration=1000/60)
        RMotion.fadein(self.t,smoothness=15)
        self.switch = True
        return
    def init(self):
        return
    def update(self):

        for event in Rs.events:
            if event.type == pygame.VIDEORESIZE:
                print("RESIZE")
        if Rs.userJustLeftClicked():
            self.switch = not self.switch
            if self.switch:
                RMotion.move(self.t,RPoint(0,mainScene.d),callback=lambda:setattr(self.t,'color',Cs.red))
            else:
                RMotion.move(self.t,RPoint(0,-mainScene.d),callback=lambda:setattr(self.t,'color',Cs.blue))
        if Rs.userJustRightClicked():
            RMotion.jump(self.t,self.j,gravity=16)

        return
    def draw(self):
        self.t.draw()
        self.red.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT",flags=pygame.RESIZABLE)
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
