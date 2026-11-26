# 🏙️ Smart City Route Optimization System

A route optimization system that finds the shortest and most efficient routes between locations in a city using **Dijkstra's** and **Bellman-Ford** algorithms.

https://smart-city-route-optimization.vercel.app/
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Problem Statement

Develop a route optimization system that:
- Represents city locations as **vertices** and roads as **weighted edges**
- Implements **Dijkstra's Algorithm** for fast shortest-path queries
- Implements **Bellman-Ford Algorithm** with negative-cycle detection
- Compares performance of both algorithms across different graph sizes
- Supports **real-time traffic simulation** affecting route selection

## 🏗️ Project Structure

```
smart-city-route-optimization/
├── main.py                    # Entry point — run demos and benchmarks
├── requirements.txt           # Python dependencies
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── graph.py               # Graph data structure (vertices, edges, generators)
│   ├── algorithms.py          # Dijkstra & Bellman-Ford implementations
│   ├── benchmark.py           # Performance comparison framework
│   └── visualizer.py          # Text & matplotlib visualizations
├── tests/
│   ├── __init__.py
│   └── test_algorithms.py     # Unit tests for algorithms & graph
├── data/                      # Sample data (auto-generated)
└── output/                    # Generated plots and reports
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/smart-city-route-optimization.git
cd smart-city-route-optimization

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
# Run full demo (shortest paths, traffic, benchmarks, visualizations)
python main.py

# Run performance benchmarks only
python main.py --benchmark

# Find a specific route
python main.py --route City_Center Airport

# List all available locations
python main.py --list-locations
```

### Running Tests

```bash
python -m pytest tests/ -v
# or
python -m unittest tests.test_algorithms -v
```

## 📊 Algorithms Implemented

### 1. Dijkstra's Algorithm
- **Time Complexity:** O((V + E) log V) with a min-heap
- **Space Complexity:** O(V)
- **Strengths:** Fastest for non-negative weights; supports early exit
- **Limitation:** Cannot handle negative edge weights

### 2. Bellman-Ford Algorithm
- **Time Complexity:** O(V × E)
- **Space Complexity:** O(V)
- **Strengths:** Handles negative weights; detects negative-weight cycles
- **Limitation:** Slower than Dijkstra for large graphs

### Performance Comparison

| Vertices | Edges | Dijkstra (ms) | Bellman-Ford (ms) | Speedup |
|----------|-------|---------------|-------------------|---------|
| 10       | 20    | ~0.02         | ~0.03             | ~1.5×   |
| 100      | 400   | ~0.15         | ~1.20             | ~8×     |
| 500      | 3000  | ~1.50         | ~30.00            | ~20×    |
| 1000     | 8000  | ~4.00         | ~150.00           | ~37×    |

> *Actual values depend on hardware. Run `python main.py --benchmark` for your results.*

## 🗺️ City Graph Model

The sample city includes **16 locations** connected by **28 roads**:

```
City_Center ──MG Road──── Railway_Station ──Station Road── Museum
    │                          │                              │
 Brigade Rd              Ring Road North                Culture Drive
    │                          │                              │
Hospital ──Emergency── Stadium   Bus_Station ── Residential_B
    │                     │          │                   │
Health Ave           Fan Walk   Transit Rd        Hotel Boulevard
    │                     │          │                   │
   Mall ──Luxury── Hotel_Zone   Library ──Library Ln── Residential_A
    │                                │                        │
Airport Highway                 Knowledge Ln           Tech Highway
    │                                │                        │
 Airport                       University ──Univ Rd── Tech_Park
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multiple Algorithms** | Dijkstra and Bellman-Ford with identical interfaces |
| **Traffic Simulation** | Dynamic traffic multipliers change optimal routes |
| **Negative Cycle Detection** | Bellman-Ford detects impossible routing loops |
| **Benchmark Suite** | Automated performance comparison across graph sizes |
| **Visualization** | Matplotlib plots of networks, paths, and benchmarks |
| **Random Graph Generator** | Generate connected random cities for testing |
| **CLI Interface** | Command-line flags for different modes |

## 🛠️ Technical Details

### Data Structures
- **Adjacency List** — efficient O(V + E) storage for sparse city graphs
- **Min-Heap (Priority Queue)** — O(log V) extraction in Dijkstra
- **Dataclasses** — clean, typed representations for Vertex, Edge, and results

### Key Design Decisions
1. **Undirected graph by default** — most city roads are two-way
2. **Traffic factor** — `effective_weight = weight × traffic_factor` lets us model congestion without changing base distances
3. **Early termination** — Dijkstra exits as soon as the destination is settled; Bellman-Ford exits when no relaxation occurs in a full pass

## 📄 License

This project is licensed under the MIT License.

---

*Built as a Data Structures & Algorithms project demonstrating graph algorithms for real-world route optimization.*
