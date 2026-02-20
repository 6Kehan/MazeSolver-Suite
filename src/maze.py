import random

class Maze:
    def __init__(self, height, width):
        self.height = height if height % 2 != 0 else height + 1
        self.width = width if width % 2 != 0 else width + 1
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.start = (1, 1)
        self.end = (self.height - 2, self.width - 2)
        self._generate_maze(self.start[0], self.start[1])
        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

    def _generate_maze(self, r, c):
        self.grid[r][c] = 0
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < self.height and 0 < nc < self.width and self.grid[nr][nc] == 1:
                self.grid[r + dr // 2][c + dc // 2] = 0
                self._generate_maze(nr, nc)

    def add_loops(self, factor=5.0):
        num_walls = int(self.height * self.width * (factor / 100))
        for _ in range(num_walls):
            r, c = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            if self.grid[r][c] == 1: self.grid[r][c] = 0

    def add_rooms(self, count=5, min_size=3, max_size=8):
        for _ in range(count):
            h, w = random.randint(min_size, max_size), random.randint(min_size, max_size)
            r, c = random.randint(1, self.height - h - 1), random.randint(1, self.width - w - 1)
            for i in range(r, r + h):
                for j in range(c, c + w):
                    if 0 < i < self.height-1 and 0 < j < self.width-1: self.grid[i][j] = 0

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
        res = []
        dirs = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
        for char in order:
            dr, dc = dirs[char]
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width and self.grid[nr][nc] == 0:
                res.append((nr, nc))
        return res