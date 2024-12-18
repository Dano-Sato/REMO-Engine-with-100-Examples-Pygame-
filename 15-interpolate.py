from REMOLib import *
import numpy as np


class RMath:
    @classmethod
    def _interpolate(cls,a, b, t, interpolation=lambda x:x):
        """ a와 b 사이를 t만큼 보간하고, 벡터 혹은 스칼라 값을 처리합니다.
        :param a: 시작 값 또는 벡터
        :param b: 끝 값 또는 벡터
        :param t: 보간 계수 (0에서 1 사이)
        :param mode: 보간 모드 ('linear', 'exponential', 'bounce', 'elastic', 'quadratic')
        :param smoothness: 부드러움 조절 인자
        :return: 보간된 값 또는 벡터
        """

        # t 값이 범위를 넘지 않도록 클램핑
        t = np.clip(t, 0.0, 1.0)
        t = interpolation(t)
        # 벡터 또는 스칼라 보간 처리
        if isinstance(a, (list, tuple, np.ndarray)):
            a = np.array(a)
            b = np.array(b)
        return a + (b - a) * t
    
    @classmethod
    def lerp(cls,start,dest,t):
        '''
        선형 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t)
    
    @classmethod
    def easein(cls,start,dest,t):
        '''
        가속 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,lambda x: x**2.5)

    @classmethod
    def easeout(cls,start,dest,t):
        '''
        감속 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,lambda x: 1-(1-x)**2.5)
    
    @classmethod
    def smooth(cls,start,dest,t):
        '''
        시작과 끝이 부드러운 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,lambda t: t**3 * (t * (6 * t - 15) + 10))
    
    @classmethod
    def bounce(cls,start,dest,t):
        '''
        바운스 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,cls._bounce)

    @classmethod
    def _bounce(cls, t):
        """ 바운스 보간 (강도 조절 가능) """

        if t < 1 / 2.75:
            return (7.5625 * t * t)
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return (7.5625 * t * t + 0.75)
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return (7.5625 * t * t + 0.9375)
        else:
            t -= 2.625 / 2.75
            return (7.5625 * t * t + 0.984375)
        


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        '''
        이 함수는 시간에 따른 보간 함수 예시로, 오브젝트의 위치, 크기, 투명도, 회전 각도를 점진적으로 변경합니다.        
        '''
        self.t = 0
        self.testObj = textObj("TEST",size=30)
        self.start = RPoint(300,500)
        self.dest = RPoint(1300,500)
        self.testObj2 = imageObj("coin.png",pos=RPoint(200,500))

        def disappear():
            self.testObj2.pos = RPoint(200,500)
            self.testObj2.alpha = 255
            self.testObj2.scale = 1
            self.testObj2.angle = 0
            self.testObj2.easeout(["pos","scale","alpha","angle"],[RPoint(1000,500),3,0,50],callback=disappear,revert=True)
            print("Disappear!")
        disappear()
        self.layout = buttonLayout(["Test","Test2","Test3"],RPoint(2300,100))
        self.layout.alpha = 0
        def bouncebounce():
            print("Bounce!")
            self.layout.alpha = 0
            self.layout.pos = RPoint(2300,100)
            self.layout.bounce(["pos","alpha"],[RPoint(1200,100),255],callback=bouncebounce,revert=True,on_update=lambda:print("test"))

        bouncebounce()


        self.unfold = False
        return
    def init(self):
        return
    def update(self):
        if self.t < 1 and not self.unfold:
            self.t += 0.02
            self.testObj.center = RMath.bounce(self.start,self.dest,self.t)
            self.testObj.size = RMath.bounce(30,70,self.t)
            self.testObj.color = RMath.bounce(Cs.white,Cs.cornflowerblue,self.t)
            self.testObj.angle = RMath.bounce(0,360,self.t)
            if self.t >= 1:
                self.unfold = True
                self.t = 0
        if self.unfold and self.t < 1:
            self.t +=0.02
            self.testObj.center = RMath.easein(self.dest,self.start,self.t)
            self.testObj.size = RMath.easein(70,30,self.t)
            self.testObj.color = RMath.easein(Cs.cornflowerblue,Cs.white,self.t)
            self.testObj.angle = RMath.easein(360,0,self.t)
            if self.t >= 1:
                self.unfold = False
                self.t = 0
        if Rs.userJustPressed(pygame.K_z):
            temp_obj = textObj("TEST",size=150)
            temp_obj.center = Rs.screenRect().center
            temp_obj.easeout(["size","alpha"],[30,0],show=True)
        self.layout.update()
        
        return
    def draw(self):
        self.testObj.draw()
        self.testObj2.draw()
        self.layout.draw()
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
