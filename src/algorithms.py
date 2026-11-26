"""
Shortest path algorithms for the Smart City Route Optimization System.

Implements:
  - Dijkstra's Algorithm  (non-negative weights, faster)
  - Bellman-Ford Algorithm (handles negative weights, detects negative cycles)
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .graph import CityGraph


@dataclass
class PathResult:
    """Result of a shortest-path computation."""
    algorithm: str
    source: str
    destination: str
    distance: float
    path: List[str]
    execution_time_ms: float
    vertices_explored: int
    found: bool

    def __repr__(self) -> str:
        if not self.found:
            return (f"[{self.algorithm}] No path from {self.source} "
                    f"to {self.destination}")
        route = " → ".join(self.path)
        return (f"[{self.algorithm}] {self.source} → {self.destination}\n"
                f"  Distance : {self.distance:.2f}\n"
                f"  Path     : {route}\n"
                f"  Time     : {self.execution_time_ms:.4f} ms\n"
                f"  Explored : {self.vertices_explored} vertices")


@dataclass
class AllPathsResult:
    """Result containing shortest distances to all reachable vertices."""
    algorithm: str
    source: str
    distances: Dict[str, float]
    predecessors: Dict[str, Optional[str]]
    execution_time_ms: float
    vertices_explored: int
    has_negative_cycle: bool = False

    def get_path(self, destination: str) -> List[str]:
        """Reconstruct the shortest path to a destination."""
        if destination not in self.distances or self.distances[destination] == float('inf'):
            return []
        path = []
        current: Optional[str] = destination
        while current is not None:
            path.append(current)
            current = self.predecessors.get(current)
        path.reverse()
        return path

    def get_result(self, destination: str) -> PathResult:
        """Get a PathResult for a specific destination."""
        path = self.get_path(destination)
        dist = self.distances.get(destination, float('inf'))
        return PathResult(
            algorithm=self.algorithm,
            source=self.source,
            destination=destination,
            distance=dist,
            path=path,
            execution_time_ms=self.execution_time_ms,
            vertices_explored=self.vertices_explored,
            found=len(path) > 0 and dist < float('inf'),
        )


# -------------------------------------------------------------------------
# Dijkstra's Algorithm
# -------------------------------------------------------------------------

def dijkstra(graph: CityGraph, source: str,
             destination: Optional[str] = None,
             use_traffic: bool = True) -> AllPathsResult:
    """
    Dijkstra's algorithm for single-source shortest paths.

    Uses a min-heap (priority queue) for efficient vertex selection.
    Time complexity : O((V + E) log V)
    Space complexity: O(V)

    Args:
        graph: The city road network
        source: Starting location
        destination: Optional target (early exit when reached)
        use_traffic: Whether to use traffic-adjusted weights

    Returns:
        AllPathsResult with distances and predecessors
    """
    if source not in graph.vertices:
        raise ValueError(f"Source '{source}' not found in graph")

    start_time = time.perf_counter()

    # Initialisation
    distances: Dict[str, float] = {v: float('inf') for v in graph.vertices}
    predecessors: Dict[str, Optional[str]] = {v: None for v in graph.vertices}
    distances[source] = 0.0
    visited: set[str] = set()
    vertices_explored = 0

    # Min-heap: (distance, vertex_name)
    heap: list[Tuple[float, str]] = [(0.0, source)]

    while heap:
        current_dist, current = heapq.heappop(heap)

        if current in visited:
            continue
        visited.add(current)
        vertices_explored += 1

        # Early exit if we only need one destination
        if destination and current == destination:
            break

        # Relax neighbours
        for edge in graph.get_neighbors(current):
            if edge.destination in visited:
                continue
            weight = edge.effective_weight if use_traffic else edge.weight
            new_dist = current_dist + weight

            if new_dist < distances[edge.destination]:
                distances[edge.destination] = new_dist
                predecessors[edge.destination] = current
                heapq.heappush(heap, (new_dist, edge.destination))

    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000

    return AllPathsResult(
        algorithm="Dijkstra",
        source=source,
        distances=distances,
        predecessors=predecessors,
        execution_time_ms=execution_time_ms,
        vertices_explored=vertices_explored,
    )


def dijkstra_shortest_path(graph: CityGraph, source: str,
                           destination: str,
                           use_traffic: bool = True) -> PathResult:
    """Convenience wrapper: returns a single PathResult."""
    result = dijkstra(graph, source, destination, use_traffic)
    return result.get_result(destination)


# -------------------------------------------------------------------------
# Bellman-Ford Algorithm
# -------------------------------------------------------------------------

def bellman_ford(graph: CityGraph, source: str,
                 use_traffic: bool = True) -> AllPathsResult:
    """
    Bellman-Ford algorithm for single-source shortest paths.

    Can handle negative edge weights and detects negative-weight cycles.
    Time complexity : O(V × E)
    Space complexity: O(V)

    Args:
        graph: The city road network
        source: Starting location
        use_traffic: Whether to use traffic-adjusted weights

    Returns:
        AllPathsResult with distances, predecessors, and negative-cycle flag
    """
    if source not in graph.vertices:
        raise ValueError(f"Source '{source}' not found in graph")

    start_time = time.perf_counter()

    # Initialisation
    distances: Dict[str, float] = {v: float('inf') for v in graph.vertices}
    predecessors: Dict[str, Optional[str]] = {v: None for v in graph.vertices}
    distances[source] = 0.0
    vertices_explored = 0

    num_vertices = graph.num_vertices
    all_edges = graph.get_all_edges()

    # Relax all edges (V - 1) times
    for iteration in range(num_vertices - 1):
        updated = False
        for edge in all_edges:
            weight = edge.effective_weight if use_traffic else edge.weight
            if (distances[edge.source] != float('inf')
                    and distances[edge.source] + weight < distances[edge.destination]):
                distances[edge.destination] = distances[edge.source] + weight
                predecessors[edge.destination] = edge.source
                updated = True
        vertices_explored += 1
        # Early termination if no updates occurred
        if not updated:
            break

    # Check for negative-weight cycles (one more pass)
    has_negative_cycle = False
    for edge in all_edges:
        weight = edge.effective_weight if use_traffic else edge.weight
        if (distances[edge.source] != float('inf')
                and distances[edge.source] + weight < distances[edge.destination]):
            has_negative_cycle = True
            break

    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000

    return AllPathsResult(
        algorithm="Bellman-Ford",
        source=source,
        distances=distances,
        predecessors=predecessors,
        execution_time_ms=execution_time_ms,
        vertices_explored=vertices_explored,
        has_negative_cycle=has_negative_cycle,
    )


def bellman_ford_shortest_path(graph: CityGraph, source: str,
                               destination: str,
                               use_traffic: bool = True) -> PathResult:
    """Convenience wrapper: returns a single PathResult."""
    result = bellman_ford(graph, source, use_traffic)
    return result.get_result(destination)
