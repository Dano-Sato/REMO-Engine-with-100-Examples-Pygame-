from REMOLib import *

'''
REMOLib에 존재하는 Icons들의 Icon들을 확인하는 카탈로그입니다.
'''





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None


class catalogObj(layoutObj):
    def update(self):
        if not self.collideMouse():
            return
        for icon in self.getChilds():
            if icon.collideMouse():
                mainScene.setIconDescription(icon)


class mainScene(Scene):
    @classmethod
    def setIconDescription(cls,icon):


        description = f"Icons.{icon.key}"
        if mainScene.IconDescriptionObj != None and description == mainScene.IconDescriptionObj.text:
            return ##이미 같은 아이콘에 대한 설명이 나타나고 있을 때, 다시 설정하지 않는다.

        mainScene.bigIcon = imageObj(icon.path,scale=2)
        mainScene.bigIcon.center = RPoint(1670,530)
        _bg = rectObj(mainScene.bigIcon.offsetRect.inflate(40,40),color=Cs.grey,edge=4)
        _bg.setParent(mainScene.bigIcon,depth=-1)

        mainScene.IconDescriptionObj = textObj(description,size=30,color=Cs.white)
        if mainScene.IconDescriptionObj.rect.width > 500:
            mainScene.IconDescriptionObj.size = 25
        mainScene.IconDescriptionObj.center = mainScene.bigIcon.midbottom+RPoint(0,80)
        bg = rectObj(mainScene.IconDescriptionObj.offsetRect.inflate(20,20),color=Cs.grey,edge=2)
        bg.setParent(mainScene.IconDescriptionObj,depth=-1)
        print(f"Icon Description : {description}")

    def initOnce(self):
        self.title = textObj("REMO Icon Catalog",size=50,color=Cs.white)
        self.title.midtop = RPoint(Rs.screen.get_rect().midtop)+RPoint(0,50)
        self.description = textObj("Icons class의 Icon들을 확인하는 카탈로그입니다.",size=30,color=Cs.white)
        self.description.midtop = RPoint(self.title.rect.midbottom)+RPoint(0,20)
        self.catalogLayout = scrollLayout(pygame.Rect(20,20,950,840),isVertical=True)
        self.catalogLayout.midbottom = RPoint(Rs.screen.get_rect().midbottom)+RPoint(0,-50)


        mainScene.IconDescriptionObj = None ##아이콘에 대한 설명을 나타내는 텍스트 오브젝트
        mainScene.bigIcon = None

        # 수평 레이아웃을 초기화
        horiz_layout = catalogObj(isVertical=False)

        count = 0
        for attr in dir(Icons):
            if attr.isupper():
                '''
                Icons 클래스의 속성 중 대문자로만 이루어진 속성만을 아이콘으로 추가합니다.
                '''
                icon_path = getattr(Icons,attr)
                icon = imageObj(icon_path,scale=0.5)
                icon_bg = rectObj(icon.rect.inflate(20,20),color=Cs.grey,edge=2)
                icon.setParent(icon_bg)
                icon.center = icon_bg.offsetRect.center
                icon_bg.setParent(horiz_layout)
                icon_bg.key = attr
                icon_bg.path = icon_path
                count += 1

                if count == 10:
                    horiz_layout.adjustBoundary() ##레이아웃의 크기를 자식들에 맞게 조정
                    horiz_layout.setParent(self.catalogLayout)
                    horiz_layout = catalogObj(isVertical=False)
                    count = 0
        return
    def init(self):
        return
    def update(self):
        self.catalogLayout.update()
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        if mainScene.IconDescriptionObj:
            if not self.catalogLayout.collideMouse():
                mainScene.IconDescriptionObj=None
                mainScene.bigIcon = None
        return
    def draw(self):
        self.title.draw()
        self.description.draw()
        self.catalogLayout.draw()
        if mainScene.IconDescriptionObj!=None:
            mainScene.IconDescriptionObj.draw()
        if mainScene.bigIcon!=None:
            mainScene.bigIcon.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="REMO Icon Catalog")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.