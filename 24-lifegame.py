from REMOLib import *
from multiprocessing import Process, Queue
import time






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class cellState(Enum):
    DEAD = 0
    ALIVE = 1


class mainScene(Scene):
    grid_size = 50
    
    def randomInit(self,chance=0.5):
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                r = random.random()
                if r > chance:
                    self.setState(x,y,cellState.ALIVE)
                else:
                    self.setState(x,y,cellState.DEAD)
    def initOnce(self):
        # 그리드 초기화
        self.grid = gridObj(RPoint(100,100), tileSize=(20,20), grid=(self.grid_size,self.grid_size))
        self.randomInit()
        # 입력/출력 큐 생성
        self.input_queue = Queue()
        self.output_queue = Queue()
        
        # 계산 프로세스 시작
        self.calc_process = Process(
            target=self.calculation_loop,
            args=(self.input_queue, self.output_queue)
        )
        self.calc_process.daemon = True
        self.calc_process.start()
        
        # 초기 상태 전송
        self.send_current_state()        
        return
    
    def getState(self,x,y):
        if not hasattr(self.grid[y][x],'state'):
            self.grid[y][x].state = cellState.DEAD
        return self.grid[y][x].state
    
    def setState(self,x,y,state):
        self.grid[y][x].state = state
        if state == cellState.DEAD:
            self.grid[y][x].color = Cs.grey
        else:
            self.grid[y][x].color = Cs.white
        return

    def send_current_state(self):
        current_grid = [[self.grid[y][x].state for x in range(self.grid_size)]
                       for y in range(self.grid_size)]
        self.input_queue.put(current_grid)

    @staticmethod
    def count_neighbors(grid, x, y, grid_size):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % grid_size
                ny = (y + dy) % grid_size
                if grid[ny][nx] == cellState.ALIVE:
                    count += 1
        return count

    @staticmethod
    def calculation_loop(input_queue, output_queue):
        while True:
            current_grid = input_queue.get()
            grid_size = len(current_grid)
            cells_to_change = []
            
            for y in range(grid_size):
                for x in range(grid_size):
                    neighbors = mainScene.count_neighbors(current_grid, x, y, grid_size)
                    current = current_grid[y][x]
                    
                    if current == cellState.ALIVE:
                        if neighbors < 2 or neighbors > 3:
                            cells_to_change.append((x, y))
                    else:
                        if neighbors == 3:
                            cells_to_change.append((x, y))
            
            output_queue.put(cells_to_change)
            time.sleep(0.1)

    def update(self):
        try:
            cells_to_change = self.output_queue.get_nowait()
            for x, y in cells_to_change:
                self.setState(x,y,cellState.DEAD if self.getState(x,y) == cellState.ALIVE else cellState.ALIVE)
            self.send_current_state()
        except:
            pass

        if Rs.userIsLeftClicking():
            x, y = self.grid.getMouseIndex()
            if x != -1 and y != -1 and self.grid[y][x].state == cellState.DEAD:
                self.setState(x,y,cellState.ALIVE)

        if Rs.userJustPressed(pygame.K_r):
            self.randomInit()
        
        return

    def draw(self):
        self.grid.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="LIFE GAME")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.

