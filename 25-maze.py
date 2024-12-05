from REMOLib import *






#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None



class mainScene(Scene):
    grid_size = (20,20)
    tile_size = 20
    key_colors = [Cs.red,Cs.green,Cs.blue,Cs.yellow,Cs.purple,Cs.cyan]
    maze_color = [Cs.orange,Cs.brown]
    @staticmethod
    def generate_maze(n, m, num_keys=2):
        # 초기화: 모든 칸을 벽으로 채움
        maze = [["1" for _ in range(m)] for _ in range(n)]
        
        # 방향 설정 (상, 하, 좌, 우)
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        def is_valid(nx, ny):
            """미로 내부에서 유효한 위치인지 확인"""
            return 0 <= nx < n and 0 <= ny < m and maze[nx][ny] == "1"

        def carve_path(x, y):
            """DFS 방식으로 길을 생성"""
            maze[x][y] = "0"  # 현재 위치를 통로로 만듦
            random.shuffle(directions)  # 랜덤한 방향으로 섞음

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                midx, midy = x + dx // 2, y + dy // 2  # 중간 칸 계산

                if is_valid(nx, ny):
                    maze[midx][midy] = "0"  # 중간 칸을 통로로 설정
                    carve_path(nx, ny)  # 다음 칸으로 이동

        # 시작 지점에서 길 생성 시작
        carve_path(0, 0)

        # 열쇠와 문 배치
        empty_cells = [(x, y) for x in range(n) for y in range(m) if maze[x][y] == "0"]
        random.shuffle(empty_cells)  # 셀을 랜덤하게 섞음
        
        for i in range(num_keys):
            # 열쇠와 문을 위한 두 개의 위치 선택
            kx, ky = empty_cells.pop()
            mx, my = empty_cells.pop()
            
            # 열쇠가 문보다 먼저 나오도록 보장
            if (kx, ky) > (mx, my):
                kx, ky, mx, my = mx, my, kx, ky
            
            maze[kx][ky] = chr(ord("a") + i)  # 열쇠 배치
            maze[mx][my] = chr(ord("A") + i) # 문 배치

        # 시작점과 끝점 설정
        maze[0][0] = "0"
        maze[n-1][m-1] = "0"

        return maze

    @staticmethod
    def print_maze(maze):
        """미로 출력"""
        for row in maze:
            print("".join(row))

    def initOnce(self):
        self.maze = gridObj(RPoint(100,100),(self.tile_size,self.tile_size),self.grid_size,color=Cs.orange,spacing=(5,5))
        # 미로 생성 및 출력
        random.seed(42)  # 디버깅을 위해 고정된 시드 사용
        maze = self.generate_maze(15, 15, num_keys=3)
        self.print_maze(maze)
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        self.maze.draw()
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
