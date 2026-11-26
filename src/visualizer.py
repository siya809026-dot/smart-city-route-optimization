"""
Visualization module for the Smart City Route Optimization System.

Generates visual representations of:
  - City road networks (graph plots)
  - Shortest paths highlighted on the map
  - Performance comparison charts (bar charts and line plots)
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from .graph import CityGraph
from .algorithms import AllPathsResult, PathResult
from .benchmark import ComparisonResult

# Try to import matplotlib; if unavailable, disable plotting gracefully
try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for file output
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def _ensure_output_dir(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


# -------------------------------------------------------------------------
# Text-based visualization (always available)
# -------------------------------------------------------------------------

def print_path(result: PathResult) -> str:
    """Pretty-print a shortest path result."""
    lines = [
        f"┌─── {result.algorithm} Result ───",
        f"│ From : {result.source}",
        f"│ To   : {result.destination}",
    ]
    if result.found:
        lines.extend([
            f"│ Dist : {result.distance:.2f}",
            f"│ Path : {' → '.join(result.path)}",
            f"│ Time : {result.execution_time_ms:.4f} ms",
            f"│ Nodes: {result.vertices_explored} explored",
        ])
    else:
        lines.append("│ Status: No path found")
    lines.append("└" + "─" * 40)
    return "\n".join(lines)


def print_all_distances(result: AllPathsResult) -> str:
    """Print all shortest distances from a source."""
    lines = [
        f"All shortest distances from '{result.source}' ({result.algorithm})",
        "=" * 55,
        f"{'Destination':<25} {'Distance':>10} {'Path':>20}",
        "-" * 55,
    ]
    for dest in sorted(result.distances.keys()):
        dist = result.distances[dest]
        if dist == float('inf'):
            lines.append(f"  {dest:<25} {'∞':>10}")
        else:
            path = result.get_path(dest)
            path_str = " → ".join(path[-3:])  # Show last 3 stops
            if len(path) > 3:
                path_str = "... → " + path_str
            lines.append(f"  {dest:<25} {dist:>10.2f}   {path_str}")
    return "\n".join(lines)


# -------------------------------------------------------------------------
# Matplotlib-based visualization
# -------------------------------------------------------------------------

def plot_city_graph(graph: CityGraph,
                    highlight_path: Optional[List[str]] = None,
                    title: str = "City Road Network",
                    output_path: str = "output/city_graph.png") -> Optional[str]:
    """
    Plot the city graph with optional shortest-path highlighting.

    Args:
        graph: The city graph to plot
        highlight_path: Optional list of vertex names forming a path to highlight
        title: Plot title
        output_path: Where to save the image

    Returns:
        Path to saved image, or None if matplotlib is unavailable
    """
    if not HAS_MATPLOTLIB:
        print("[WARNING] matplotlib not installed — skipping graph plot.")
        return None

    _ensure_output_dir(os.path.dirname(output_path))

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # Use stored coordinates or generate a simple layout
    positions: Dict[str, Tuple[float, float]] = {}
    for name, vertex in graph.vertices.items():
        if vertex.longitude != 0 and vertex.latitude != 0:
            positions[name] = (vertex.longitude, vertex.latitude)
        else:
            import math
            idx = list(graph.vertices.keys()).index(name)
            angle = 2 * math.pi * idx / len(graph.vertices)
            positions[name] = (math.cos(angle), math.sin(angle))

    # Draw edges
    highlight_edges = set()
    if highlight_path:
        for i in range(len(highlight_path) - 1):
            highlight_edges.add((highlight_path[i], highlight_path[i + 1]))
            highlight_edges.add((highlight_path[i + 1], highlight_path[i]))

    drawn_edges: set[Tuple[str, str]] = set()
    for src in graph.adjacency_list:
        for edge in graph.adjacency_list[src]:
            pair = tuple(sorted([edge.source, edge.destination]))
            if pair in drawn_edges:
                continue
            drawn_edges.add(pair)

            x = [positions[edge.source][0], positions[edge.destination][0]]
            y = [positions[edge.source][1], positions[edge.destination][1]]

            is_highlight = (edge.source, edge.destination) in highlight_edges
            color = "#e74c3c" if is_highlight else "#bdc3c7"
            width = 3.0 if is_highlight else 1.0
            zorder = 3 if is_highlight else 1

            ax.plot(x, y, color=color, linewidth=width, zorder=zorder, alpha=0.8)

            # Edge weight label
            mid_x = (x[0] + x[1]) / 2
            mid_y = (y[0] + y[1]) / 2
            ax.text(mid_x, mid_y, f"{edge.effective_weight:.1f}",
                    fontsize=6, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                              edgecolor="gray", alpha=0.7),
                    zorder=4)

    # Draw vertices
    for name, (px, py) in positions.items():
        is_on_path = highlight_path and name in highlight_path
        is_endpoint = highlight_path and name in (highlight_path[0], highlight_path[-1])

        if is_endpoint:
            color, size = "#e74c3c", 200
        elif is_on_path:
            color, size = "#f39c12", 150
        else:
            color, size = "#3498db", 100

        ax.scatter(px, py, c=color, s=size, zorder=5, edgecolors="white", linewidth=1.5)
        ax.annotate(name.replace("_", " "), (px, py),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=7, fontweight="bold",
                    zorder=6)

    # Legend
    legend_elements = [
        mpatches.Patch(color="#3498db", label="Location"),
    ]
    if highlight_path:
        legend_elements.extend([
            mpatches.Patch(color="#e74c3c", label="Shortest Path"),
            mpatches.Patch(color="#f39c12", label="Intermediate Stop"),
        ])
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Graph plot saved to: {output_path}")
    return output_path


def plot_benchmark_comparison(results: List[ComparisonResult],
                              output_path: str = "output/benchmark_comparison.png") -> Optional[str]:
    """
    Plot benchmark comparison as a grouped bar chart + line chart.

    Args:
        results: List of ComparisonResult from benchmarking
        output_path: Where to save the image

    Returns:
        Path to saved image, or None if matplotlib is unavailable
    """
    if not HAS_MATPLOTLIB:
        print("[WARNING] matplotlib not installed — skipping benchmark plot.")
        return None

    _ensure_output_dir(os.path.dirname(output_path))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    labels = [f"V={r.num_vertices}\nE={r.num_edges}" for r in results]
    dijkstra_times = [r.dijkstra_result.avg_time_ms for r in results]
    bf_times = [r.bellman_ford_result.avg_time_ms for r in results]
    speedups = [r.speedup_factor for r in results]

    x = range(len(labels))
    width = 0.35

    # --- Bar chart ---
    bars1 = ax1.bar([i - width / 2 for i in x], dijkstra_times, width,
                    label="Dijkstra", color="#2ecc71", edgecolor="white")
    bars2 = ax1.bar([i + width / 2 for i in x], bf_times, width,
                    label="Bellman-Ford", color="#e74c3c", edgecolor="white")

    ax1.set_xlabel("Graph Size", fontsize=11)
    ax1.set_ylabel("Avg Execution Time (ms)", fontsize=11)
    ax1.set_title("Execution Time Comparison", fontsize=13, fontweight="bold")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=7)
    for bar in bars2:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=7)

    # --- Speedup line chart ---
    vertices = [r.num_vertices for r in results]
    ax2.plot(vertices, speedups, "o-", color="#9b59b6", linewidth=2,
             markersize=8, markerfacecolor="#8e44ad")
    ax2.fill_between(vertices, speedups, alpha=0.15, color="#9b59b6")
    ax2.set_xlabel("Number of Vertices", fontsize=11)
    ax2.set_ylabel("Speedup Factor (×)", fontsize=11)
    ax2.set_title("Dijkstra Speedup over Bellman-Ford", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3)
    for v, s in zip(vertices, speedups):
        ax2.annotate(f"{s:.1f}×", (v, s), textcoords="offset points",
                     xytext=(0, 12), ha="center", fontsize=9, fontweight="bold")

    fig.suptitle("Smart City Route Optimization — Algorithm Benchmark",
                 fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Benchmark plot saved to: {output_path}")
    return output_path
