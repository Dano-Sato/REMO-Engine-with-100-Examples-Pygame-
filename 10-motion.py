from REMOLib import *




class RMotion:
    '''
    RMotion은 게임 오브젝트의 이동을 제어하는 클래스입니다.
    '''
    __motionPipeline = []

    @classmethod
    def move(cls,obj:graphicObj,delta,*,frameDuration = 1000/60,callback = lambda:None,smoothness=8):
        '''
        지정한 오브젝트를 주어진 변위 `delta`만큼 이동시키는 함수입니다.\n
        obj: 이동할 그래픽 오브젝트\n
        delta: 이동 변위 (RPoint)\n
        frameDuration: 한 프레임당 지속 시간 (기본값: 1000/60 밀리초)\n
        callback: 이동이 끝났을 때 호출할 함수 (기본값: 빈 함수)\n
        smoothness: 이동의 부드러움을 조절하는 값 (기본값: 8, 값이 클수록 이동이 부드럽고 느려짐)\n
        '''
        p = RPoint(0,0)
        inst = []
        while p!=delta:
            temp = p
            p = p.moveTo(delta,smoothness=smoothness)
            inst.append(p-temp)
        
        cls.__motionPipeline.append({"obj":obj,"inst":inst,"timer":RTimer(frameDuration),"callback":callback})

    @classmethod
    def shake(cls,obj:graphicObj,intensity=RPoint(0,5),count=30,*,frameDuration = 1000/60,callback = lambda:None):
        '''
        지정한 오브젝트를 `intensity` 값에 따라 랜덤하게 흔드는 함수입니다.\n
        obj: 흔들릴 그래픽 오브젝트\n
        intensity: 흔들림의 x,y축 강도를 나타내는 값 (RPoint, 기본값: RPoint(0, 5))\n
        count: 흔드는 횟수 (기본값: 30)\n
        frameDuration: 한 프레임당 지속 시간 (기본값: 1000/60 밀리초)\n
        callback: 흔들림이 끝났을 때 호출할 함수 (기본값: 빈 함수)\n
        '''
        inst = []
        for _ in range(count):
            delta = RPoint(random.randint(-intensity.x,intensity.x),random.randint(-intensity.y,intensity.y))
            inst.extend([delta,-delta])
        cls.__motionPipeline.append({"obj":obj,"inst":inst,"timer":RTimer(frameDuration),"callback":callback})
        None


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
    
    @classmethod
    def jump(cls,obj:graphicObj,delta:RPoint,*,frameDuration = 1000/60,callback = lambda:None,gravity=4):
        '''
        지정한 오브젝트를 주어진 변위 `delta`만큼 점프시키는 함수입니다.\n
        알고리즘 특성상 변위가 정확하지 않은 경우가 있습니다.
        obj: 점프할 그래픽 오브젝트\n
        delta: 점프 변위 (RPoint)\n
        frameDuration: 한 프레임당 지속 시간 (기본값: 1000/60 밀리초)\n
        callback: 점프가 끝났을 때 호출할 함수 (기본값: 빈 함수)\n
        smoothness: 점프의 부드러움을 조절하는 값 (기본값: 8, 값이 클수록 점프가 부드럽고 느려짐)\n
        '''
        d = delta.distance(RPoint(0,0))
        v = math.sqrt(2*gravity*d)
        g = gravity
        inst = []
        temp = RPoint(0,0)
        while True:
            _d =(v/d)*delta
            inst.append(_d)
            temp += _d
            if v<g:
                break
            v -= g
        inst.extend([-x for x in reversed(inst)])
        cls.__motionPipeline.append({"obj":obj,"inst":inst,"timer":RTimer(frameDuration),"callback":callback})
 








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
        self.switch = True
        return
    def init(self):
        return
    def update(self):
        RMotion._motionUpdate()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
