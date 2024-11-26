from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.i = 10
        self.size = (1000,1000)
        return
    def init(self):
        return
    def update(self):
        start = time.time() 
        for _ in range(self.i):
            self.sfx = pygame.Surface(self.size,pygame.SRCALPHA,32).convert_alpha()            
        print("init time:",time.time()-start)
        for _ in range(self.i):
            import numpy as np
            array = np.zeros((self.size[1], self.size[0], 3), dtype=np.uint8)
            self.sfx = pygame.surfarray.make_surface(array)
        print("another init time:",time.time()-start)

        return
    def draw(self):
        start = time.time() 
        for _ in range(self.i):
            self.sfx.blit(self.sfx,(0,0))       
        print("blit time:",time.time()-start)
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
