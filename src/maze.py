import random

class Maze:
    def __init__(self, height, width):
        # 强制将尺寸调整为奇数
        self.height = height if height % 2 != 0 else height + 1
        self.width = width if width % 2 != 0 else width + 1
        
        # 初始化网格：1=墙, 0=路
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # 默认起点和终点
        self.start = (1, 1)
        self.end = (self.height - 2, self.width - 2)
        
        # 1. 基础生成 (Recursive Backtracker - Perfect Maze)
        self._generate_maze(self.start[0], self.start[1])
        
        # 确保默认起终点是通的
        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

    def _generate_maze(self, r, c):
        """递归回溯算法生成完美迷宫"""
        self.grid[r][c] = 0
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < self.height and 0 < nc < self.width and self.grid[nr][nc] == 1:
                self.grid[r + dr // 2][c + dc // 2] = 0
                self._generate_maze(nr, nc)

    def add_loops(self, factor=5.0):
        """
        随机打通一些墙壁以形成环路 (Imperfect Maze)。
        factor: 移除墙壁的百分比 (0-100)。
        """
        num_walls = int(self.height * self.width * (factor / 100))
        count = 0
        attempts = 0
        max_attempts = num_walls * 5 # 防止死循环
        
        while count < num_walls and attempts < max_attempts:
            r = random.randint(1, self.height - 2)
            c = random.randint(1, self.width - 2)
            if self.grid[r][c] == 1:
                # 简单检查：避免打通成大广场，只打通连接两条路的墙
                # 但为了简单，这里直接打通
                self.grid[r][c] = 0
                count += 1
            attempts += 1

    def add_rooms(self, count=5, min_size=3, max_size=8):
        """
        随机开辟房间 (Dungeon Maze)。
        """
        for _ in range(count):
            # 随机宽高
            h = random.randint(min_size, max_size)
            w = random.randint(min_size, max_size)
            # 随机位置
            r = random.randint(1, self.height - h - 1)
            c = random.randint(1, self.width - w - 1)
            
            # 打通矩形区域
            for i in range(r, r + h):
                for j in range(c, c + w):
                    if 0 < i < self.height-1 and 0 < j < self.width-1:
                        self.grid[i][j] = 0

    def set_start_pos(self, r, c):
        if 0 <= r < self.height and 0 <= c < self.width:
            self.start = (r, c)
            self.grid[r][c] = 0
            return True
        return False

    def set_end_pos(self, r, c):
        if 0 <= r < self.height and 0 <= c < self.width:
            self.end = (r, c)
            self.grid[r][c] = 0
            return True
        return False

    def get_neighbors(self, node, order="NWSE"):
        r, c = node
        neighbors = []
        directions = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
        for char in order:
            if char in directions:
                dr, dc = directions[char]
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if self.grid[nr][nc] == 0:
                        neighbors.append((nr, nc))
        return neighbors