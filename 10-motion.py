from REMOLib import *




class RMotion:
    '''
    RMotion은 게임 오브젝트의 이동을 제어하는 클래스입니다.
    '''
    __motionPipeline = []

    @classmethod
    def move(cls,obj:graphicObj,delta,*,frameDuration = 1000/60,callback = lambda:None):
        p = RPoint(0,0)
        inst = []
        while p!=delta:
            temp = p
            p = p.moveTo(delta)
            inst.append(p-temp)
        
        cls.__motionPipeline.append({"obj":obj,"inst":inst,"timer":RTimer(frameDuration),"callback":callback})

    @classmethod
    def _motionUpdate(cls):
        for motion in cls.__motionPipeline:
            if motion["timer"].isOver():
                motion["obj"].pos = motion["obj"].pos + motion["inst"].pop(0)
                if len(motion["inst"])==0:
                    cls.__motionPipeline.remove(motion)
                    motion["callback"]()
                motion["timer"].reset()
        return








#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.t = textObj("Hello",size=30)
        self.t.center = Rs.screen.get_rect().center
        RMotion.move(self.t,RPoint(100,0))
        self.switch = True
        return
    def init(self):
        return
    def update(self):
        RMotion._motionUpdate()
        if Rs.userJustLeftClicked():
            self.switch = not self.switch
            if self.switch:
                RMotion.move(self.t,RPoint(0,100),callback=lambda:setattr(self.t,'color',Cs.red))
            else:
                RMotion.move(self.t,RPoint(0,-100),callback=lambda:setattr(self.t,'color',Cs.blue))
        return
    def draw(self):
        self.t.draw()
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
