from REMOLib import *






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

    def count_neighbors(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.grid_size
                ny = (y + dy) % self.grid_size
                if self.getState(nx,ny) == cellState.ALIVE:
                    count += 1
        return count

    def update(self):
        if Rs.userJustPressed(pygame.K_r):
            self.randomInit()

        

        next_state = {}



        # 다음 세대 계산
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                neighbors = self.count_neighbors(x, y)
                
                if self.getState(x,y) == cellState.ALIVE:  # 살아있는 셀
                    if neighbors < 2 or neighbors > 3:
                        next_state[(x,y)] = cellState.DEAD
                else:  # 죽은 셀
                    if neighbors == 3:
                        next_state[(x,y)] = cellState.ALIVE
        
        # 그리드 업데이트
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if (x,y) in next_state:
                    self.setState(x,y,next_state[(x,y)])

        if Rs.userIsLeftClicking():
            x,y = self.grid.getMouseIndex()
            if x != -1 and y != -1 and self.getState(x,y) == cellState.DEAD:
                self.setState(x,y,cellState.ALIVE)
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
