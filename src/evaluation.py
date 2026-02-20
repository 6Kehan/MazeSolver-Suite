import matplotlib.pyplot as plt
import os
import datetime

# 简写映射
NAME_MAP = {
    "BFS": "BFS",
    "DFS": "DFS",
    "A* (Manhattan)": "A*-Man",
    "A* (Euclidean)": "A*-Euc",
    "MDP (Value Iter.)": "MDP-VI",
    "MDP (Policy Iter.)": "MDP-PI"
}

def save_evaluation_plots(data, context_info, output_dir="Evaluate"):
    """保存单次赛跑的柱状对比图 (Bar Chart)"""
    if not data: return
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    names = [NAME_MAP.get(d['name'], d['name']) for d in data]
    colors = [d['color'] for d in data]
    ts = datetime.datetime.now().strftime("%H%M%S")
    plt.switch_backend('Agg') 
    
    def _plot_bar(key, title, ylabel, suffix):
        plt.figure(figsize=(8, 5))
        plt.subplots_adjust(bottom=0.15)
        bars = plt.bar(names, [d[key] for d in data], color=colors)
        plt.title(f"{title}\n({context_info})")
        plt.ylabel(ylabel); plt.xlabel("Algorithm")
        plt.xticks(rotation=15)
        for bar in bars:
            y = bar.get_height()
            plt.text(bar.get_x()+bar.get_width()/2, y, f'{y:.1f}' if isinstance(y,float) and y<1000 else f'{int(y)}', ha='center', va='bottom', fontsize=9)
        plt.savefig(f"{output_dir}/eval_{ts}_{suffix}.png")
        plt.close()

    try:
        _plot_bar('time', "Time Complexity", "Time (ms)", "time")
        _plot_bar('nodes', "Search Space (Nodes)", "Count", "nodes")
        _plot_bar('steps', "Path Optimality", "Steps", "steps")
        print(f"Bar charts saved to {output_dir}/")
    except Exception as e: print(f"Error plotting bars: {e}")

def save_benchmark_trends(results, output_dir="Evaluate"):
    """
    【新增】保存 Benchmark 趋势折线图 (Line Chart)。
    X轴: 迷宫大小, Y轴: 指标, 线条: 不同算法
    """
    if not results: return
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    plt.switch_backend('Agg')
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 数据整理
    # 结构: data_map[algo_name] = {size: [val1, val2...]}
    sizes = sorted(list(set(r['Size'] for r in results)))
    algos = sorted(list(set(r['Algorithm'] for r in results)))
    
    # 颜色映射 (保持和 GUI 一致)
    COLOR_MAP = {
        "BFS": "blue", "DFS": "red", 
        "A* (Manhattan)": "green", "A* (Euclidean)": "magenta",
        "MDP (Value Iter.)": "orange", "MDP (Policy Iter.)": "cyan"
    }

    def _plot_line(metric_key, title, ylabel, filename):
        plt.figure(figsize=(10, 6))
        
        for algo in algos:
            # 提取该算法在不同尺寸下的平均值
            y_values = []
            x_values = []
            for size in sizes:
                # 找到所有匹配 (Algo, Size) 的记录
                matches = [r[metric_key] for r in results if r['Algorithm'] == algo and r['Size'] == size]
                if matches:
                    avg_val = sum(matches) / len(matches)
                    x_values.append(size)
                    y_values.append(avg_val)
            
            if x_values:
                label_name = NAME_MAP.get(algo, algo)
                col = COLOR_MAP.get(algo, 'black')
                plt.plot(x_values, y_values, marker='o', label=label_name, color=col, linewidth=2)

        plt.title(f"Scalability Analysis: {title}")
        plt.xlabel("Maze Size (NxN)")
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        save_path = os.path.join(output_dir, f"bench_{ts}_{filename}.png")
        plt.savefig(save_path)
        plt.close()
        print(f"Saved trend plot: {save_path}")

    try:
        _plot_line('Time_ms', "Running Time vs Map Size", "Time (ms)", "trend_time")
        _plot_line('Nodes_Expanded', "Nodes Expanded vs Map Size", "Nodes Count", "trend_nodes")
        _plot_line('Path_Length', "Path Length vs Map Size", "Steps", "trend_steps")
    except Exception as e:
        print(f"Error plotting trends: {e}")