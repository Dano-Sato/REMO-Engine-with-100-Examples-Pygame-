from REMOLib import *


## 7. Settings
# 게임의 설정을 변경하는 장면을 만들어 봅시다!
# 설정 변경에 필요한 함수를 이해해 봅시다!
## 다국어 지원을 해 봅시다!

#cardLayout, cardObj, inventoryObj, catalogObj 등을 만들어보자.



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

class settingScene(Scene):
    def makeButtonLayout(self,sheet,curState,settingFunc,buttonSize=(200,50),buttonColor=Cs.tiffanyBlue):
        '''
        sheet: 버튼에 연결될 옵션 {'옵션명':옵션값}
        curState: 현재 옵션 설정 상태
        settingFunc: 버튼을 눌렀을 때 실행할 함수. 인자로 선택된 옵션을 받는다.
        settingFunc(sheet,option)
        '''

        ##버튼 레이아웃 생성##
        layout = layoutObj(isVertical=False)
            

        ##버튼 생성##
        for option in sheet:

            ##선택된 옵션은 색을 진하게, 선택되지 않은 옵션은 밝게
            if sheet[option] == curState:
                _color = Cs.dark(buttonColor)
                _hoverMode = False
            else:
                _color = buttonColor
                _hoverMode = True


            button = textButton(str(option),buttonSize,color=_color,hoverMode=_hoverMode)
                
            ##함수 제너레이터
            def f(_sheet,_option):
                def _():
                    Rs.acquireDrawLock()
                    settingFunc(_sheet,_option) ##옵션 설정 함수 실행
                    for button in layout.childs:
                        ##선택된 버튼은 색을 진하게, 선택되지 않은 버튼은 밝게
                        if button.text == str(_option):
                            button.color = Cs.dark(buttonColor)
                            button.hoverMode = False
                        else:
                            button.color = buttonColor
                            button.hoverMode = True
                    Rs.releaseDrawLock()
                return _
            button.connect(f(sheet,option))
            button.setParent(layout)

        return layout
    def initOnce(self):

        self.bg = rectObj(Rs.screen.get_rect().inflate(-100,-100),color=Cs.dark(Cs.grey),edge=5,alpha=200)
        self.title = textObj("Settings",pos=(0,0),size=40,color=Cs.white)
        self.title.midleft = RPoint(150,150)
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        self.bg.draw()
        self.title.draw()
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
