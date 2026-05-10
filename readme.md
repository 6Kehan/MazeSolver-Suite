# User Guide

### 1.1 Environment Requirements

please ensure the following dependencies are installed:

```bash
pip install pandas matplotlib
```

### 1.2 Starting the Program

Open your terminal, navigate to the project root directory, and run the main interface script:

```bash
python src/gui.py
```
---

## 2. Core Features Guide

The left side of the interface is the control panel, and the right side is the visualization canvas for the maze and paths.

### 1. Maze Setup

Here you can customize the physical environment for generating the maze:

* **Size**: Enter the width and height of the maze.
* **Type**: Select your desired maze structure from the dropdown menu.
* **Start / End**: Enter the starting and target coordinates for pathfinding.
* **Generate**: Click this button, and the right canvas will immediately generate and render a brand new maze based on your parameters.

### 2. Algorithms

In this area, select the AI pathfinding algorithms and exploration rules you want to test:

* **Priority**: Set the preferred direction order for expanding neighbor nodes via the dropdown menu.
* **Algorithm Checkboxes**: You can check any number of algorithms (from 1 to 6) to run.
* **Show Search**: When checked, the nodes expanded by the algorithm will be displayed in real-time as yellow squares during the animation (**Nodes Expanded**).

### 3. Results

* **RUN RACE**: Click the large green button, and the right canvas will dynamically demonstrate the pathfinding process of all checked algorithms. When multiple paths overlap, they will be displayed as colored concentric squares.
* **Results**: After the animation finishes, the data table in the lower left corner will immediately update to show the core performance metrics of this run. Simultaneously, it will generate visualization charts for this run, located in the `Evaluate/` directory.

---

## 3. Automated Benchmarking and Visualization

The system provides two automated testing buttons at the very bottom of the interface. **Note: These two tests will dynamically read the "Maze Type" and "Start/End" settings currently generated on your canvas.**

### Run Order Test

* **Function**: Automatically run all 6 algorithms using 4 different search direction orders (NWSE, NESW, SWNE, SENW) under the current maze.
* **Output**: After the run is complete, the system will automatically generate an `order_bench_[timestamp].csv` data file in the background, and automatically plot and save charts.

### Run Maze Size Test (10-100)

* **Function**: Automatically start from a `10x10` size and gradually increase to `100x100` with a step size of 10, running all 6 algorithms at each size.
* **Output**: After the run finishes, the system will automatically generate `bench_[Maze Type]_[timestamp].csv` in the background, along with comparison charts and CSV data.

**Data Storage Location**: All CSV data tables will be automatically saved in the `data/` folder under the project root directory, and PNG visualization charts will be automatically saved in the `Evaluate/` folder under the project root directory.