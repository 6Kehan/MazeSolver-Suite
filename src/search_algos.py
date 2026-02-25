import heapq
import math
import random
from collections import deque

# Search Algorithms
def solve_bfs(maze, order="NWSE"):
    """
    Breadth-First Search (BFS) - Queue (FIFO)
    Guarantees the shortest path.
    """
    start = maze.start
    end = maze.end
    
    queue = deque([start])
    visited = {start}
    parent_map = {start: None}
    visited_order = [] # Record visit order for animation
    
    path = []
    found = False
    
    while queue:
        current = queue.popleft()
        visited_order.append(current)
        
        if current == end:
            found = True
            break
        
        # BFS adds neighbors to queue in specified order
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
    Depth-First Search (DFS) - Stack (LIFO)
    Does not guarantee the shortest path.
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
        
        # Get neighbors
        neighbors = maze.get_neighbors(current, order)
        
        # Stack is Last-In-First-Out.
        # If user selects order="NWSE", it means we want "North" to be popped first.
        # To make "North" at the top of the stack, we need to push it last.
        # So we reverse the neighbor list to push in [East, South, West, North] order.
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
    """A* Search - Manhattan Distance"""
    return _solve_astar(maze, _heuristic_manhattan, order)

def solve_astar_euclidean(maze, order="NWSE"):
    """A* Search - Euclidean Distance"""
    return _solve_astar(maze, _heuristic_euclidean, order)

def _solve_astar(maze, heuristic_func, order):
    start = maze.start
    end = maze.end
    
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    open_set_hash = {start}
    
    parent_map = {start: None}
    g_score = {start: 0} # Cost from start to current node
    
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
        
        # Get neighbors and calculate g_score and f_score
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

# MDP Algorithms
# MDP parameter configuration
GAMMA = 0.99        # Discount factor
EPSILON = 1e-6      # Convergence threshold
REWARD_GOAL = 100   # Goal reward
REWARD_STEP = -1    # Step penalty

def solve_mdp_value(maze, order="NWSE"):
    """Value Iteration"""
    rows, cols = maze.height, maze.width
    end = maze.end
    
    # Initialize value table V(s) = 0
    V = {}
    states = []
    for r in range(rows):
        for c in range(cols):
            if maze.grid[r][c] == 0:
                V[(r, c)] = 0
                states.append((r, c))
    
    # Initialize end state value
    V[end] = REWARD_GOAL

    # Iterate until convergence
    while True:
        delta = 0
        new_V = V.copy()
        
        for s in states:
            if s == end: continue 
            
            neighbors = maze.get_neighbors(s, order)
            if not neighbors: continue
            
            # Bellman Update
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

    # Extract policy to generate path
    path = _extract_path_from_values(maze, V, order)
    return states, path

def solve_mdp_policy(maze, order="NWSE"):
    """Policy Iteration"""
    rows, cols = maze.height, maze.width
    end = maze.end
    states = [ (r,c) for r in range(rows) for c in range(cols) if maze.grid[r][c] == 0 ]

    # Initialize with random policy
    policy = {} 
    V = {s: 0 for s in states}
    
    for s in states:
        if s == end: continue
        nbs = maze.get_neighbors(s, order)
        if nbs: policy[s] = random.choice(nbs)
        else: policy[s] = s

    # Iteration
    is_stable = False
    while not is_stable:
        # Policy Evaluation
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
        
        # Policy Improvement
        is_stable = True
        for s in states:
            if s == end: continue
            old_action = policy.get(s)
            
            best_action = None
            max_val = -float('inf')
            
            # Use order to ensure consistent choice in case of ties
            for n in maze.get_neighbors(s, order):
                reward = REWARD_GOAL if n == end else REWARD_STEP
                val = reward + GAMMA * V[n]
                if val > max_val:
                    max_val = val
                    best_action = n
            
            policy[s] = best_action
            if old_action != best_action:
                is_stable = False

    # Generate path
    path = []
    curr = maze.start
    visited_set = set()
    while curr != end:
        path.append(curr)
        visited_set.add(curr)
        nxt = policy.get(curr)
        
        # Prevent infinite loop or no path available
        if not nxt or nxt in visited_set: break 
        curr = nxt
    
    path.append(end)
    return states, path

# Helper Functions

def _reconstruct_path(parent_map, current):
    """Reconstruct path from end to start by backtracking"""
    path = []
    while current:
        path.append(current)
        current = parent_map.get(current)
    path.reverse()
    return path

def _extract_path_from_values(maze, V, order):
    """Greedy path finding based on value table V"""
    path = []
    curr = maze.start
    end = maze.end
    visited = set()
    
    while curr != end:
        path.append(curr)
        visited.add(curr)
        
        neighbors = maze.get_neighbors(curr, order)
        if not neighbors: break
        
        # Find neighbor with highest value
        best_n = max(neighbors, key=lambda n: V.get(n, -float('inf')))
        
        if best_n in visited: break
        curr = best_n
        
    path.append(end)
    return path

def _heuristic_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _heuristic_euclidean(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)