from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        texts = [f"text{i}" for i in range(30)]
        self.layout = buttonLayout(texts,RPoint(100,100))
        self.layout.bounce(["pos"],[RPoint(1000,100)],revert=True)

        self.imgs = []
        for i in range(145):
            img = imageObj("test2.png",pos=RPoint(10*i,100),scale=0.5)
            self.imgs.append(img)
            img.bounce(["pos","alpha"],[RPoint(1500,100),0],revert=True)

        self.test_angle = 120
        self.test_size = (100,100)
        self.tex_count = 0
    def init(self):
        return
    def update(self):
        self.layout.update()
        if Rs.userJustPressed(pygame.K_z):
            Rs.setWindowRes((2560,1440))
        if Rs.userJustPressed(pygame.K_x):
            if not self.layout.onInterpolation():
                self.layout.bounce(["pos"],[RPoint(1000,100)],revert=True)
            for img in self.imgs:
                if not img.onInterpolation():
                    img.bounce(["pos"],[RPoint(1500,100)],revert=True)
        if Rs.userJustPressed(pygame.K_c):
            Rs.transition(Scenes.defaultScene)
        return
    def draw(self):
        self.layout.draw()
        for img in self.imgs:
            img.draw()

    
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
    defaultScene = defaultScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(2560,1440),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
