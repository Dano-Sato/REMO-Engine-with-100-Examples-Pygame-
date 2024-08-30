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
    __fonts = {"default":{"en":"korean_button.ttf","kr":"korean_button.ttf","jp":"japanese_button.ttf"}} # 폰트 데이터를 저장하는 딕셔너리


    @classmethod
    def setLanguage(cls, language: str):
        '''
        언어를 설정하는 함수입니다.
        '''
        cls.__language = language
        cls._updateAllObjs() # 언어가 변경되면 로컬라이제이션과 관련된 모든 오브젝트의 텍스트를 업데이트합니다.

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
    def manageObj(cls,obj,key,*,font=None,callback=lambda obj:None):
        '''
        오브젝트의 텍스트를 관리하는 함수입니다. 이후 언어 변경이 있을 때마다 텍스트가 업데이트됩니다.
        callback을 지정하면 업데이트시 함수가 호출됩니다.
        '''
        obj_id = id(obj)
        REMOLocalizeManager.__localizationPipeline[obj_id]={"obj":obj,"key":key,"font":font,"callback":callback}
        REMOLocalizeManager._updateObj(obj,key,font=font,callback=callback)
        return


    @classmethod
    def _updateObj(cls, obj, key,*,font=None,callback=lambda obj:None):
        '''
        개별 오브젝트의 텍스트를 업데이트하는 함수입니다.
        폰트를 지정하면 해당 폰트로 텍스트를 업데이트합니다.
        '''
        language = cls.getLanguage()
        if key in cls.__translations and language in cls.__translations[key]:
            translated_text = cls.__translations[key][language]
            obj.text = translated_text  # 오브젝트에 번역된 텍스트를 설정하는 메서드
            obj.font = REMOLocalizeManager.getFont(font)
            callback(obj)

    @classmethod
    def _updateAllObjs(cls):
        '''
        로컬라이제이션 파이프라인에 등록된 모든 오브젝트의 텍스트를 업데이트하는 함수입니다.
        '''
        for key in cls.__localizationPipeline:
            item = cls.__localizationPipeline[key]
            obj = item["obj"]
            key = item["key"]
            font = item["font"]
            callback = item["callback"]
            cls._updateObj(obj, key, font=font, callback=callback)

    @classmethod
    def importTranslations(cls, translations: dict):
        '''
        번역 데이터를 가져오는 함수입니다.
        번역 데이터는 {"hello": {"en": "Hello", "kr": "안녕하세요"}}와 같은 형식으로 구성됩니다.
        '''
        cls.__translations.update(translations)

    @classmethod
    def importFonts(cls, fonts: dict):
        '''
        폰트 데이터를 가져오는 함수입니다.
        폰트 데이터는 {"default": {"en": "Arial", "kr": "맑은 고딕"}}과 같은 형식으로 구성됩니다.
        '''
        cls.__fonts.update(fonts)

    @classmethod
    def getText(cls, key: str):
        '''
        키에 해당하는 텍스트를 반환하는 함수입니다.
        '''
        language = cls.getLanguage()
        if key in cls.__translations and language in cls.__translations[key]:
            return cls.__translations[key][language]
        raise KeyError(f"Key '{key}' not found in translations for language '{language}'")

#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        db = REMODatabase.loadExcel('db.xlsx')
        REMOLocalizeManager.setLanguage("kr")
        REMOLocalizeManager.importTranslations(db['ui'])
        print(db['ui'])
        self.t = textObj("",size=30)
        def centerToScreen(obj):
            obj.center = Rs.screen.get_rect().center
        REMOLocalizeManager.manageObj(self.t,"lang",callback=centerToScreen)
        return











    def init(self):
        return  
    def update(self):
        if Rs.userJustPressed(pygame.K_a):
            REMOLocalizeManager.setLanguage("kr")
        if Rs.userJustPressed(pygame.K_s):
            REMOLocalizeManager.setLanguage("en")
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
