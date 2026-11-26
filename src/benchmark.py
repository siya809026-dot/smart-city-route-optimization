"""
Performance benchmarking module.

Compares Dijkstra's and Bellman-Ford algorithms across different graph sizes
and generates detailed performance reports.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .graph import CityGraph, generate_random_city
from .algorithms import dijkstra, bellman_ford


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    algorithm: str
    num_vertices: int
    num_edges: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    median_time_ms: float
    std_dev_ms: float
    num_runs: int


@dataclass
class ComparisonResult:
    """Side-by-side comparison of two algorithms."""
    num_vertices: int
    num_edges: int
    dijkstra_result: BenchmarkResult
    bellman_ford_result: BenchmarkResult
    speedup_factor: float  # How many times faster Dijkstra is


def benchmark_algorithm(graph: CityGraph, algorithm_name: str,
                        num_runs: int = 5, source: str | None = None) -> BenchmarkResult:
    """
    Benchmark a shortest-path algorithm on a given graph.

    Args:
        graph: The city graph to test on
        algorithm_name: 'dijkstra' or 'bellman_ford'
        num_runs: Number of runs to average over
        source: Source vertex (defaults to first vertex)

    Returns:
        BenchmarkResult with timing statistics
    """
    if source is None:
        source = next(iter(graph.vertices))

    algorithm_fn = dijkstra if algorithm_name == "dijkstra" else bellman_ford
    times: List[float] = []

    for _ in range(num_runs):
        start = time.perf_counter()
        algorithm_fn(graph, source, use_traffic=False)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return BenchmarkResult(
        algorithm=algorithm_name.replace("_", "-").title(),
        num_vertices=graph.num_vertices,
        num_edges=graph.num_edges,
        avg_time_ms=statistics.mean(times),
        min_time_ms=min(times),
        max_time_ms=max(times),
        median_time_ms=statistics.median(times),
        std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
        num_runs=num_runs,
    )


def run_comparison(graph_sizes: List[Tuple[int, int]] | None = None,
                   num_runs: int = 5,
                   seed: int = 42) -> List[ComparisonResult]:
    """
    Compare Dijkstra and Bellman-Ford across multiple graph sizes.

    Args:
        graph_sizes: List of (num_vertices, num_edges) tuples.
                     Defaults to a standard set of sizes.
        num_runs: Number of runs per algorithm per size
        seed: Random seed for reproducibility

    Returns:
        List of ComparisonResult for each graph size
    """
    if graph_sizes is None:
        graph_sizes = [
            (10, 20),
            (50, 150),
            (100, 400),
            (200, 1000),
            (500, 3000),
            (1000, 8000),
        ]

    results: List[ComparisonResult] = []

    for num_v, num_e in graph_sizes:
        print(f"  Benchmarking V={num_v}, E={num_e} ...")
        graph = generate_random_city(num_v, num_e, seed=seed)

        dijkstra_bench = benchmark_algorithm(graph, "dijkstra", num_runs)
        bf_bench = benchmark_algorithm(graph, "bellman_ford", num_runs)

        speedup = bf_bench.avg_time_ms / dijkstra_bench.avg_time_ms if dijkstra_bench.avg_time_ms > 0 else float('inf')

        results.append(ComparisonResult(
            num_vertices=num_v,
            num_edges=num_e,
            dijkstra_result=dijkstra_bench,
            bellman_ford_result=bf_bench,
            speedup_factor=round(speedup, 2),
        ))

    return results


def format_benchmark_report(results: List[ComparisonResult]) -> str:
    """Format benchmark results into a readable report."""
    lines = [
        "",
        "╔══════════════════════════════════════════════════════════════════════════════╗",
        "║            PERFORMANCE COMPARISON: Dijkstra vs Bellman-Ford                 ║",
        "╚══════════════════════════════════════════════════════════════════════════════╝",
        "",
        f"{'Vertices':>10} {'Edges':>8} │ {'Dijkstra (ms)':>15} {'Bellman-Ford (ms)':>18} │ {'Speedup':>8}",
        "─" * 10 + " " + "─" * 8 + " ┼ " + "─" * 15 + " " + "─" * 18 + " ┼ " + "─" * 8,
    ]

    for r in results:
        lines.append(
            f"{r.num_vertices:>10} {r.num_edges:>8} │ "
            f"{r.dijkstra_result.avg_time_ms:>15.4f} "
            f"{r.bellman_ford_result.avg_time_ms:>18.4f} │ "
            f"{r.speedup_factor:>7.2f}x"
        )

    lines.extend([
        "",
        "─" * 78,
        "Notes:",
        "  • Speedup = Bellman-Ford time / Dijkstra time",
        "  • Dijkstra: O((V+E) log V) — faster but requires non-negative weights",
        "  • Bellman-Ford: O(V×E) — slower but handles negative weights",
        "  • Times are averaged over multiple runs for reliability",
        "",
    ])

    return "\n".join(lines)
