from collections import deque

from REMOLib import *


class Obj:
    """게임 오브젝트 플레이스홀더."""


class mainScene(Scene):
    grid_size = (21, 21)  # (가로, 세로)
    tile_size = 28

    def initOnce(self):
        self.grid_spacing = (4, 4)
        self.grid_origin = RPoint(100, 120)

        # 색상 정의
        self.path_color = Cs.grey75
        self.wall_color = Cs.black
        self.visited_color = Cs.cornflowerblue
        self.start_color = Cs.limegreen
        self.goal_color = Cs.tomato
        self.goal_cleared_color = Cs.gold
        self.player_color = Cs.deepskyblue

        # 미로를 그릴 그리드 오브젝트 생성
        self.maze = gridObj(
            self.grid_origin,
            (self.tile_size, self.tile_size),
            self.grid_size,
            color=self.path_color,
            spacing=self.grid_spacing,
        )
        self.maze.adjustLayout()

        # UI 요소
        info_pos_y = self.grid_origin.y - 60
        self.info_label = textObj(
            "WASD로 이동 / R로 새 미로",
            pos=(self.grid_origin.x, info_pos_y),
            size=30,
        )

        grid_height = (
            self.grid_size[1] * self.tile_size
            + (self.grid_size[1] - 1) * self.grid_spacing[1]
        )
        footer_y = self.grid_origin.y + grid_height + 30

        self.status_label = textObj(
            "탈출구에 도달하세요!",
            pos=(self.grid_origin.x, footer_y),
            size=26,
        )
        self.step_label = textObj(
            "이동 횟수: 0",
            pos=(self.grid_origin.x, footer_y + 40),
            size=24,
        )
        self.best_label = textObj(
            "",
            pos=(self.grid_origin.x, footer_y + 70),
            size=24,
        )

        self.goal_cell = (self.grid_size[0] - 1, self.grid_size[1] - 1)

        self.reset_game()
        return

    @staticmethod
    def escape_maze(grid):
        n, m = len(grid), len(grid[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        visited = [[False for _ in range(m)] for _ in range(n)]

        queue = deque([(0, 0, 0)])  # (y, x, 이동 거리)
        visited[0][0] = True

        while queue:
            y, x, dist = queue.popleft()

            if (x, y) == (m - 1, n - 1):
                return dist

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < n and 0 <= nx < m:
                    if grid[ny][nx] != "1" and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((ny, nx, dist + 1))

        return -1

    @staticmethod
    def generate_maze(rows, cols):
        maze = [["1" for _ in range(cols)] for _ in range(rows)]
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        def is_valid(ny, nx):
            return 0 <= ny < rows and 0 <= nx < cols and maze[ny][nx] == "1"

        def carve_path(y, x):
            maze[y][x] = "0"
            random.shuffle(directions)
            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                my, mx = y + dy // 2, x + dx // 2
                if is_valid(ny, nx):
                    maze[my][mx] = "0"
                    carve_path(ny, nx)

        carve_path(0, 0)
        return maze

    def ensure_exit_accessible(self):
        gx, gy = self.goal_cell
        self.maze_data[gy][gx] = "0"

        # 출구 인접 칸이 모두 벽일 경우 통로를 연결한다.
        if gx > 0 and self.maze_data[gy][gx - 1] == "0":
            return
        if gy > 0 and self.maze_data[gy - 1][gx] == "0":
            return

        if gx > 0:
            self.maze_data[gy][gx - 1] = "0"
        if gy > 0:
            self.maze_data[gy - 1][gx] = "0"

    def reset_game(self):
        rows, cols = self.grid_size[1], self.grid_size[0]
        self.maze_data = self.generate_maze(rows, cols)
        self.maze_data[0][0] = "0"
        self.ensure_exit_accessible()

        self.player_pos = [0, 0]
        self.visited = {tuple(self.player_pos)}
        self.steps = 0
        self.game_cleared = False

        self.best_path_length = self.escape_maze(self.maze_data)
        if self.best_path_length != -1:
            self.best_label.text = f"최단 이동 횟수: {self.best_path_length}"
        else:
            self.best_label.text = "탈출 경로를 찾을 수 없습니다."

        self.status_label.text = "탈출구에 도달하세요!"
        self.step_label.text = "이동 횟수: 0"

        self.update_tile_colors()

    def is_walkable(self, x, y):
        cols, rows = self.grid_size
        return 0 <= x < cols and 0 <= y < rows and self.maze_data[y][x] != "1"

    def try_move(self, dx, dy):
        if self.game_cleared:
            return

        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy

        if not self.is_walkable(nx, ny):
            return

        self.player_pos = [nx, ny]
        self.visited.add((nx, ny))
        self.steps += 1
        self.step_label.text = f"이동 횟수: {self.steps}"

        if (nx, ny) == self.goal_cell:
            self.game_cleared = True
            self.status_label.text = "탈출 성공! R을 눌러 새로운 미로를 만들어보세요."
        else:
            self.status_label.text = "탈출구에 도달하세요!"

        self.update_tile_colors()

    def update_tile_colors(self):
        for y, row in enumerate(self.maze_data):
            for x, cell in enumerate(row):
                tile = self.maze[y][x]
                if cell == "1":
                    tile.color = self.wall_color
                else:
                    tile.color = self.path_color
                    if (x, y) in self.visited:
                        tile.color = self.visited_color

        start_tile = self.maze[0][0]
        start_tile.color = self.start_color

        gx, gy = self.goal_cell
        exit_tile = self.maze[gy][gx]
        exit_tile.color = (
            self.goal_cleared_color if self.game_cleared else self.goal_color
        )

        px, py = self.player_pos
        player_tile = self.maze[py][px]
        player_tile.color = self.player_color

    def init(self):
        return

    def update(self):
        if Rs.userJustPressed(pygame.K_w):
            self.try_move(0, -1)
        if Rs.userJustPressed(pygame.K_s):
            self.try_move(0, 1)
        if Rs.userJustPressed(pygame.K_a):
            self.try_move(-1, 0)
        if Rs.userJustPressed(pygame.K_d):
            self.try_move(1, 0)

        if Rs.userJustPressed(pygame.K_r):
            self.reset_game()

        return

    def draw(self):
        Rs.fillScreen(Cs.black)
        self.maze.draw()
        self.info_label.draw()
        self.status_label.draw()
        self.step_label.draw()
        if self.best_label.text:
            self.best_label.draw()
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


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=(1920, 1080),
        screen_size=(2560, 1440),
        fullscreen=False,
        caption="미로 탈출",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
