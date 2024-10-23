from REMOLib import *
import numpy as np



class interpolateMode(Enum):
    LINEAR = auto()
    EXPONENTIAL = auto()
    BOUNCE = auto()
    ELASTIC = auto()
    QUADRATIC = auto()

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
        return cls._interpolate(start,dest,t,lambda x: x**3)

    @classmethod
    def easeout(cls,start,dest,t):
        '''
        감속 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,lambda x: 1-(1-x)**3)
    
    @classmethod
    def smooth(cls,start,dest,t):
        '''
        시작과 끝이 부드러운 보간을 수행합니다.
        '''
        return cls._interpolate(start,dest,t,lambda t: t**3 * (t * (6 * t - 15) + 10))
    
    @classmethod
    def _exponential(cls,t, smoothness=1.0):
        """ 지수적으로 보간 (t ** smoothness) """
        return t ** smoothness    

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

    @classmethod
    def _elastic(cls,t, smoothness=1.0):
        """ 탄성 보간 """
        if t == 0 or t == 1:
            return t
        p = smoothness * 0.3
        a = 1.0
        s = p / 4
        t -= 1
        return -(a * math.pow(2, 10 * t) * math.sin((t - s) * (2 * math.pi) / p))

    @classmethod
    def _quadratic(cls,t, smoothness=1.0):
        """ 2차 함수 보간 (t^smoothness) """
        return t ** smoothness * (2 - t)
#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.t = 0
        self.testObj = textObj("TEST",size=30)
        self.start = RPoint(100,500)
        self.dest = RPoint(1000,500)
        return
    def init(self):
        return
    def update(self):
        if self.t < 1:
            self.t += 0.01
            self.testObj.center = RMath.easein(self.start,self.dest,self.t)
        return
    def draw(self):
        self.testObj.draw()
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