from REMOLib import *



'''
REMO Project에서의 다국어 지원을 위한 클래스를 구상해보고 있습니다.
'''

class REMOLocalizeManager:
    '''
    REMO 프로젝트의 텍스트 번역과 폰트 등을 관리하는 클래스입니다.
    textObj, textButton, longTextObj 등에서 사용할 수 있습니다.
    '''
    __localizationPipeline = {}  # 로컬라이제이션을 관리할 오브젝트와 키를 저장
    __language = "en"            # 기본 언어는 영어로 설정
    __translations = {}          # 번역 데이터를 저장하는 딕셔너리
    __fonts = {}                # 폰트 데이터를 저장하는 딕셔너리


    @classmethod
    def setLanguage(cls, language: str):
        '''
        언어를 설정하는 함수입니다.
        '''
        cls.__language = language
        #cls.updateTexts() # 언어가 변경되면 로컬라이제이션과 관련된 모든 오브젝트의 텍스트를 업데이트합니다.

    @classmethod
    def getLanguage(cls):
        '''
        현재 언어를 반환하는 함수입니다.
        '''
        return cls.__language
    
    @classmethod
    def getFont(cls,key=None):
        '''
        폰트를 반환하는 함수입니다.
        '''
        if key==None:
            key = "default"
        if key in cls.__fonts:
            return cls.__fonts[key][REMOLocalizeManager.getLanguage()]

    @classmethod
    def manageObj(cls,obj,key,*,font=None):
        '''
        오브젝트의 텍스트를 관리하는 함수입니다.
        '''
        obj_id = id(obj)
        REMOLocalizeManager.__localizationPipeline[obj_id]={"obj":obj,"key":key,"font":font}
        REMOLocalizeManager.updateText(obj,key,font=font)
        return


    @classmethod
    def updateText(cls, obj, key,*,font=None):
        '''
        개별 오브젝트의 텍스트를 업데이트하는 함수입니다.
        폰트를 지정하면 해당 폰트로 텍스트를 업데이트합니다.
        '''
        language = cls.getLanguage()
        if language in cls.__translations and key in cls.__translations[language]:
            translated_text = cls.__translations[language][key]
            obj.text = translated_text  # 오브젝트에 번역된 텍스트를 설정하는 메서드
            obj.font = REMOLocalizeManager.getFont(font)

    @classmethod
    def updateTexts(cls):
        '''
        로컬라이제이션 파이프라인에 등록된 모든 오브젝트의 텍스트를 업데이트하는 함수입니다.
        '''
        for item in cls.__localizationPipeline:
            obj = item["obj"]
            key = item["key"]
            font = item["font"]
            cls.updateText(obj, key, font=font)

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
