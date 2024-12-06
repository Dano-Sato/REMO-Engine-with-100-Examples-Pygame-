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
    def escape_maze(grid):
        n, m = len(grid), len(grid[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        visited = [[[False] * (1 << 6) for _ in range(m)] for _ in range(n)]  # 최대 6개의 열쇠

        # BFS 초기 상태
        queue = deque([(0, 0, 0, 0)])  # (x, y, 이동 거리, 열쇠 상태)
        visited[0][0][0] = True

        while queue:
            x, y, dist, keys = queue.popleft()

            # 목표 지점 도달
            if x == n - 1 and y == m - 1:
                return dist

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < n and 0 <= ny < m:
                    cell = grid[nx][ny]

                    # 벽은 통과할 수 없음
                    if cell == "1":
                        continue

                    # 열쇠 획득
                    if "a" <= cell <= "f":
                        new_keys = keys | (1 << (ord(cell) - ord("a")))  # 열쇠 상태 업데이트
                    else:
                        new_keys = keys

                    # 문 통과
                    if "A" <= cell <= "F":
                        if not (keys & (1 << (ord(cell) - ord("A")))):  # 필요한 열쇠가 없으면 패스
                            continue

                    # 이미 방문한 상태라면 패스
                    if not visited[nx][ny][new_keys]:
                        visited[nx][ny][new_keys] = True
                        queue.append((nx, ny, dist + 1, new_keys))

        # 도달할 수 없는 경우
        return -1

    @staticmethod
    def generate_maze(n, m, num_keys=2):
        # 초기화: 모든 칸을 벽으로 채움
        maze = [["1" for _ in range(m)] for _ in range(n)]
        
        # 방향 설정 (상, 하, 좌, 우)
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        def is_valid(nx, ny):
            return 0 <= nx < n and 0 <= ny < m and maze[nx][ny] == "1"

        def carve_path(x, y):
            maze[x][y] = "0"
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                midx, midy = x + dx // 2, y + dy // 2
                if is_valid(nx, ny):
                    maze[midx][midy] = "0"
                    carve_path(nx, ny)

        # 시작 지점에서 기본 미로 생성
        carve_path(0, 0)

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
