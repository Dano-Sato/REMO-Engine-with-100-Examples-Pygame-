from REMOLib import *

'''
REMOLib에 존재하는 Icons들의 Icon들을 확인하는 카탈로그입니다.
'''





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None


class catalogObj(layoutObj):
    def merge(self):
        '''
        어차피 카탈로그 안의 차일드들은 개별로 업데이트 될 일이 없기 때문에,
        레이아웃의 차일드를 미리 전부 합쳐서 그래픽 부하를 줄입니다.
        '''
        self.catalogs = []
        for child in self.getChilds():
            self.catalogs.append({"rect":child.rect,"key":child.key,"path":child.path})
        super().merge()

    def update(self):
        if not self.collideMouse():
            return
        for icon in self.catalogs:
            '''
            아이콘들의 rect를 계산하여 마우스가 아이콘 위에 있는지 확인합니다.
            아이콘 위에 있다면, 아이콘에 대한 설명을 설정합니다.
            '''
            geo = icon["rect"]
            geo = pygame.Rect(self.geometryPos.x+geo.x,self.geometryPos.y+geo.y,geo.width,geo.height)
            if geo.collidepoint(Rs.mousePos().toTuple()):
                mainScene.setIconDescription(icon)


class mainScene(Scene):
    @classmethod
    def setIconDescription(cls,icon):
        '''
        화면 우측에서 보여줄 아이콘에 대한 설명 텍스트, 그리고 대형 아이콘을 설정합니다.
        '''
        key, path = icon["key"], icon["path"]

        description = f"Icons.{key}"

        if Rs.userJustLeftClicked():
            '''
            아이콘을 클릭하면 설명을 클립보드에 복사합니다. 동시에 팝업을 띄웁니다.
            '''
            import pyperclip
            pyperclip.copy(description)
            obj = textObj(f"{description} copied to clipboard!",size=30,color=Cs.white)
            obj_bg = rectObj(obj.offsetRect.inflate(50,50),color=Cs.grey,edge=2)
            obj_bg.setParent(obj,depth=-1)
            obj.midtop = Rs.mousePos() + RPoint(0,50)
            Rs.fadeAnimation(obj,time=100)


        
        if mainScene.IconDescriptionObj != None and description == mainScene.IconDescriptionObj.text:
            return ##이미 같은 아이콘에 대한 설명이 나타나고 있을 때, 다시 설정하지 않는다.

        mainScene.bigIcon = imageObj(path,scale=2)
        mainScene.bigIcon.center = RPoint(1670,530)
        _bg = rectObj(mainScene.bigIcon.offsetRect.inflate(40,40),color=Cs.grey,edge=4)
        _bg.setParent(mainScene.bigIcon,depth=-1)

        mainScene.IconDescriptionObj = textObj(description,size=30,color=Cs.white)
        if mainScene.IconDescriptionObj.rect.width > 500:
            mainScene.IconDescriptionObj.size = 25
        mainScene.IconDescriptionObj.center = mainScene.bigIcon.midbottom+RPoint(0,80)
        bg = rectObj(mainScene.IconDescriptionObj.offsetRect.inflate(20,20),color=Cs.grey,edge=2)
        bg.setParent(mainScene.IconDescriptionObj,depth=-1)

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
                icon_bg.merge()
                count += 1

                if count == 10:
                    horiz_layout.adjustBoundary() ##레이아웃의 크기를 자식들에 맞게 조정
                    horiz_layout.merge()
                    horiz_layout.setParent(self.catalogLayout)
                    horiz_layout = catalogObj(isVertical=False)
                    count = 0
        return
    def init(self):
        return
    def update(self):
        self.catalogLayout.update()
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
