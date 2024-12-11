from REMOLib import *
import ctypes
from multiprocessing import Pool

class PickleableSurface(pygame.Surface):
    def __getstate__(self):
        return pygame.image.tobytes(self, "RGBA"), self.get_size(), self.get_flags()

    def __setstate__(self, state):
        surface_string, size, flags = state
        self.__init__(size=size, flags=flags)
        self.blit(pygame.image.frombytes(surface_string, size, "RGBA"), (0, 0))


def fill_surface(args):
    """worker function for surface filling"""
    surface = PickleableSurface(args[0])
    color, alpha = args[1]
    surface.fill((color, color, color, alpha))
    return surface
#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        # surface 크기와 개수 설정
        surface_size = (1920, 1080)
        num_surfaces = 100  # 원하는 surface 개수
        
        time_start = time.time()
        # Process Pool 생성 및 작업 분배
        with Pool() as pool:
            # 각 surface마다 다른 색상/알파값 설정
            fill_args = [
                (surface_size, (min(255, i * 25), min(255, i * 30))) 
                for i in range(num_surfaces)
            ]
            
            # 병렬 처리로 surface 생성 및 채우기
            try:
                self.surfaces = pool.map(fill_surface, fill_args)
            except Exception as e:
                print(f"Surface filling error: {e}")
                self.surfaces = []
        
        print(f"Surface filling time: {time.time() - time_start}")
        print(len(self.surfaces))

        time_start = time.time()
        old_surfaces = []
        for i in range(num_surfaces):
            surface = fill_surface((surface_size, (min(255, i * 25), min(255, i * 30))))
            old_surfaces.append(surface)
        print(f"Surface filling time (Legacy): {time.time() - time_start}")
        print(len(old_surfaces))
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
