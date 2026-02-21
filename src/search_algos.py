import heapq
import math
import random
from collections import deque

# ==========================================
# PART 1: Classical Search Algorithms
# ==========================================

def solve_bfs(maze, order="NWSE"):
    """
    广度优先搜索 (BFS) - Queue (FIFO)
    保证最短路径。
    """
    start = maze.start
    end = maze.end
    
    queue = deque([start])
    visited = {start}
    parent_map = {start: None}
    visited_order = [] # 记录访问顺序用于动画
    
    path = []
    found = False
    
    while queue:
        current = queue.popleft()
        visited_order.append(current)
        
        if current == end:
            found = True
            break
        
        # BFS 按照顺序将邻居加入队列
        for neighbor in maze.get_neighbors(current, order):
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                queue.append(neighbor)
    
    if found:
        path = _reconstruct_path(parent_map, end)
    return visited_order, path

def solve_dfs(maze, order="NWSE"):
    """
    深度优先搜索 (DFS) - Stack (LIFO)
    不保证最短路径，路径通常很长且蜿蜒。
    """
    start = maze.start
    end = maze.end
    
    stack = [start]
    visited = {start}
    parent_map = {start: None}
    visited_order = []
    
    path = []
    found = False
    
    while stack:
        current = stack.pop()
        visited_order.append(current)
        
        if current == end:
            found = True
            break
        
        # 获取邻居
        neighbors = maze.get_neighbors(current, order)
        
        # 【关键逻辑】Stack 是后进先出。
        # 如果用户选 order="NWSE" (优先走北)，意味着我们希望 "北" 最先被 pop 出来。
        # 为了让 "北" 在栈顶，我们需要把它最后压入栈。
        # 所以我们将邻居列表反转，变成 [东, 南, 西, 北] 的顺序压入。
        neighbors.reverse()
        
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                stack.append(neighbor)
    
    if found:
        path = _reconstruct_path(parent_map, end)
    return visited_order, path

def solve_astar_manhattan(maze, order="NWSE"):
    """A* 搜索 - 曼哈顿距离 (适合网格)"""
    return _solve_astar(maze, _heuristic_manhattan, order)

def solve_astar_euclidean(maze, order="NWSE"):
    """A* 搜索 - 欧几里得距离 (适合允许斜向移动的环境，这里作为对比)"""
    return _solve_astar(maze, _heuristic_euclidean, order)

def _solve_astar(maze, heuristic_func, order):
    start = maze.start
    end = maze.end
    
    # Priority Queue: (f_score, tie_breaker_count, node)
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    open_set_hash = {start}
    
    parent_map = {start: None}
    g_score = {start: 0} # 从起点到当前的代价
    
    visited_order = []
    path = []
    found = False
    
    while open_set:
        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)
        visited_order.append(current)
        
        if current == end:
            found = True
            break
        
        # 获取邻居 (Order 在这里主要影响 f 值相同时的平局处理)
        for neighbor in maze.get_neighbors(current, order):
            temp_g = g_score[current] + 1
            
            if neighbor not in g_score or temp_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = temp_g
                f = temp_g + heuristic_func(neighbor, end)
                
                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (f, count, neighbor))
                    open_set_hash.add(neighbor)
    
    if found:
        path = _reconstruct_path(parent_map, end)
    return visited_order, path

# ==========================================
# PART 2: MDP Algorithms
# ==========================================

# MDP 参数配置
GAMMA = 0.99        # 折扣因子 (看重未来奖励)
EPSILON = 1e-6      # 收敛阈值
REWARD_GOAL = 100   # 终点奖励
REWARD_STEP = -1    # 每步惩罚 (Living Penalty)

def solve_mdp_value(maze, order="NWSE"):
    """Value Iteration (值迭代)"""
    rows, cols = maze.height, maze.width
    end = maze.end
    
    # 1. 初始化价值表 V(s) = 0
    V = {}
    states = []
    for r in range(rows):
        for c in range(cols):
            if maze.grid[r][c] == 0:
                V[(r, c)] = 0
                states.append((r, c))
    
    # 终点价值初始化 (有助于加速收敛)
    V[end] = REWARD_GOAL

    # 2. 迭代直到收敛
    while True:
        delta = 0
        new_V = V.copy()
        
        for s in states:
            if s == end: continue 
            
            neighbors = maze.get_neighbors(s, order)
            if not neighbors: continue
            
            # Bellman Update: max( R + gamma * V(s') )
            max_val = -float('inf')
            for neighbor in neighbors:
                reward = REWARD_GOAL if neighbor == end else REWARD_STEP
                val = reward + GAMMA * V[neighbor]
                if val > max_val:
                    max_val = val
            
            new_V[s] = max_val
            delta = max(delta, abs(new_V[s] - V[s]))
            
        V = new_V
        if delta < EPSILON:
            break

    # 3. 提取策略生成路径
    path = _extract_path_from_values(maze, V, order)
    return states, path

def solve_mdp_policy(maze, order="NWSE"):
    """Policy Iteration (策略迭代)"""
    rows, cols = maze.height, maze.width
    end = maze.end
    states = [ (r,c) for r in range(rows) for c in range(cols) if maze.grid[r][c] == 0 ]

    # 1. 随机策略初始化
    policy = {} 
    V = {s: 0 for s in states}
    
    for s in states:
        if s == end: continue
        nbs = maze.get_neighbors(s, order)
        if nbs: policy[s] = random.choice(nbs)
        else: policy[s] = s

    # 2. 迭代
    is_stable = False
    while not is_stable:
        # --- 策略评估 (Policy Evaluation) ---
        while True:
            delta = 0
            for s in states:
                if s == end: continue
                next_node = policy.get(s)
                if not next_node: continue
                
                reward = REWARD_GOAL if next_node == end else REWARD_STEP
                v_new = reward + GAMMA * V[next_node]
                
                delta = max(delta, abs(v_new - V[s]))
                V[s] = v_new
            if delta < EPSILON: break
        
        # --- 策略改进 (Policy Improvement) ---
        is_stable = True
        for s in states:
            if s == end: continue
            old_action = policy.get(s)
            
            best_action = None
            max_val = -float('inf')
            
            # 使用 order 确保平局时的选择一致性
            for n in maze.get_neighbors(s, order):
                reward = REWARD_GOAL if n == end else REWARD_STEP
                val = reward + GAMMA * V[n]
                if val > max_val:
                    max_val = val
                    best_action = n
            
            policy[s] = best_action
            if old_action != best_action:
                is_stable = False

    # 3. 生成路径
    path = []
    curr = maze.start
    visited_set = set()
    while curr != end:
        path.append(curr)
        visited_set.add(curr)
        nxt = policy.get(curr)
        
        # 防止死循环或无路可走
        if not nxt or nxt in visited_set: break 
        curr = nxt
    
    path.append(end)
    return states, path

# ================= Helper Functions =================

def _reconstruct_path(parent_map, current):
    """从终点回溯到起点重构路径"""
    path = []
    while current:
        path.append(current)
        current = parent_map.get(current)
    path.reverse()
    return path

def _extract_path_from_values(maze, V, order):
    """根据价值表 V 贪婪寻找路径"""
    path = []
    curr = maze.start
    end = maze.end
    visited = set()
    
    while curr != end:
        path.append(curr)
        visited.add(curr)
        
        neighbors = maze.get_neighbors(curr, order)
        if not neighbors: break
        
        # 找价值最高的邻居
        best_n = max(neighbors, key=lambda n: V.get(n, -float('inf')))
        
        if best_n in visited: break
        curr = best_n
        
    path.append(end)
    return path

def _heuristic_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _heuristic_euclidean(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)