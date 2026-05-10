# MazeSolver-Suite

[![Demo Video](https://img.shields.io/badge/Video-Demo-red)](https://youtu.be/uy2UaO0K3jc)

**MazeSolver-Suite** is an interactive maze pathfinding visualization and benchmarking platform. It integrates six search and planning algorithms with a GUI, real-time animation, and automated performance analysis tools.

## Demo

[![MazeSolver-Suite Demo](https://img.shields.io/badge/Watch-Demo%20Video-red)](https://youtu.be/uy2UaO0K3jc)

Click the badge or [this link](https://youtu.be/uy2UaO0K3jc) to see a walkthrough of the system, including maze generation, algorithm race mode, and automated benchmarking.

---

## Features

### Maze Generation
Three maze types with increasing structural complexity:
- **Perfect Maze** — Recursive backtracking algorithm. No loops, exactly one solution (tree structure).
- **Imperfect Maze** — Built on a perfect maze by randomly removing walls to create loops and multiple solutions.
- **Dungeon Maze** — Starts with randomly placed open rooms, then connects them with corridors. Highest complexity with large open areas and multiple paths.

### Search & Planning Algorithms
All six algorithms support configurable neighbor expansion priority orders (NWSE, NESW, SWNE, SENW):

| Algorithm | Type | Optimality |
|-----------|------|------------|
| **BFS** | Uninformed search (FIFO queue) | Guarantees shortest path |
| **DFS** | Uninformed search (LIFO stack) | Does not guarantee shortest path |
| **A\* — Manhattan** | Informed search (priority queue) | Guarantees shortest path |
| **A\* — Euclidean** | Informed search (priority queue) | Guarantees shortest path |
| **MDP Value Iteration** | Dynamic programming (global policy) | Global optimum |
| **MDP Policy Iteration** | Dynamic programming (policy evaluation + improvement) | Global optimum |

### GUI Features
- Adjustable maze size, type, start/end coordinates
- Checkbox selection for any combination of algorithms
- Dropdown menu for search direction priority
- **Race Mode** — Run multiple algorithms simultaneously; results are visualized as colored concentric squares on the same canvas
- Real-time animation of node expansion and final paths
- Performance results table (time, expanded nodes, path length)

### Automated Benchmarking

**Run Order Test** — Executes all 6 algorithms under 4 direction orders (NWSE, NESW, SWNE, SENW) on the current maze, generating CSV data files and trend charts.

**Run Maze Size Test** — Automatically scales maze size from 10×10 to 100×10 (step 10), runs all algorithms at each size, and produces comparison charts and CSV data.

---

## Environment Setup

```bash
pip install pandas matplotlib
```

## Quick Start

```bash
python src/gui.py
```

## Project Structure

```
MazeSolver-Suite/
├── src/
│   ├── gui.py           # Tkinter user interface
│   ├── maze.py           # Maze generator (3 types)
│   ├── search_algos.py   # 6 algorithm implementations
│   ├── evaluation.py     # Benchmarking & chart generation
│   └── __init__.py
├── data/                 # Generated CSV benchmark results
├── Evaluate/             # Generated PNG evaluation charts
└── readme.md
```

---

## Performance Insights

Extensive benchmarking (detailed in the [technical report](./CS7IS2_Assignment1_Report.pdf)) reveals:

- **A\*-Manhattan** offers the best overall balance of speed, optimality, and stability across all maze types.
- **DFS** is the fastest when search direction aligns with the goal direction, but degrades dramatically under unfavorable direction orders — up to 60× difference in runtime.
- **BFS** is the slowest search algorithm in deep mazes due to exhaustive nearest-node expansion, but reliably returns the shortest path.
- **MDP algorithms** are significantly slower than search algorithms (global vs. goal-directed), but provide a complete policy for every cell in the maze.
- Heuristic function choice matters: in a 100×100 Dungeon maze, A\*-Manhattan was nearly 2× faster than A\*-Euclidean due to better alignment with the 4-direction movement model.
