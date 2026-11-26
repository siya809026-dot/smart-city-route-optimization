"""
Flask Web Application for Smart City Route Optimization System.
Provides a web interface for route finding, benchmarking, and visualization.
"""

from flask import Flask, render_template, jsonify, request
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import CityGraph, create_sample_city, generate_random_city
from src.algorithms import dijkstra, bellman_ford, dijkstra_shortest_path, bellman_ford_shortest_path
from src.benchmark import run_comparison

app = Flask(__name__)

# Pre-load the sample city
city = create_sample_city()


def graph_to_json(graph: CityGraph) -> dict:
    """Convert graph to JSON-serializable format for the frontend."""
    nodes = []
    for name, vertex in graph.vertices.items():
        nodes.append({
            "id": name,
            "label": name.replace("_", " "),
            "lat": vertex.latitude,
            "lon": vertex.longitude,
            "type": vertex.location_type,
        })

    edges = []
    seen = set()
    for src in graph.adjacency_list:
        for edge in graph.adjacency_list[src]:
            pair = tuple(sorted([edge.source, edge.destination]))
            if pair not in seen:
                seen.add(pair)
                edges.append({
                    "source": edge.source,
                    "target": edge.destination,
                    "weight": edge.weight,
                    "road_name": edge.road_name or "",
                    "traffic_factor": edge.traffic_factor,
                    "effective_weight": edge.effective_weight,
                })

    return {"nodes": nodes, "edges": edges}


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/graph")
def get_graph():
    """Return the city graph data."""
    return jsonify(graph_to_json(city))


@app.route("/api/locations")
def get_locations():
    """Return list of available locations."""
    locations = sorted([
        {"id": name, "label": name.replace("_", " "), "type": v.location_type}
        for name, v in city.vertices.items()
    ], key=lambda x: x["label"])
    return jsonify(locations)


@app.route("/api/shortest-path", methods=["POST"])
def shortest_path():
    """Find shortest path between two locations using both algorithms."""
    data = request.get_json()
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"error": "Source and destination required"}), 400
    if source not in city.vertices:
        return jsonify({"error": f"Location '{source}' not found"}), 404
    if destination not in city.vertices:
        return jsonify({"error": f"Location '{destination}' not found"}), 404

    # Run Dijkstra
    dij_result = dijkstra_shortest_path(city, source, destination)

    # Run Bellman-Ford
    bf_result = bellman_ford_shortest_path(city, source, destination)

    response = {
        "dijkstra": {
            "distance": dij_result.distance if dij_result.found else None,
            "path": dij_result.path if dij_result.found else [],
            "time_ms": round(dij_result.execution_time_ms, 4),
            "vertices_explored": dij_result.vertices_explored,
            "found": dij_result.found,
        },
        "bellman_ford": {
            "distance": bf_result.distance if bf_result.found else None,
            "path": bf_result.path if bf_result.found else [],
            "time_ms": round(bf_result.execution_time_ms, 4),
            "vertices_explored": bf_result.vertices_explored,
            "found": bf_result.found,
        },
        "match": (dij_result.found and bf_result.found and
                  abs(dij_result.distance - bf_result.distance) < 1e-9),
    }

    if dij_result.found and bf_result.found and dij_result.execution_time_ms > 0:
        response["speedup"] = round(bf_result.execution_time_ms / dij_result.execution_time_ms, 2)

    return jsonify(response)


@app.route("/api/all-distances", methods=["POST"])
def all_distances():
    """Find all shortest distances from a source."""
    data = request.get_json()
    source = data.get("source")

    if not source or source not in city.vertices:
        return jsonify({"error": "Valid source required"}), 400

    dij_all = dijkstra(city, source)
    bf_all = bellman_ford(city, source)

    distances = []
    for dest in sorted(city.vertices.keys()):
        d_dist = dij_all.distances[dest]
        b_dist = bf_all.distances[dest]
        distances.append({
            "destination": dest,
            "label": dest.replace("_", " "),
            "dijkstra_dist": round(d_dist, 2) if d_dist != float('inf') else None,
            "bellman_ford_dist": round(b_dist, 2) if b_dist != float('inf') else None,
            "path": dij_all.get_path(dest),
        })

    return jsonify({
        "source": source,
        "distances": distances,
        "dijkstra_time_ms": round(dij_all.execution_time_ms, 4),
        "bellman_ford_time_ms": round(bf_all.execution_time_ms, 4),
    })


@app.route("/api/benchmark", methods=["POST"])
def benchmark():
    """Run performance benchmarks."""
    data = request.get_json() or {}
    sizes = data.get("sizes", [
        [10, 20], [50, 150], [100, 400], [200, 1000], [500, 3000],
    ])
    num_runs = min(data.get("num_runs", 3), 5)  # Cap at 5

    graph_sizes = [(v, e) for v, e in sizes]
    results = run_comparison(graph_sizes, num_runs=num_runs, seed=42)

    benchmark_data = []
    for r in results:
        benchmark_data.append({
            "vertices": r.num_vertices,
            "edges": r.num_edges,
            "dijkstra_ms": round(r.dijkstra_result.avg_time_ms, 4),
            "bellman_ford_ms": round(r.bellman_ford_result.avg_time_ms, 4),
            "speedup": r.speedup_factor,
            "dijkstra_min": round(r.dijkstra_result.min_time_ms, 4),
            "dijkstra_max": round(r.dijkstra_result.max_time_ms, 4),
            "bellman_ford_min": round(r.bellman_ford_result.min_time_ms, 4),
            "bellman_ford_max": round(r.bellman_ford_result.max_time_ms, 4),
        })

    return jsonify({"results": benchmark_data})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
