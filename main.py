#!/usr/bin/env python3
"""
Smart City Route Optimization System
=====================================
Main entry point demonstrating route optimization using
Dijkstra's and Bellman-Ford shortest-path algorithms.

Usage:
    python main.py                 # Run full demo
    python main.py --benchmark     # Run benchmark only
    python main.py --route A B     # Find route between two locations
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import CityGraph, create_sample_city, generate_random_city
from src.algorithms import (
    dijkstra, dijkstra_shortest_path,
    bellman_ford, bellman_ford_shortest_path,
)
from src.benchmark import run_comparison, format_benchmark_report
from src.visualizer import (
    print_path, print_all_distances,
    plot_city_graph, plot_benchmark_comparison,
)


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║         🏙️  SMART CITY ROUTE OPTIMIZATION SYSTEM  🏙️          ║
    ║                                                               ║
    ║   Finding the shortest & most efficient routes in the city    ║
    ║   Using Dijkstra's & Bellman-Ford Algorithms                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def demo_shortest_path(graph: CityGraph):
    """Demonstrate shortest path finding between various locations."""
    print("\n" + "=" * 70)
    print("  DEMO 1: Shortest Path Between Two Locations")
    print("=" * 70)

    test_routes = [
        ("City_Center", "Airport"),
        ("Railway_Station", "Tech_Park"),
        ("Hospital", "Residential_B"),
        ("University", "Mall"),
        ("Bus_Station", "Hotel_Zone"),
    ]

    for source, destination in test_routes:
        print(f"\n{'─' * 60}")
        print(f"  Route: {source} → {destination}")
        print(f"{'─' * 60}")

        # Dijkstra
        dij_result = dijkstra_shortest_path(graph, source, destination)
        print(print_path(dij_result))

        # Bellman-Ford
        bf_result = bellman_ford_shortest_path(graph, source, destination)
        print(print_path(bf_result))

        # Compare
        if dij_result.found and bf_result.found:
            if abs(dij_result.distance - bf_result.distance) < 1e-9:
                print("  ✅ Both algorithms agree on the shortest distance!")
            else:
                print("  ⚠️  Distance mismatch detected!")

            speedup = bf_result.execution_time_ms / dij_result.execution_time_ms if dij_result.execution_time_ms > 0 else 0
            print(f"  ⏱️  Dijkstra was {speedup:.2f}x faster than Bellman-Ford")


def demo_all_distances(graph: CityGraph):
    """Demonstrate finding all shortest distances from a source."""
    print("\n" + "=" * 70)
    print("  DEMO 2: All Shortest Distances from City Center")
    print("=" * 70)

    source = "City_Center"

    # Dijkstra
    dij_all = dijkstra(graph, source)
    print(f"\n{print_all_distances(dij_all)}")

    print(f"\n  Execution time: {dij_all.execution_time_ms:.4f} ms")
    print(f"  Vertices explored: {dij_all.vertices_explored}")


def demo_traffic_impact(graph: CityGraph):
    """Demonstrate how traffic conditions affect route selection."""
    print("\n" + "=" * 70)
    print("  DEMO 3: Traffic Impact on Route Selection")
    print("=" * 70)

    source, destination = "City_Center", "Airport"

    # Normal conditions
    print("\n  📊 Normal Traffic Conditions:")
    normal_result = dijkstra_shortest_path(graph, source, destination)
    print(print_path(normal_result))

    # Simulate heavy traffic on Airport Highway
    print("\n  🚗 Heavy Traffic on Airport Highway (3x congestion):")
    graph.update_traffic("Airport", "Mall", 3.0)
    traffic_result = dijkstra_shortest_path(graph, source, destination)
    print(print_path(traffic_result))

    if normal_result.path != traffic_result.path:
        print("  🔄 Route changed due to traffic!")
    else:
        print("  ℹ️  Same route, but with increased travel time.")

    # Reset traffic
    graph.update_traffic("Airport", "Mall", 1.0)


def demo_benchmark():
    """Run performance benchmarks comparing both algorithms."""
    print("\n" + "=" * 70)
    print("  DEMO 4: Performance Benchmark")
    print("=" * 70)

    print("\n  Running benchmarks across different graph sizes...")
    results = run_comparison(num_runs=3)
    report = format_benchmark_report(results)
    print(report)

    # Generate benchmark plot
    plot_path = plot_benchmark_comparison(results, "output/benchmark_comparison.png")
    if plot_path:
        print(f"  📊 Benchmark visualization saved to: {plot_path}")

    return results


def demo_visualization(graph: CityGraph):
    """Generate graph visualizations."""
    print("\n" + "=" * 70)
    print("  DEMO 5: Visualization")
    print("=" * 70)

    # Plot the city graph
    plot_city_graph(graph, title="Smart City Road Network",
                    output_path="output/city_network.png")

    # Plot with highlighted shortest path
    result = dijkstra_shortest_path(graph, "City_Center", "Airport")
    if result.found:
        plot_city_graph(graph, highlight_path=result.path,
                        title=f"Shortest Path: City Center → Airport ({result.distance:.1f} km)",
                        output_path="output/shortest_path_highlighted.png")


def find_route(graph: CityGraph, source: str, destination: str):
    """Find and display a route between two locations."""
    print(f"\n  Finding route: {source} → {destination}")
    print("─" * 50)

    if not graph.has_vertex(source):
        print(f"  ❌ Location '{source}' not found!")
        print(f"  Available: {', '.join(sorted(graph.vertices.keys()))}")
        return

    if not graph.has_vertex(destination):
        print(f"  ❌ Location '{destination}' not found!")
        print(f"  Available: {', '.join(sorted(graph.vertices.keys()))}")
        return

    dij = dijkstra_shortest_path(graph, source, destination)
    bf = bellman_ford_shortest_path(graph, source, destination)

    print(print_path(dij))
    print(print_path(bf))

    if dij.found:
        plot_city_graph(graph, highlight_path=dij.path,
                        title=f"Route: {source} → {destination} ({dij.distance:.1f} km)",
                        output_path="output/custom_route.png")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart City Route Optimization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          Run full demo
  python main.py --benchmark              Run benchmarks only
  python main.py --route City_Center Airport
        """,
    )
    parser.add_argument("--benchmark", action="store_true",
                        help="Run performance benchmarks only")
    parser.add_argument("--route", nargs=2, metavar=("FROM", "TO"),
                        help="Find route between two locations")
    parser.add_argument("--list-locations", action="store_true",
                        help="List all available locations")

    args = parser.parse_args()

    print_banner()

    # Create the sample city
    city = create_sample_city()
    print(f"  Loaded city: {city}")
    print(f"  Locations: {city.num_vertices}")
    print(f"  Roads: {city.num_edges}")

    if args.list_locations:
        print("\n  Available Locations:")
        for name in sorted(city.vertices.keys()):
            v = city.vertices[name]
            print(f"    • {name} ({v.location_type})")
        return

    if args.route:
        find_route(city, args.route[0], args.route[1])
        return

    if args.benchmark:
        demo_benchmark()
        return

    # Full demo
    demo_shortest_path(city)
    demo_all_distances(city)
    demo_traffic_impact(city)
    demo_benchmark()
    demo_visualization(city)

    print("\n" + "=" * 70)
    print("  ✅ All demos completed successfully!")
    print("  📁 Check the 'output/' folder for generated visualizations.")
    print("=" * 70)


if __name__ == "__main__":
    main()
