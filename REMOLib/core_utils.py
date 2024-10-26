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
    __interpolablePipeline = {}
    DEFAULT_STEPS = 50
    DEFAULT_FRAME_DURATION = 1000/60
    @classmethod
    def interpolate(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, interpolation=lambda x: x, revert=False, on_update=lambda: None):
        '''
        지정한 오브젝트의 속성을 서서히 변화시키는 함수입니다.
        obj: 변화시킬 오브젝트
        attributes: 변화시킬 속성 (문자열 또는 문자열 리스트)
        ends: 속성의 최종 값 (리스트 혹은 단일 스칼라, 벡터)
        frameDuration: 한 프레임당 지속 시간 (기본값: 1000/60 밀리초)
        steps: 변화시킬 단계 수 (기본값: 50)
        callback: 변화가 끝났을 때 호출할 함수 (기본값: 빈 함수)
        interpolation: 보간 함수 (기본값: 선형 보간)
        revert: True일 경우, 보간이 끝난 후 다시 되돌아갑니다. (역재생)
        on_update: 보간이 업데이트될 때마다 호출되는 함수
        '''
        # attributes가 리스트나 튜플이 아니면 리스트로 변환
        if not isinstance(attributes, (list, tuple)):
            attributes = [attributes]
            ends = [ends]
        
        t_s = np.linspace(0, 1, steps)
        insts = {
            attr: [cls.__interpolate(getattr(obj, attr), ends[i], t, interpolation) for t in t_s]
            for i, attr in enumerate(attributes)
        }

        # reset=True일 경우 insts를 뒤집어서 원상복구 추가
        if revert:
            for attr in insts:
                insts[attr].extend(insts[attr][::-1])  # 뒤집어서 리스트에 추가
      

        cls.__interpolablePipeline[id(obj)]={
            "obj": obj,
            "attributes": attributes,
            "ends": ends,
            "insts": insts,
            "timer": RTimer(frameDuration),
            "callback": callback,
            "interpolation": interpolation,
            "on_update": on_update
        }
        return

    @classmethod
    def easein(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        cls.interpolate(obj, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=lambda x: x**2.5, revert=revert, on_update=on_update)
        return

    @classmethod
    def easeout(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        cls.interpolate(obj, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=lambda x: 1 - (1 - x)**2.5, revert=revert, on_update=on_update)
        return
    
    @classmethod
    def smooth(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        cls.interpolate(obj, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=lambda t: t**3 * (t * (6 * t - 15) + 10), revert=revert, on_update=on_update)
        return

    @classmethod
    def jump(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        cls.interpolate(obj, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=lambda t: 4 * t * (1-t), revert=revert, on_update=on_update)
        return

    @classmethod
    def bounce(cls, obj, attributes, ends, *, frameDuration=DEFAULT_FRAME_DURATION, steps=DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        cls.interpolate(obj, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=cls.__bounce, revert=revert, on_update=on_update)
        return
    

    @classmethod
    def _update(cls):
        '''
        시간에 따른 보간을 업데이트합니다.
        '''
        keys_to_remove = []

        for obj_id, interpolable in cls.__interpolablePipeline.items():
            if interpolable["timer"].isOver():
                # 각 속성 업데이트
                for attr in interpolable["attributes"]:
                    setattr(interpolable["obj"], attr, interpolable["insts"][attr].pop(0))

                # on_update 함수를 실행하여 업데이트 이벤트 발생
                if interpolable["on_update"]:
                    interpolable["on_update"]()

                # 모든 insts가 완료되었는지 확인하고 callback 실행 후 제거
                if len(interpolable["insts"][interpolable["attributes"][0]]) == 0:
                    keys_to_remove.append(obj_id)  # 나중에 제거할 키 추적
                    if interpolable["callback"]:
                        interpolable["callback"]()

                interpolable["timer"].reset()

        # 처리 후에 사전에서 키 제거
        for key in keys_to_remove:
            del cls.__interpolablePipeline[key]
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


class interpolableObj:
    
     
    def easein(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
        점점 가속되는 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''

        interpolateManager.easein(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, revert=revert, on_update=on_update)
        return
    
    def easeout(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
        점점 감속되는 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''

        interpolateManager.easeout(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, revert=revert, on_update=on_update)
        return
    
    def smooth(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
        시작과 끝이 부드러운 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''

        interpolateManager.smooth(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, revert=revert, on_update=on_update)
        return
    
    def jump(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
        점프하는 듯한 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''

        interpolateManager.jump(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, revert=revert, on_update=on_update)
        return
    
    def bounce(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
        통통 튀는 듯한 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''


        interpolateManager.bounce(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, revert=revert, on_update=on_update)
        return
    
    def interpolate(self, attributes, ends, *, frameDuration=interpolateManager.DEFAULT_FRAME_DURATION, steps=interpolateManager.DEFAULT_STEPS, callback=lambda: None, interpolation=lambda x: x, revert=False, on_update=lambda: None):
        '''
        주어진 보간 함수를 이용해 보간을 수행합니다.

        Args:
            attributes (list or str): 보간할 속성 리스트 (예: "pos", "scale" 등).
            ends (list or value): 보간 종료 시 속성들이 도달할 값.
            frameDuration (float, optional): 한 프레임의 지속 시간 (기본값: 1000/60 ms).
            steps (int, optional): 보간이 완료될 때까지의 단계 수 (기본값: 50).
            callback (function, optional): 보간 완료 후 호출되는 함수.
            interpolation (function, optional): 보간 함수 (기본값: 선형 보간).
            revert (bool, optional): True일 경우 원래 상태로 복귀. (역재생)
            on_update (function, optional): 각 프레임마다 호출되는 함수.

        Returns:
            None
        '''
        interpolateManager.interpolate(self, attributes, ends, frameDuration=frameDuration, steps=steps, callback=callback, interpolation=interpolation, revert=revert, on_update=on_update)
        return
    
    def slidein(self, delta=RPoint(50, 0), *, speed=1.5, callback=lambda: None, revert=False, on_update=lambda: None):
        '''
            오브젝트를 슬라이딩시키며 나타나게 하는 함수.

            Args:
                delta (RPoint, optional): 시작 위치에서의 변위.
                speed (float, optional): 슬라이드 속도 조절 (기본값: 1.5).
                callback (function, optional): 슬라이드 완료 후 호출되는 함수.
                revert (bool, optional): True일 경우 슬라이드 후 원래 위치로 돌아갑니다.
                on_update (function, optional): 슬라이드가 진행되는 동안 매 프레임마다 호출되는 함수.

            Returns:
                None
        '''


        self.pos -= delta
        self.alpha = 0
        steps = int(interpolateManager.DEFAULT_STEPS // speed)
        self.easeout(["pos", "alpha"], [self.pos + delta, 255], steps=steps, callback=callback, revert=revert, on_update=on_update)


