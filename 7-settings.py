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

    def initOnce(self):

        self.bg = rectObj(Rs.screen.get_rect().inflate(-100,-100),color=Cs.dark(Cs.grey),edge=5,alpha=200)
        self.title = textObj("Settings",pos=(0,0),size=40,color=Cs.white)
        self.title.midleft = RPoint(150,150)
        self.leftLayout = layoutObj(pos=(0,0),isVertical=True,spacing=40)
        self.leftLayout.pos = self.title.pos + RPoint(0,100)

        self.resolutionLabel = textObj("Resolution",pos=(0,0),size=50,color=Cs.white)
        self.resolutionLabel.setParent(self.leftLayout)
        self.resolutionButtons = Rs.makeOptionLayout(settingSheets.resolution,None,lambda option:Rs.setWindowRes(option))
        self.resolutionButtons.setParent(self.leftLayout)

        self.fullscreenLabel = textObj("Fullscreen",pos=(0,0),size=50,color=Cs.white)
        self.fullscreenLabel.setParent(self.leftLayout)
        self.fullscreenButtons = Rs.makeOptionLayout(settingSheets.fullscreen,None,lambda option:Rs.setFullScreen(option))
        self.fullscreenButtons.setParent(self.leftLayout)

        self.musicVolumeLabel = textObj("Music Volume",pos=(0,0),size=50,color=Cs.white)
        self.musicVolumeLabel.setParent(self.leftLayout)
        self.musicVolumeSlider = Rs.musicVolumeSlider(length=500,color=Cs.aquamarine)
        self.musicVolumeSlider.setParent(self.leftLayout)
        
        ##DEBUG
        Rs.playMusic("night_detective.mp3")
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
    window = REMOGame(window_resolution=(2560,1440),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.settingScene)
    window.run()

    # Done! Time to quit.
