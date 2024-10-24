import pygame,math,typing,random
import numpy as np
from abc import ABC

'''
REMO Library의 기본 요소들을 정의하는 모듈입니다.
'''

## Idea from Pyside2.QPoint
## includes all of the method of QPoint + additional methods
## 2-Dimensional (x,y) Point
class RPoint():
    '''
    2차원 좌표를 나타내는 클래스\n
    x,y : 좌표값\n
    toTuple() : 튜플로 변환\n
    '''
    def __init__(self,x=(0,0),y=None):
        if y==None:
            self.__x=int(x[0])
            self.__y=int(x[1])
        else:
            self.__x=int(x)
            self.__y=int(y)

    @property            
    def x(self) -> int:
        return self.__x
    @property
    def y(self) -> int:
        return self.__y

    @x.setter    
    def x(self,x:int):
        self.__x = x
    @y.setter
    def y(self,x:int):
        self.__y = x
    
    def __add__(self,p2):
        if type(p2) != RPoint:
            p2 = RPoint(p2)
        return RPoint(self.x+p2.x,self.y+p2.y)
    # 후열 덧셈 연산자
    def __radd__(self, p2):
        return self.__add__(p2)        
    def __sub__(self,p2):
        if type(p2) != RPoint:
            p2 = RPoint(p2)
        return RPoint(self.x-p2.x,self.y-p2.y)
    # 후열 뺄셈 연산자
    def __rsub__(self, p2):
        if type(p2) != RPoint:
            p2 = RPoint(p2)
        return RPoint(p2.x - self.x, p2.y - self.y)    

    ##음수 연산자
    def __neg__(self):
        return RPoint(-self.x, -self.y)

    def __mul__(self,m):
        return RPoint(int(self.x*m),int(self.y*m))
    def __rmul__(self,m):
        return self.__mul__(m)
    def __truediv__(self,m):
        return RPoint(int(self.x/m),int(self.y/m))
    def __floordiv__(self,m):
        return self/m 
    def __eq__(self,p2):
        if type(p2) != RPoint:
            return False
        if self.x==p2.x and self.y==p2.y:
            return True
        return False
    
    def toTuple(self) -> typing.Tuple[int,int]:
        return (self.__x,self.__y)
    def transposed(self):
        return RPoint(self.y,self.x)
            
    def __repr__(self):
        return "REMOGame.RPoint({0},{1})".format(self.x,self.y)
    
    
    ##2차원 거리 출력
    def distance(self,p2) -> float:
        return math.dist(self.toTuple(),p2.toTuple())
    ## 포인트 p2로 speed값만큼 이동한 결과를 반환한다. 
    def moveTo(self,p2,speed=None,*,smoothness=5):
        '''
        p2로 이동하는 함수\n
        speed : 이동속도\n
        smoothness : 이동의 매끄러움을 조절하는 값으로, 거리가 멀면 더 빠르게, 가까우면 더 느리게 이동하는 효과를 줍니다. 더 큰 값일수록 속도가 부드럽게 증가합니다.\n
        '''
        d = self.distance(p2)
        if speed==None: #스피드를 정하지 않을경우, 거리에 비례하는 속도로 정해진다
            speed=max(d/smoothness,2)
        if d <= speed:
            return p2 ##도달
        else:
            result = self
            delta = p2-self
            delta *= (speed/d)
            result += delta
        return result



class RTimer:
    '''
    타이머 클래스\n
    정해진 시간이 지나면 True를 반환한다.\n
    '''
    def __init__(self, duration, startNow=True):
        """
        :param duration: 타이머의 기간(밀리초 단위)
        :param start_now: 즉시 타이머를 시작할지 여부
        """
        self.duration = duration
        self.startTime = pygame.time.get_ticks() if startNow else None

    def start(self, duration=None):
        """타이머를 시작합니다."""
        if duration:
            self.duration = duration
        self.startTime = pygame.time.get_ticks()

    def reset(self):
        """타이머를 리셋하고 다시 시작합니다."""
        self.start()

    def stop(self):
        """타이머를 중지합니다."""
        self.startTime = None

    def isOver(self):
        """타이머가 완료되었는지 확인합니다."""
        if self.startTime is None:
            return False
        return pygame.time.get_ticks() - self.startTime >= self.duration
    
    def isRunning(self):
        '''타이머가 활성화되어 있는지 확인합니다.'''
        if self.startTime is None:
            return False
        return True

    def timeLeft(self):
        """남은 시간을 반환합니다. (밀리초 단위)"""
        if self.startTime is None:
            return self.duration
        elapsed = pygame.time.get_ticks() - self.startTime
        return max(0, self.duration - elapsed)

    def timeElapsed(self):
        """경과된 시간을 반환합니다. (밀리초 단위)"""
        if self.startTime is None:
            return 0
        return pygame.time.get_ticks() - self.startTime


class safeInt:
    bigNumber = 2147483648
    '''
    안전한 정수형 클래스입니다.
    실제 값을 저장하지 않으며 getter에서만 반환됩니다.
    '''

    def __makeOffset(self):
        return random.randint(-safeInt.bigNumber,safeInt.bigNumber)

    def __init__(self,value:int):
        self.__m = self.__makeOffset()
        self.__n = int(value) - self.__m

    @property
    def value(self):
        return self.__m + self.__n
    
    @value.setter
    def value(self,value):
        self.__m = self.__makeOffset()
        self.__n = int(value) - self.__m

    def __add__(self,other):
        return safeInt(self.value+int(other))
    def __sub__(self,other):
        return safeInt(self.value-int(other))
    def __mul__(self,other):
        return safeInt(self.value*int(other))
    def __truediv__(self,other):
        return safeInt(self.value//int(other))
    def __str__(self):
        return str(self.value)
    def __int__(self):
        return self.value
    def __float__(self):
        return float(self.value)
    def __repr__(self) -> str:
        return "safeInt({0})".format(str(self.value))

    # Comparison operators
    def __eq__(self, other):
        return self.value == other
    
    def __ne__(self, other):
        return self.value != other
    
    def __lt__(self, other):
        return self.value < other
    
    def __le__(self, other):
        return self.value <= other
    
    def __gt__(self, other):
        return self.value > other
    
    def __ge__(self, other):
        return self.value >= other


class Scene(ABC):

    def __init__(self):
        self.initiated=False
        return
    def _init(self):
        if self.initiated==False:
            self.initOnce()
            self.initiated = True
        self.init()
        
    #Scene을 불러올 때마다 initiation 되는 메소드 부분 
    def init(self):
        return
    
    #Scene을 처음 불러올때만 initiation 되는 메소드
    def initOnce(self):
        return

    def update(self):
        #update childs
        #if child has update method, it updates child
        return
    def draw(self):
        #draw childs
        return



class EventHandler:
    def __init__(self):
        # 이벤트와 해당 이벤트에 연결된 리스너(함수)들을 저장하는 딕셔너리
        self.events = {}

    def addEvent(self, event_name, listener):
        """
        새로운 이벤트 리스너를 특정 이벤트에 추가합니다.
        
        Args:
            event_name: 이벤트의 이름 또는 키.
            listener: 이벤트가 발생할 때 호출될 함수(리스너).
        """
        # 이벤트 이름이 딕셔너리에 없을 경우, 빈 리스트로 초기화
        if event_name not in self.events:
            self.events[event_name] = []
        # 해당 이벤트에 리스너를 추가
        self.events[event_name].append(listener)

    def occurEvent(self, event_name, *args, **kwargs):
        """
        특정 이벤트가 발생했을 때 해당 이벤트에 등록된 모든 리스너를 호출합니다.
        
        Args:
            event_name: 발생한 이벤트의 이름.
            *args: 리스너에 전달될 위치 기반 인자들.
            **kwargs: 리스너에 전달될 키워드 기반 인자들.
        """
        # 이벤트가 존재할 경우, 등록된 모든 리스너를 호출
        if event_name in self.events:
            for listener in self.events[event_name]:
                # *args와 **kwargs를 통해 리스너 함수에 전달
                listener(*args, **kwargs)


class interpolateManager:
    __interpolablePipeline = []
    DEFAULT_STEPS = 50
    DEFAULT_FRAME_DURATION = 1000/60
    @classmethod
    def interpolate(cls,obj,attributes,ends,*,frameDuration=DEFAULT_FRAME_DURATION,steps=DEFAULT_STEPS,callback=lambda:None,interpolation = lambda x:x):
        '''
        지정한 오브젝트의 속성을 서서히 변화시키는 함수입니다.\n
        obj: 변화시킬 오브젝트\n
        attributes: 변화시킬 속성 (문자열 또는 문자열 리스트)\n
        ends: 속성의 최종 값 (리스트 혹은 단일 스칼라,벡터)\n
        frameDuration: 한 프레임당 지속 시간 (기본값: 1000/60 밀리초)\n
        steps: 변화시킬 단계 수 (기본값: 50)\n
        callback: 변화가 끝났을 때 호출할 함수 (기본값: 빈 함수)\n
        interpolation: 보간 함수 (기본값: 선형 보간)

        '''
        # attributes가 리스트나 튜플이 아니면 리스트로 변환
        if not isinstance(attributes, (list, tuple)):
            attributes = [attributes]
            ends = [ends]
        t_s = np.linspace(0,1,steps)
        insts = {
            attr: [cls.__interpolate(getattr(obj, attr), ends[i], t, interpolation) for t in t_s]
            for i, attr in enumerate(attributes)
        }
        cls.__interpolablePipeline.append({"obj":obj,"attributes":attributes,"ends":ends,"insts":insts,"timer":RTimer(frameDuration),"callback":callback,"interpolation":interpolation})
        return

    @classmethod
    def easein(cls,obj,attributes,ends,*,frameDuration=DEFAULT_FRAME_DURATION,steps=DEFAULT_STEPS,callback=lambda:None):
        '''
        점점 가속되는 보간을 수행합니다.
        '''
        cls.interpolate(obj,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback,interpolation=lambda x: x**2.5)
        return

    @classmethod
    def easeout(cls,obj,attributes,ends,*,frameDuration=DEFAULT_FRAME_DURATION,steps=DEFAULT_STEPS,callback=lambda:None):
        '''
        점점 감속되는 보간을 수행합니다.
        '''
        cls.interpolate(obj,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback,interpolation=lambda x: 1-(1-x)**2.5)
        return
    
    @classmethod
    def smooth(cls,obj,attributes,ends,*,frameDuration=DEFAULT_FRAME_DURATION,steps=DEFAULT_STEPS,callback=lambda:None):
        '''
        시작과 끝이 부드러운 보간을 수행합니다.
        '''
        cls.interpolate(obj,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback,interpolation=lambda t: t**3 * (t * (6 * t - 15) + 10))
        return

    @classmethod
    def bounce(cls,obj,attributes,ends,*,frameDuration=DEFAULT_FRAME_DURATION,steps=DEFAULT_STEPS,callback=lambda:None):
        '''
        통통 튀는 듯한 보간을 수행합니다.
        '''
        cls.interpolate(obj,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback,interpolation=cls.__bounce)
        return

    @classmethod
    def __interpolate(cls,a, b, t, interpolation=lambda x:x):
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
    def __bounce(cls, t):
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
    def _update(cls):
        '''
        시간에 따른 보간을 업데이트합니다.
        '''
        for interpolable in cls.__interpolablePipeline:
            if interpolable["timer"].isOver():
                for attr in interpolable["attributes"]:
                    setattr(interpolable["obj"],attr,interpolable["insts"][attr].pop(0))
                if len(interpolable["insts"][interpolable["attributes"][0]])==0:
                    cls.__interpolablePipeline.remove(interpolable)
                    interpolable["callback"]()
                interpolable["timer"].reset()
        return

    None 

class interpolableObj:
    
    def easein(self,attributes,ends,*,frameDuration=interpolateManager.DEFAULT_FRAME_DURATION,steps=interpolateManager.DEFAULT_STEPS,callback=lambda:None):
        interpolateManager.easein(self,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback)
        return
    
    def easeout(self,attributes,ends,*,frameDuration=interpolateManager.DEFAULT_FRAME_DURATION,steps=interpolateManager.DEFAULT_STEPS,callback=lambda:None):
        interpolateManager.easeout(self,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback)
        return
    
    def smooth(self,attributes,ends,*,frameDuration=interpolateManager.DEFAULT_FRAME_DURATION,steps=interpolateManager.DEFAULT_STEPS,callback=lambda:None):
        interpolateManager.smooth(self,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback)
        return
    
    def bounce(self,attributes,ends,*,frameDuration=interpolateManager.DEFAULT_FRAME_DURATION,steps=interpolateManager.DEFAULT_STEPS,callback=lambda:None):
        interpolateManager.bounce(self,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback)
        return
    
    def interpolate(self,attributes,ends,*,frameDuration=interpolateManager.DEFAULT_FRAME_DURATION,steps=interpolateManager.DEFAULT_STEPS,callback=lambda:None,interpolation = lambda x:x):
        interpolateManager.interpolate(self,attributes,ends,frameDuration=frameDuration,steps=steps,callback=callback,interpolation=interpolation)
        return