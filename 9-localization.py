from REMOLib import *



'''
REMO Project에서의 다국어 지원을 위한 클래스를 구상해보고 있습니다.
주로 UI에 사용되는 텍스트를 다국어로 지원하기 위한 클래스입니다.
'''

#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        db = REMODatabase.loadExcel('db.xlsx')
        REMOLocalizeManager.setLanguage("en")
        REMOLocalizeManager.importTranslations(db['ui'])
        print(db['ui'])
        self.t = textObj("",size=30)
        def centerToScreen(obj):
            obj.center = Rs.screen.get_rect().center
        self.t.localize("lang",callback=centerToScreen)

        self.t2 = textButton("",pygame.Rect(100,100,200,50),size=30)
        self.t2.localize("lang")

        self.t3 = longTextObj("",pos=RPoint(100,200),size=30)
        self.t3.localize("longText")


        return
    def init(self):
        return  
    def update(self):
        if Rs.userJustPressed(pygame.K_a):
            REMOLocalizeManager.setLanguage("kr")
        if Rs.userJustPressed(pygame.K_s):
            REMOLocalizeManager.setLanguage("en")
        self.t2.update()
        return
    def draw(self):
        self.t.draw()
        self.t2.draw()
        self.t3.draw()
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
