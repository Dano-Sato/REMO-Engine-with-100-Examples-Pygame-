from REMOLib import *


"""
eventManager 클래스는 게임 내에서 발생하는 이벤트를 관리하는 클래스입니다.
eventManager의 활용 예시입니다.
"""


def testFunc(*args,a,b,**kwargs):
    print(args)
    print(a)
    print(b)
    print(kwargs)

#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class eventType(Enum):
    EVENT1 = auto()

class triggerType(Enum):
    TRIGGER1 = auto()

class mainScene(Scene):
    def initOnce(self):
        EventManager.addEvent(eventType.EVENT1, lambda a: print("EVENT1 발생!",a))
        testFunc(1,2,3,a=4,b=5,c=6)
        return
    def init(self):
        return
    def update(self):
        if Rs.userJustPressed(pygame.K_a):
            EventManager.occurEvent(eventType.EVENT1,required_triggers=[triggerType.TRIGGER1],a=5)
            if EventManager.checkTrigger(triggerType.TRIGGER1):
                print("TRIGGER1 발생!")
        if Rs.userJustPressed(pygame.K_z):
            EventManager.activateTrigger(triggerType.TRIGGER1)

        return
    def draw(self):
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
