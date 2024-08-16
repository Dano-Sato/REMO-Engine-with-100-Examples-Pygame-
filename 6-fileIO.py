from REMOLib import *
import io





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        test = "6_test.assets"
        testpath = Rs.getPath("hexagon.png")
        with open(testpath, 'rb') as file:
            data_as_binary = file.read()        
        REMODatabase.saveData(test,data_as_binary)

        data = REMODatabase.loadData(test)
        bytes = io.BytesIO(data)
        bytes.seek(0)

        self.image = pygame.image.load(bytes)

        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        Rs.screen.blit(self.image,(0,0))
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
