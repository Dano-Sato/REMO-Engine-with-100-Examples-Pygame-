from REMOLib import *


## 7. Settings
# 게임의 설정을 변경하는 장면을 만들어 봅시다!
# 설정 변경에 필요한 함수를 이해해 봅시다!
## 다국어 지원을 해 봅시다!

#cardLayout, cardObj, inventoryObj, catalogObj 등을 만들어보자.
#excel IO





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None



class mainScene(Scene):
    def initOnce(self):
        self.read = REMODatabase.loadExcel('db.xlsx')
        print(self.read)
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        return
    
class settingSheets():
    '''
    설정과 관련된 정보를 담고 있는 클래스입니다.
    '''

    # 각 레이블의 폰트와 크기
    label = {
        "font":None,
        "size":30
    }
    language = {
        "한국어":"ko",
        "English":"en",
        "日本語":"jp"
    }
    resolution = {
        "2560x1440":(2560,1440),
        "1920x1080":(1920,1080),
        "1280x720":(1280,720),
    }
    fullscreen = {
        "On":True,
        "Off":False
    }


class settingScene(Scene):
    '''
    게임의 설정을 변경하기 위한 씬입니다.
    '''
    __settingPipeline = {}

    @classmethod
    def appendObj(cls,obj,font='default'):
        '''
        언어 변경시 레이블의 폰트와 텍스트를 변경하기 위한 함수입니다.
        '''
        if font in cls.__settingPipeline:
            cls.__settingPipeline[font].append(obj)
        else:
            cls.__settingPipeline[font] = [obj]


    language = None
    def makeButtonLayout(self,sheet,curState=None,settingFunc=lambda:None,buttonSize=pygame.Rect(0,0,200,50),buttonColor=Cs.tiffanyBlue):
        '''
        sheet: 버튼에 연결될 옵션 {'옵션명':옵션값}
        curState: 현재 옵션 설정 상태
        settingFunc: 버튼을 눌렀을 때 실행할 함수. 인자로 선택된 옵션을 받는다.
        settingFunc(sheet,option)
        '''

        ##버튼 레이아웃 생성##
        layout = layoutObj(rect=buttonSize,isVertical=False)
            

        ##버튼 생성##
        for option in sheet:

            ##선택된 옵션은 색을 진하게, 선택되지 않은 옵션은 밝게
            if sheet[option] == curState:
                _color = Cs.dark(buttonColor)
                _enabled = False
            else:
                _color = buttonColor
                _enabled = True

            button = textButton(str(option),buttonSize,color=_color,enabled=_enabled)
                
            ##함수 제너레이터
            def f(_sheet,_option):
                def _():
                    Rs.acquireDrawLock()
                    settingFunc(_sheet,_option) ##옵션 설정 함수 실행
                    for button in layout.getChilds():
                        ##선택된 버튼은 색을 진하게, 선택되지 않은 버튼은 밝게
                        if button.text == str(_option):
                            button.color = Cs.dark(buttonColor)
                            button.enabled = False
                        else:
                            button.color = buttonColor
                            button.enabled = True
                    Rs.releaseDrawLock()
                return _
            button.connect(f(sheet,option))
            button.setParent(layout)
        

        return layout
    def initOnce(self):

        self.bg = rectObj(Rs.screen.get_rect().inflate(-100,-100),color=Cs.dark(Cs.grey),edge=5,alpha=200)
        self.title = textObj("Settings",pos=(0,0),size=40,color=Cs.white)
        self.title.midleft = RPoint(150,150)
        self.leftLayout = layoutObj(pos=(0,0),isVertical=True,spacing=20)
        self.leftLayout.pos = self.title.pos + RPoint(0,100)

        self.resolutionLabel = textObj("Resolution",pos=(0,0),size=30,color=Cs.white)
        self.resolutionLabel.setParent(self.leftLayout)
        def setResolution(sheet,option):
            Rs.setWindowRes(sheet[option])
        self.resolutionButtons = self.makeButtonLayout(settingSheets.resolution,None,setResolution)
        self.resolutionButtons.setParent(self.leftLayout)

        self.fullscreenLabel = textObj("Fullscreen",pos=(0,0),size=30,color=Cs.white)
        self.fullscreenLabel.setParent(self.leftLayout)
        def setFullscreen(sheet,option):
            Rs.setFullScreen(sheet[option])
        self.fullscreenButtons = self.makeButtonLayout(settingSheets.fullscreen,None,setFullscreen)
        self.fullscreenButtons.setParent(self.leftLayout)

        self.musicVolumeLabel = textObj("Music Volume",pos=(0,0),size=30,color=Cs.white)
        self.musicVolumeLabel.setParent(self.leftLayout)
        self.musicVolumeSlider = Rs.musicVolumeSlider(length=500,color=Cs.aquamarine)
        self.musicVolumeSlider.setParent(self.leftLayout)
        
        ##DEBUG
        Rs.playMusic("piano_calm.mp3")
        return
    def init(self):
        return
    def update(self):
        self.leftLayout.update()
        return
    def draw(self):
        self.bg.draw()
        self.title.draw()
        self.leftLayout.draw()
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
    settingScene = settingScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.settingScene)
    window.run()

    # Done! Time to quit.
