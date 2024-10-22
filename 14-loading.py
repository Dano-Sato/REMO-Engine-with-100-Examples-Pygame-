from REMOLib import *


class loading:
    @classmethod
    def setRenderer(cls,func):
        '''
        로딩 화면을 그리는 메소드를 설정합니다.
        '''
        cls.renderLoadingScreen = func
    @classmethod
    def updateProgress(cls,progress):
        '''
        로딩 화면의 진행도를 설정합니다.
        로딩 화면이 업데이트됩니다.
        '''
        cls.progress = min(100,progress)

        Rs.events = pygame.event.get()
        cls.updateScreen()


    @classmethod
    def updateScreen(cls):
        '''
        로딩 화면을 업데이트하는 함수입니다.
        '''
        ## 필수 업데이트들 처리
        RMotion._motionUpdate() # 모션 업데이트


        ## 화면 업데이트
        Rs.screen.fill(Cs.black) ## 검은 화면
        cls.renderLoadingScreen()
        Rs._draw()
        Rs._screenCapture = Rs.screen.copy()
        Rs._screenBuffer = pygame.transform.smoothscale(Rs._screenCapture,Rs.getWindowRes())
        Rs.window.blit(Rs._screenBuffer,(0,0))
        pygame.display.flip()        

        
        pass

    @classmethod
    def init(cls):
        '''
        기본 로딩 화면을 설정합니다.
        '''
        cls.centerText = textObj("Loading...",size=70)
        cls.centerText.center = Rs.screenRect().center
        cls.progressBar = rectObj(pygame.Rect(0,0,Rs.screenRect().width,50),color=Cs.grey25)
        cls.progressBar.y = Rs.screenRect().height - cls.progressBar.rect.height - 50
        cls.renderLoadingScreen = cls.drawDefault

    @classmethod
    def drawDefault(cls):
        '''
        기본 로딩 화면을 그리는 함수입니다.
        '''
        cls.centerText.text = f"Loading... {cls.progress:.1f}%"
        cls.centerText.draw()
        cls.progressBar.width = int((Rs.screenRect().width * cls.progress)/100)
        cls.progressBar.draw()



#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        loading.init()
        objs = []
        for i in range(100000):
            # 무거운 함수들 (팩토리얼, 오브젝트 생성 등)
            math.factorial(i%1000)
            if i%100==0:
                objs.append(textObj(f"{i}",size=20))
                loading.updateProgress(i/1000)
        loading.updateProgress(100)
        self.layout = layoutObj(childs=objs)
        return
    def init(self):
        return
    def update(self):
        self.layout.update()
        return
    def draw(self):
        self.layout.draw()
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