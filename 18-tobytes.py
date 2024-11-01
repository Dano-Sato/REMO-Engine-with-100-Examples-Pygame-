from REMOLib import *
import xxhash
import timeit





#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):

        # 테스트용 Surface 생성
        surface = pygame.Surface((1000, 1000))  # 큰 이미지로 성능 테스트
        surface.fill((255, 0, 0))  # 빨간색으로 채우기

        # 해시 함수
        def hash_surface():
            surface_bytes = pygame.image.tobytes(surface, "RGBA")
            hash_value = xxhash.xxh64(surface_bytes).hexdigest()
            return hash_value

        # timeit을 사용한 실행 시간 측정
        execution_time = timeit.timeit(hash_surface, number=20)  # 10번 반복 측정
        print(f"Execution Time: {execution_time:.5f} sec")

        self.button = imageObj("test2.png",pos=RPoint(100,100),scale=0.5)
        self.started = True
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        execution_time = timeit.timeit(self.button.draw, number=300)  # 10번 반복 측정
        print(f"Execution Time: {execution_time:.5f} sec")
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
