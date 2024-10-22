from REMOLib import *


class loading:
    @classmethod
    def setLoadingScreen(cls,func):
        cls.renderLoadingScreen = func
    @classmethod
    def setProgress(cls,progress):
        cls.progress = min(100,progress)

        Rs.events = pygame.event.get()
        print(Rs.events)
        for event in Rs.events:
            if event.type == pygame.QUIT:
                REMOGame.exit()

        Rs.screen.fill(Cs.black) ## 검은 화면
        cls.renderLoadingScreen()
        Rs._draw()
        Rs._screenCapture = Rs.screen.copy()
        Rs._screenBuffer = pygame.transform.smoothscale(Rs._screenCapture,Rs.getWindowRes())
        Rs.window.blit(Rs._screenBuffer,(0,0))
        pygame.display.flip()
    @classmethod
    def defaultLoadingScreen(cls):
        print(f"Loading... {cls.progress}%")

    @classmethod
    def init(cls):
        cls.centerText = textObj("Loading...",size=100)
        cls.centerText.center = Rs.screenRect().center
        cls.progressBar = rectObj(pygame.Rect(0,0,Rs.screenRect().width,50),color=Cs.grey25)
        cls.progressBar.y = Rs.screenRect().height - cls.progressBar.rect.height - 50
        cls.renderLoadingScreen = cls.defaultLoadingScreen

    @classmethod
    def defaultLoadingScreen(cls):
        print("Test")
        Rs.screen.fill(Cs.black)
        cls.centerText.text = f"Loading... {cls.progress}%"
        cls.centerText.draw()
        cls.progressBar.width = int((Rs.screenRect().width * cls.progress)/100)
        cls.progressBar.draw()



#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        loading.init()
        for i in range(100000):
            i +=1
            print(i)
            if i%1000==0:
                loading.setProgress(i/1000)
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
