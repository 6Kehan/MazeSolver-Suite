import sys
sys.setrecursionlimit(100000) # 必须足够大

import tkinter as tk
from tkinter import ttk, messagebox
import time
import csv
import datetime
import os

from src.maze import Maze
from src.search_algos import *
from src.evaluation import save_evaluation_plots, save_benchmark_trends # 引入新函数

ALGO_COLORS = {
    "BFS": "#0000FF",            
    "DFS": "#FF0000",            
    "A* (Manhattan)": "#00FF00", 
    "A* (Euclidean)": "#FF00FF", 
    "MDP (Value Iter.)": "#FFA500", 
    "MDP (Policy Iter.)": "#00FFFF" 
}

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver Ultimate - Benchmark Edition")
        self.root.geometry("1400x900")
        
        self.rows_var = tk.StringVar(value="41")
        self.cols_var = tk.StringVar(value="41")
        self.start_x_var = tk.StringVar(value="1")
        self.start_y_var = tk.StringVar(value="1")
        self.end_x_var = tk.StringVar(value="39")
        self.end_y_var = tk.StringVar(value="39")
        
        self.search_order = tk.StringVar(value="NWSE")
        self.maze_type = tk.StringVar(value="Perfect")
        self.show_search = tk.BooleanVar(value=True)
        
        self.algo_vars = {name: tk.BooleanVar(value=(name=="BFS")) for name in ALGO_COLORS.keys()}
        
        self.current_maze = None
        self.is_running = False 
        
        self.path_px = 20
        self.wall_px = 4
        self.offset_x = 0
        self.offset_y = 0
        self.skip_frames = 1

        self._setup_ui()

    def _setup_ui(self):
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_pane.pack(fill="both", expand=True)
        
        sidebar = ttk.Frame(main_pane, width=400, padding=10)
        main_pane.add(sidebar, minsize=400)
        
        # 1. Maze Setup
        gen_group = ttk.LabelFrame(sidebar, text="1. Maze Setup", padding=10)
        gen_group.pack(fill="x", pady=5)
        
        f1 = ttk.Frame(gen_group); f1.pack(fill="x")
        ttk.Label(f1, text="Size:").pack(side="left")
        ttk.Entry(f1, textvariable=self.rows_var, width=4).pack(side="left", padx=2)
        ttk.Label(f1, text="x").pack(side="left")
        ttk.Entry(f1, textvariable=self.cols_var, width=4).pack(side="left", padx=2)
        
        f2 = ttk.Frame(gen_group); f2.pack(fill="x", pady=5)
        ttk.Label(f2, text="Type:").pack(side="left")
        ttk.Combobox(f2, textvariable=self.maze_type, values=["Perfect", "Imperfect", "Dungeon"], state="readonly", width=10).pack(side="left", padx=5)
        ttk.Button(f2, text="Generate", command=self.generate_maze).pack(side="right")
        
        f3 = ttk.Frame(gen_group); f3.pack(fill="x")
        ttk.Label(f3, text="Start:").pack(side="left")
        ttk.Entry(f3, textvariable=self.start_x_var, width=4).pack(side="left")
        ttk.Entry(f3, textvariable=self.start_y_var, width=4).pack(side="left")
        
        f4 = ttk.Frame(gen_group); f4.pack(fill="x", pady=2)
        ttk.Label(f4, text="End:").pack(side="left")
        ttk.Entry(f4, textvariable=self.end_x_var, width=4).pack(side="left")
        ttk.Entry(f4, textvariable=self.end_y_var, width=4).pack(side="left")

        # 2. Algorithms
        algo_group = ttk.LabelFrame(sidebar, text="2. Algorithms", padding=10)
        algo_group.pack(fill="x", pady=5)
        
        f5 = ttk.Frame(algo_group); f5.pack(fill="x")
        ttk.Label(f5, text="Priority:").pack(side="left")
        ttk.Combobox(f5, textvariable=self.search_order, values=["NWSE", "NESW", "SWNE", "SENW"], state="readonly", width=8).pack(side="left", padx=5)
        
        grid_f = ttk.Frame(algo_group); grid_f.pack(fill="x", pady=5)
        for i, (name, var) in enumerate(self.algo_vars.items()):
            tk.Checkbutton(grid_f, text=name, variable=var, fg=ALGO_COLORS[name]).grid(row=i//2, column=i%2, sticky="w")
        
        ttk.Checkbutton(algo_group, text="Show Search (Yellow)", variable=self.show_search).pack(anchor="w")
        self.run_btn = tk.Button(algo_group, text="RUN RACE ➤", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.run_race)
        self.run_btn.pack(fill="x", pady=5)

        # 3. Results
        res_group = ttk.LabelFrame(sidebar, text="3. Results", padding=10)
        res_group.pack(fill="both", expand=True, pady=5)
        self.tree = ttk.Treeview(res_group, columns=("A","T","N","S"), show="headings", height=8)
        for col, h in zip(("A","T","N","S"), ("Algo","Time","Nodes","Steps")): 
            self.tree.heading(col, text=h)
            self.tree.column(col, width=60)
        self.tree.pack(fill="both", expand=True)

        ttk.Button(sidebar, text="Run Full Benchmark (10-100) 📊", command=self.run_benchmark).pack(fill="x", side="bottom")

        # Display
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame)
        self.canvas = tk.Canvas(right_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

    def calculate_geometry(self):
        if not self.current_maze: return
        w_canvas = self.canvas.winfo_width()
        h_canvas = self.canvas.winfo_height()
        rows, cols = self.current_maze.height, self.current_maze.width
        n_path_cols, n_wall_cols = cols // 2, cols - (cols // 2)
        n_path_rows, n_wall_rows = rows // 2, rows - (rows // 2)
        RATIO = 6.0 
        total_units_w = n_path_cols * RATIO + n_wall_cols
        total_units_h = n_path_rows * RATIO + n_wall_rows
        unit = min((w_canvas - 20) / total_units_w, (h_canvas - 20) / total_units_h)
        if unit < 0.5: unit = 0.5
        self.wall_px = unit
        self.path_px = unit * RATIO
        actual_w = n_path_cols * self.path_px + n_wall_cols * self.wall_px
        actual_h = n_path_rows * self.path_px + n_wall_rows * self.wall_px
        self.offset_x = (w_canvas - actual_w) / 2
        self.offset_y = (h_canvas - actual_h) / 2

    def get_rect(self, r, c, scale=1.0):
        walls_before_x = (c + 1) // 2
        paths_before_x = c // 2
        x = self.offset_x + walls_before_x * self.wall_px + paths_before_x * self.path_px
        walls_before_y = (r + 1) // 2
        paths_before_y = r // 2
        y = self.offset_y + walls_before_y * self.wall_px + paths_before_y * self.path_px
        w = self.path_px if c % 2 != 0 else self.wall_px
        h = self.path_px if r % 2 != 0 else self.wall_px
        cx, cy = x + w/2, y + h/2
        sw, sh = w * scale, h * scale
        return cx - sw/2, cy - sh/2, cx + sw/2, cy + sh/2

    def generate_maze(self):
        try:
            r, c = int(self.rows_var.get()), int(self.cols_var.get())
            total = r * c
            self.skip_frames = 200 if total > 8000 else 50 if total > 2500 else 10 if total > 900 else 1
            
            self.current_maze = Maze(r, c)
            m_type = self.maze_type.get()
            if m_type == "Imperfect": self.current_maze.add_loops(6.0)
            elif m_type == "Dungeon":
                self.current_maze.add_rooms(max(3, total//200), 3, min(r,c)//4)
                self.current_maze.add_loops(3.0)
            
            sx, sy = int(self.start_x_var.get()), int(self.start_y_var.get())
            ex, ey = int(self.end_x_var.get()), int(self.end_y_var.get())
            if not (self.current_maze.set_start_pos(sy, sx) and self.current_maze.set_end_pos(ey, ex)):
                 messagebox.showwarning("Info", "Coordinates adjusted.")

            self.canvas.update()
            self.calculate_geometry()
            self.draw_maze_static()
            self._clear_results()
        except ValueError: messagebox.showerror("Error", "Check inputs")

    def _clear_results(self):
        for item in self.tree.get_children(): self.tree.delete(item)

    def draw_maze_static(self):
        self.canvas.delete("all")
        if not self.current_maze: return
        self.calculate_geometry()
        rows, cols = self.current_maze.height, self.current_maze.width
        for r in range(rows):
            for c in range(cols):
                if self.current_maze.grid[r][c] == 1:
                    x1, y1, x2, y2 = self.get_rect(r, c)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")
        x1, y1, x2, y2 = self.get_rect(*self.current_maze.start, scale=0.8)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#00FF00", outline="")
        x1, y1, x2, y2 = self.get_rect(*self.current_maze.end, scale=0.8)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FF0000", outline="")

    def run_race(self):
        if not self.current_maze or self.is_running: return
        selected = [n for n, v in self.algo_vars.items() if v.get()]
        if not selected: return
        self.is_running = True
        self.draw_maze_static()
        for item in self.tree.get_children(): self.tree.delete(item)
        
        race_data = []
        plot_data = [] 
        
        base_scale = 0.8
        for idx, name in enumerate(selected):
            solver = {"BFS":solve_bfs,"DFS":solve_dfs,"A* (Manhattan)":solve_astar_manhattan,"A* (Euclidean)":solve_astar_euclidean,"MDP (Value Iter.)":solve_mdp_value,"MDP (Policy Iter.)":solve_mdp_policy}[name]
            
            t1 = time.perf_counter()
            vis, path = solver(self.current_maze, self.search_order.get())
            t2 = time.perf_counter()
            
            time_ms = (t2-t1)*1000
            nodes_count = len(vis)
            steps_count = len(path)
            
            self.tree.insert("", "end", values=(name, f"{time_ms:.2f}", nodes_count, steps_count))
            
            race_data.append({
                "vis": vis, "path": path, 
                "color": ALGO_COLORS[name], 
                "scale": max(0.2, base_scale - idx*0.15)
            })
            
            plot_data.append({
                "name": name, "time": time_ms, "nodes": nodes_count,
                "steps": steps_count, "color": ALGO_COLORS[name]
            })

        if len(selected) > 1:
            info_str = f"Type={self.maze_type.get()}, Size={self.rows_var.get()}x{self.cols_var.get()}, Order={self.search_order.get()}"
            save_evaluation_plots(plot_data, info_str)

        if self.show_search.get(): self.animate_race_search(race_data)
        else: self.animate_race_path(race_data)

    def animate_race_search(self, data):
        max_l = max(len(d["vis"]) for d in data)
        def step(i):
            if i >= max_l: self.animate_race_path(data); return
            if i % self.skip_frames == 0:
                for d in data:
                    for idx in range(i, min(i+self.skip_frames, len(d["vis"]))):
                        n = d["vis"][idx]
                        if n != self.current_maze.start and n != self.current_maze.end:
                            x1, y1, x2, y2 = self.get_rect(n[0], n[1])
                            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FFFACD", outline="")
            self.root.after(10, step, i + self.skip_frames)
        step(0)

    def animate_race_path(self, data):
        max_l = max(len(d["path"]) for d in data)
        batch = 3 
        def step(i):
            if i >= max_l: self.is_running = False; return
            for b in range(batch):
                curr = i + b
                if curr < max_l:
                    for d in data:
                        if curr < len(d["path"]):
                            n = d["path"][curr]
                            if n != self.current_maze.start and n != self.current_maze.end:
                                x1, y1, x2, y2 = self.get_rect(n[0], n[1], scale=d["scale"])
                                self.canvas.create_rectangle(x1, y1, x2, y2, fill=d["color"], outline="")
            self.root.after(10, step, i + batch)
        step(0)

    # === 【关键修改】Benchmark 逻辑 ===
    def run_benchmark(self):
        msg = "Run Full Benchmark?\n\nScope: Size 10x10 to 100x100\nAlgorithms: ALL 6\n\nNote: This will take a few minutes because MDP is slow on large maps."
        if not messagebox.askyesno("Confirm", msg): return
        
        self.run_btn.config(text="Benchmarking...", state="disabled")
        self.root.update() # 强制刷新界面防止假死
        
        results = []
        
        # 定义所有要跑的算法
        all_algos = [
            ("BFS", solve_bfs),
            ("DFS", solve_dfs),
            ("A* (Manhattan)", solve_astar_manhattan),
            ("A* (Euclidean)", solve_astar_euclidean),
            ("MDP (Value Iter.)", solve_mdp_value),
            ("MDP (Policy Iter.)", solve_mdp_policy)
        ]
        
        # 定义测试尺寸：10, 20, ..., 100
        sizes = list(range(10, 101, 10))
        
        current_order = self.search_order.get()
        current_type = self.maze_type.get()
        
        try:
            for size in sizes:
                # 每个尺寸跑 1 次 (为了节省时间，如果是严谨实验可以跑3次)
                # 为了 Report 更好看，这里设置为 1 次即可演示趋势
                for trial in range(1):
                    # 生成临时迷宫 (不影响当前 GUI 显示)
                    m = Maze(size, size)
                    
                    # 应用迷宫类型设置
                    if current_type == "Imperfect": m.add_loops(6.0)
                    elif current_type == "Dungeon":
                        total = size*size
                        m.add_rooms(max(3, total//200), 3, min(size,size)//4)
                        m.add_loops(3.0)
                        
                    m.set_start_pos(1, 1)
                    m.set_end_pos(size-2, size-2)
                    
                    print(f"Benchmarking Size {size}...")
                    
                    for name, func in all_algos:
                        t1 = time.perf_counter()
                        v, p = func(m, order=current_order)
                        t2 = time.perf_counter()
                        
                        results.append({
                            "Size": size,
                            "Trial": trial,
                            "Algorithm": name,
                            "Time_ms": round((t2-t1)*1000, 4),
                            "Nodes_Expanded": len(v),
                            "Path_Length": len(p),
                            "Success": len(p) > 0
                        })
            
            # 保存 CSV
            if not os.path.exists("data"): os.makedirs("data")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = f"data/bench_{ts}.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
                
            # 【核心】调用折线图绘制
            save_benchmark_trends(results)
            
            messagebox.showinfo("Success", f"Benchmark Done!\n\nCSV saved to: {csv_path}\nTrend Plots saved to: Evaluate/ folder")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.run_btn.config(text="RUN RACE ➤", state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()