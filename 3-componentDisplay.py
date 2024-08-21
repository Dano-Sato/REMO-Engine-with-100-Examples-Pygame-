###레모 엔진의 기본적인 컴포넌트들을 보여주는 예제
##주석 작업은 하기 전.


from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.image = imageObj("vampire1_default.png",pos=RPoint(1100,200))
        self.imageShadow = Rs.copyImage(self.image)
        self.imageShadow.colorize(Cs.grey,alpha=150)
        self.imageShadow.pos = self.image.pos+RPoint(10,10)
        self.text = textObj("Vampire Radia",pos=(300,-20),size=40,color=Cs.red)
        self.text.colorize(Cs.dark(Cs.grey))
        self.text.setParent(self.image)
        self.longTextBg = rectObj(pygame.Rect(140,140,1100,800),color=Cs.dark(Cs.grey),edge=5,alpha=225)
        self.name = textObj("Name: Radia",size=50)
        self.description = longTextObj("Radia is so cute, but she is 500 years old. She loves chess. 에라 모르겠다 그냥 아무글이나 좀 써보자 내가 아는 사람 얘기해 줄게 며칠전 사랑하던 그녀와 헤어진 그냥 아는 사람",
                                       textWidth=850,size=25)
        self.stats = textObj("공격력:1235,방어력:352,어쩌고 저쩌고",size=25)        
        self.textLayout = layoutObj(pos=(120,120),childs=[self.name,self.description,self.stats],spacing=30)
        self.textLayout.setParent(self.longTextBg)

        self.buttons = buttonLayout(["싸운다","도망친다","쓰다듬는다","게임 종료"],pos=RPoint(120,600),isVertical=False)
        self.buttons.setParent(self.longTextBg)
        self.buttons["싸운다"].connect(lambda:print("싸운다"))
        self.buttons.싸운다.color = Cs.red
        self.buttons.게임_종료.connect(lambda:REMOGame.exit())
        return
    def init(self):
        return
    def update(self):
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        self.buttons.update()
        return
    def draw(self):
        self.imageShadow.draw()
        self.image.draw()
        self.longTextBg.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DP")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
