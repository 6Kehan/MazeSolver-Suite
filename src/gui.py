import sys
sys.setrecursionlimit(100000)  # 增加递归深度以支持更大的迷宫
import tkinter as tk
from tkinter import ttk, messagebox
import time
import csv
import datetime
import os
from src.maze import Maze
from src.search_algos import *

ALGO_COLORS = {
    "BFS": "#0000FF",            # 蓝
    "DFS": "#FF0000",            # 红
    "A* (Manhattan)": "#00FF00", # 绿
    "A* (Euclidean)": "#FF00FF", # 紫
    "MDP (Value Iter.)": "#FFA500", # 橙
    "MDP (Policy Iter.)": "#00FFFF" # 青
}

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver Ultimate - Race & Benchmark")
        self.root.geometry("1400x900")
        
        self.rows_var = tk.StringVar(value="41")
        self.cols_var = tk.StringVar(value="41")
        self.start_x_var = tk.StringVar(value="1")
        self.start_y_var = tk.StringVar(value="1")
        self.end_x_var = tk.StringVar(value="39")
        self.end_y_var = tk.StringVar(value="39")
        
        self.search_order = tk.StringVar(value="NWSE")
        
        # 【新增】迷宫类型变量
        self.maze_type = tk.StringVar(value="Perfect")
        
        self.algo_vars = {
            "BFS": tk.BooleanVar(value=True),
            "DFS": tk.BooleanVar(),
            "A* (Manhattan)": tk.BooleanVar(),
            "A* (Euclidean)": tk.BooleanVar(),
            "MDP (Value Iter.)": tk.BooleanVar(),
            "MDP (Policy Iter.)": tk.BooleanVar()
        }
        
        self.current_maze = None
        self.cell_size = 20
        self.is_running = False 
        
        self.animation_speed = 10
        self.skip_frames = 1
        self.show_search = tk.BooleanVar(value=True)

        self._setup_ui()

    def _setup_ui(self):
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_pane.pack(fill="both", expand=True)
        
        sidebar = ttk.Frame(main_pane, width=400, relief="flat")
        main_pane.add(sidebar, minsize=400)
        content_frame = ttk.Frame(sidebar, padding=10)
        content_frame.pack(fill="both", expand=True)

        # --- 1. Maze Setup ---
        gen_group = ttk.LabelFrame(content_frame, text="1. Maze Setup", padding=10)
        gen_group.pack(fill="x", pady=(0, 10))
        
        # Size
        gf = ttk.Frame(gen_group)
        gf.pack(fill="x")
        ttk.Label(gf, text="Size (RxC):").pack(side="left")
        ttk.Entry(gf, textvariable=self.rows_var, width=4).pack(side="left", padx=2)
        ttk.Label(gf, text="x").pack(side="left")
        ttk.Entry(gf, textvariable=self.cols_var, width=4).pack(side="left", padx=2)
        
        # 【修改】迷宫类型选择 (Combobox)
        type_frame = ttk.Frame(gen_group)
        type_frame.pack(fill="x", pady=5)
        ttk.Label(type_frame, text="Type:").pack(side="left")
        types = ["Perfect", "Imperfect", "Dungeon"]
        ttk.Combobox(type_frame, textvariable=self.maze_type, values=types, state="readonly", width=12).pack(side="left", padx=5)
        
        ttk.Button(type_frame, text="Generate", command=self.generate_maze).pack(side="right")
        
        # Start/End
        cf = ttk.Frame(gen_group)
        cf.pack(fill="x", pady=5)
        ttk.Label(cf, text="Start:").pack(side="left")
        ttk.Entry(cf, textvariable=self.start_x_var, width=3).pack(side="left")
        ttk.Entry(cf, textvariable=self.start_y_var, width=3).pack(side="left")
        ttk.Label(cf, text=" End:").pack(side="left", padx=(10,0))
        ttk.Entry(cf, textvariable=self.end_x_var, width=3).pack(side="left")
        ttk.Entry(cf, textvariable=self.end_y_var, width=3).pack(side="left")

        # --- 2. Algorithms ---
        algo_group = ttk.LabelFrame(content_frame, text="2. Select Algorithms (Race Mode)", padding=10)
        algo_group.pack(fill="x", pady=(0, 10))
        
        df = ttk.Frame(algo_group)
        df.pack(fill="x", pady=(0,5))
        ttk.Label(df, text="Priority:").pack(side="left")
        ttk.Combobox(df, textvariable=self.search_order, values=["NWSE", "NESW", "SWNE", "SENW"], width=8, state="readonly").pack(side="left", padx=5)
        
        grid_f = ttk.Frame(algo_group)
        grid_f.pack(fill="x")
        i = 0
        for name, var in self.algo_vars.items():
            color = ALGO_COLORS.get(name, "black")
            chk = tk.Checkbutton(grid_f, text=name, variable=var, fg=color) 
            chk.grid(row=i//2, column=i%2, sticky="w", padx=5)
            i += 1
            
        opt_f = ttk.Frame(algo_group)
        opt_f.pack(fill="x", pady=5)
        ttk.Checkbutton(opt_f, text="Show Search Process (Yellow Area)", variable=self.show_search).pack(side="left")
        
        self.run_btn = tk.Button(algo_group, text="RUN RACE ➤", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.run_race)
        self.run_btn.pack(fill="x", pady=5)

        # --- 3. Results ---
        res_group = ttk.LabelFrame(content_frame, text="3. Race Results", padding=10)
        res_group.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("Algo", "Time(ms)", "Nodes", "Steps")
        self.tree = ttk.Treeview(res_group, columns=columns, show="headings", height=8)
        self.tree.heading("Algo", text="Algorithm")
        self.tree.heading("Time(ms)", text="Time")
        self.tree.heading("Nodes", text="Expanded")
        self.tree.heading("Steps", text="Path Len")
        self.tree.column("Algo", width=100); self.tree.column("Time(ms)", width=70)
        self.tree.column("Nodes", width=60); self.tree.column("Steps", width=60)
        self.tree.pack(fill="both", expand=True)

        # --- 4. Tools ---
        bench_group = ttk.LabelFrame(content_frame, text="4. Tools", padding=10)
        bench_group.pack(fill="x", side="bottom")
        ttk.Button(bench_group, text="Run Benchmark & Save CSV 📊", command=self.run_benchmark).pack(fill="x")

        # --- Display ---
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame)
        self.canvas = tk.Canvas(right_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

    def generate_maze(self):
        try:
            r, c = int(self.rows_var.get()), int(self.cols_var.get())
            total_cells = r * c
            if total_cells > 8000: self.skip_frames = 200
            elif total_cells > 2500: self.skip_frames = 50
            elif total_cells > 900: self.skip_frames = 10
            else: self.skip_frames = 1
            
            sx, sy = 1, 1
            ex, ey = r-2, c-2
            self.start_x_var.set(str(sx)); self.start_y_var.set(str(sy))
            self.end_x_var.set(str(ex)); self.end_y_var.set(str(ey))
            
            # 创建迷宫
            self.current_maze = Maze(r, c)
            
            # 【修改】根据类型应用不同的生成策略
            m_type = self.maze_type.get()
            if m_type == "Imperfect":
                self.current_maze.add_loops(factor=6.0) # 6% 的墙被打通
            elif m_type == "Dungeon":
                # 计算房间数量，迷宫越大房间越多
                num_rooms = max(3, total_cells // 200) 
                self.current_maze.add_rooms(count=num_rooms, min_size=3, max_size=min(r,c)//4)
                self.current_maze.add_loops(factor=3.0) # 地牢也要通一点，增加连通性
            
            self.current_maze.set_start_pos(sy, sx)
            self.current_maze.set_end_pos(ey, ex)
            
            self.draw_maze_static()
            self._clear_results()
            
        except ValueError: messagebox.showerror("Error", "Check inputs")

    def _clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def draw_maze_static(self):
        self.canvas.delete("all")
        if not self.current_maze: return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        rows, cols = self.current_maze.height, self.current_maze.width
        self.cell_size = min((w-20)//cols, (h-20)//rows, 40)
        if self.cell_size < 1: self.cell_size = 1
        x_off = (w - cols*self.cell_size)//2
        y_off = (h - rows*self.cell_size)//2
        self.origin = (x_off, y_off)
        for r in range(rows):
            for c in range(cols):
                if self.current_maze.grid[r][c] == 1:
                    self._draw_cell(r, c, "black", scale=1.0)
        self._draw_cell(*self.current_maze.start, "#00FF00", scale=0.9)
        self._draw_cell(*self.current_maze.end, "#FF0000", scale=0.9)

    def _draw_cell(self, r, c, color, scale=1.0):
        x_off, y_off = self.origin
        cx = x_off + c*self.cell_size + self.cell_size/2
        cy = y_off + r*self.cell_size + self.cell_size/2
        hs = (self.cell_size*scale)/2
        self.canvas.create_rectangle(cx-hs, cy-hs, cx+hs, cy+hs, fill=color, outline="")

    def run_race(self):
        if not self.current_maze or self.is_running: return
        selected = [name for name, var in self.algo_vars.items() if var.get()]
        if not selected: messagebox.showwarning("Warning", "Select at least one algorithm!"); return
        self.is_running = True
        self.draw_maze_static() 
        self._clear_results()
        order = self.search_order.get()
        solver_map = {
            "BFS": solve_bfs, "DFS": solve_dfs,
            "A* (Manhattan)": solve_astar_manhattan, "A* (Euclidean)": solve_astar_euclidean,
            "MDP (Value Iter.)": solve_mdp_value, "MDP (Policy Iter.)": solve_mdp_policy
        }
        race_data = []
        base_scale = 0.8
        scale_step = 0.15
        for idx, name in enumerate(selected):
            func = solver_map.get(name)
            t1 = time.perf_counter()
            visited, path = func(self.current_maze, order=order)
            t2 = time.perf_counter()
            self.tree.insert("", "end", values=(name, f"{(t2-t1)*1000:.2f}", len(visited), len(path)))
            current_scale = max(0.2, base_scale - (idx * scale_step))
            race_data.append({
                "name": name, "visited": visited, "path": path,
                "color": ALGO_COLORS.get(name, "gray"), "scale": current_scale
            })
        if self.show_search.get():
            self.animate_race_search(race_data)
        else:
            self.animate_race_path(race_data)

    def animate_race_search(self, race_data):
        max_len = max(len(d["visited"]) for d in race_data)
        def step(i):
            if i >= max_len: self.animate_race_path(race_data); return
            if i % self.skip_frames == 0 or i == max_len - 1:
                for data in race_data:
                    start_idx = i
                    end_idx = min(i + self.skip_frames, len(data["visited"]))
                    for idx in range(start_idx, end_idx):
                        node = data["visited"][idx]
                        if node != self.current_maze.start and node != self.current_maze.end:
                            self._draw_cell(node[0], node[1], "#FFFACD", scale=1.0) # Light Yellow
            self.root.after(10, step, i + self.skip_frames)
        step(0)

    def animate_race_path(self, race_data):
        """动画阶段2：并行显示最终路径 (已加速版)"""
        max_len = max(len(d["path"]) for d in race_data)
        
        # --- 【加速配置】 ---
        # 想要多快？修改这个 batch_size
        # 1 = 原速, 3 = 3倍速, 5 = 飞快
        batch_size = 3  
        
        def step(i):
            if i >= max_len:
                self.is_running = False
                return

            # 内层循环：每一帧画 batch_size 步
            for offset in range(batch_size):
                curr_i = i + offset
                if curr_i >= max_len: break
                
                for data in race_data:
                    if curr_i < len(data["path"]):
                        node = data["path"][curr_i]
                        if node != self.current_maze.start and node != self.current_maze.end:
                            self._draw_cell(node[0], node[1], data["color"], scale=data["scale"])
            
            # 延迟从 30ms 降低到 10ms
            self.root.after(10, step, i + batch_size)
            
        step(0)

    def run_benchmark(self):
        if not messagebox.askyesno("Confirm", "Run Benchmark? (Sizes: 10, 20, 30, 40)\nThis may take a minute."): return
        sizes = [10, 20, 30, 40]
        results = []
        order = self.search_order.get()
        solver_map = {
            "BFS": solve_bfs, "DFS": solve_dfs,
            "A*_Man": solve_astar_manhattan, "A*_Euc": solve_astar_euclidean,
            "MDP_V": solve_mdp_value, "MDP_P": solve_mdp_policy
        }
        self.run_btn.config(text="Benchmarking...", state="disabled")
        self.root.update()
        try:
            for size in sizes:
                for trial in range(1, 4):
                    m = Maze(size, size)
                    # Benchmark 默认使用 Perfect Maze (可修改)
                    m.set_start_pos(1, 1); m.set_end_pos(size-2, size-2)
                    print(f"Benchmarking Size {size} Trial {trial}...")
                    for name, func in solver_map.items():
                        t1 = time.perf_counter()
                        v, p = func(m, order=order)
                        t2 = time.perf_counter()
                        results.append({
                            "Size": size, "Trial": trial, "Algorithm": name, "Direction": order,
                            "Time_ms": round((t2-t1)*1000, 4), "Nodes_Expanded": len(v), "Path_Length": len(p), "Success": len(p) > 0
                        })
            output_dir = "data"
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{ts}.csv"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            messagebox.showinfo("Success", f"Data saved to:\n{filepath}")
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: self.run_btn.config(text="RUN RACE ➤", state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()