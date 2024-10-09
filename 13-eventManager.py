from REMOLib import *


class EventManager:
    __triggers = {}
    __events = {}
    __event_counters = {}

    @classmethod
    def activateTrigger(cls, *triggers):
        """
        여러 트리거를 한 번에 활성화하는 클래스 메서드.
        """
        for trigger in triggers:
            cls.__triggers[trigger] = True

    @classmethod
    def disableTrigger(cls, *triggers):
        """
        여러 트리거를 한 번에 비활성화하는 클래스 메서드.
        """
        for trigger in triggers:
            cls.__triggers[trigger] = False

    @classmethod
    def checkTrigger(cls, *triggers, operation="and"):
        """
        트리거들을 AND/OR 조건에 따라 확인하는 클래스 메서드.
        :param operation: "and" 또는 "or" (기본값은 "and")
        :param *triggers: 확인할 트리거 리스트
        :return: AND 연산일 경우 모두 True면 True, OR 연산일 경우 하나라도 True면 True
        """
        if operation == "and":
            return all(cls.__triggers.get(trigger, False) for trigger in triggers)
        elif operation == "or":
            return any(cls.__triggers.get(trigger, False) for trigger in triggers)
        else:
            raise ValueError("operation must be 'and' or 'or'")

    @classmethod
    def addEvent(cls, event_name, listener):
        """
        새로운 이벤트 리스너를 특정 이벤트에 추가합니다.
        :param event_name: 이벤트의 이름 또는 키.
        :param listener: 이벤트가 발생할 때 호출될 함수(리스너).
        """
        if event_name not in cls.__events:
            cls.__events[event_name] = []
            cls.__event_counters[event_name] = 0  # 이벤트 카운터 초기화
        cls.__events[event_name].append(listener)

    @classmethod
    def occurEvent(cls, event_name, *args, required_triggers=None, trigger_operation="and", **kwargs):
        """
        특정 이벤트가 발생했을 때 트리거를 확인하고, 등록된 리스너를 호출하며 카운터를 증가시킵니다.
        :param event_name: 발생한 이벤트의 이름.
        :param required_triggers: 이벤트 발생에 필요한 트리거 리스트.
        :param trigger_operation: "and" 또는 "or" (기본값은 "and")
        :param *args: 리스너에 전달될 위치 기반 인자들.
        :param **kwargs: 리스너에 전달될 키워드 기반 인자들.
        """
        # 트리거 조건 확인
        if required_triggers:
            if not cls.checkTrigger(*required_triggers, operation=trigger_operation):
                print(f"이벤트 '{event_name}'는 필요한 트리거 조건을 만족하지 않습니다.")
                return

        if event_name in cls.__events:
            cls.__event_counters[event_name] += 1
            for listener in cls.__events[event_name]:
                listener(*args, **kwargs)
        else:
            print(f"이벤트 '{event_name}'가 존재하지 않습니다.")

    @classmethod
    def getEventCount(cls, event_name):
        """
        특정 이벤트가 몇 번 호출되었는지 반환합니다.
        :param event_name: 이벤트의 이름.
        :return: 이벤트 호출 횟수.
        """
        return cls.__event_counters.get(event_name, 0)


#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        return
    def init(self):
        return
    def update(self):
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
