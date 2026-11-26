"""
Unit tests for shortest-path algorithms.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graph import CityGraph, create_sample_city, generate_random_city
from src.algorithms import (
    dijkstra, dijkstra_shortest_path,
    bellman_ford, bellman_ford_shortest_path,
)


class TestDijkstra(unittest.TestCase):
    """Test Dijkstra's algorithm."""

    def setUp(self):
        """Create a simple test graph."""
        self.graph = CityGraph(directed=False)
        self.graph.add_edge("A", "B", 4.0)
        self.graph.add_edge("A", "C", 2.0)
        self.graph.add_edge("B", "D", 3.0)
        self.graph.add_edge("C", "B", 1.0)
        self.graph.add_edge("C", "D", 5.0)
        self.graph.add_edge("D", "E", 2.0)

    def test_shortest_path_basic(self):
        """Test basic shortest path finding."""
        result = dijkstra_shortest_path(self.graph, "A", "E")
        self.assertTrue(result.found)
        self.assertAlmostEqual(result.distance, 8.0)  # A→C→B→D→E = 2+1+3+2

    def test_shortest_path_to_self(self):
        """Path to self should be zero distance."""
        result = dijkstra_shortest_path(self.graph, "A", "A")
        self.assertTrue(result.found)
        self.assertAlmostEqual(result.distance, 0.0)

    def test_shortest_path_direct_neighbor(self):
        """Test path to direct neighbor."""
        result = dijkstra_shortest_path(self.graph, "A", "C")
        self.assertTrue(result.found)
        self.assertAlmostEqual(result.distance, 2.0)

    def test_no_path(self):
        """Test when no path exists."""
        graph = CityGraph(directed=True)
        graph.add_edge("A", "B", 1.0)
        graph.add_vertex("C")  # Isolated vertex
        result = dijkstra_shortest_path(graph, "A", "C")
        self.assertFalse(result.found)

    def test_invalid_source(self):
        """Test with nonexistent source."""
        with self.assertRaises(ValueError):
            dijkstra_shortest_path(self.graph, "Z", "A")

    def test_all_distances(self):
        """Test computing distances to all vertices."""
        result = dijkstra(self.graph, "A")
        self.assertAlmostEqual(result.distances["A"], 0.0)
        self.assertAlmostEqual(result.distances["C"], 2.0)
        self.assertAlmostEqual(result.distances["B"], 3.0)  # A→C→B
        self.assertAlmostEqual(result.distances["D"], 6.0)  # A→C→B→D
        self.assertAlmostEqual(result.distances["E"], 8.0)  # A→C→B→D→E


class TestBellmanFord(unittest.TestCase):
    """Test Bellman-Ford algorithm."""

    def setUp(self):
        """Create a simple test graph."""
        self.graph = CityGraph(directed=False)
        self.graph.add_edge("A", "B", 4.0)
        self.graph.add_edge("A", "C", 2.0)
        self.graph.add_edge("B", "D", 3.0)
        self.graph.add_edge("C", "B", 1.0)
        self.graph.add_edge("C", "D", 5.0)
        self.graph.add_edge("D", "E", 2.0)

    def test_shortest_path_basic(self):
        """Test basic shortest path finding."""
        result = bellman_ford_shortest_path(self.graph, "A", "E")
        self.assertTrue(result.found)
        self.assertAlmostEqual(result.distance, 8.0)

    def test_shortest_path_to_self(self):
        """Path to self should be zero distance."""
        result = bellman_ford_shortest_path(self.graph, "A", "A")
        self.assertTrue(result.found)
        self.assertAlmostEqual(result.distance, 0.0)

    def test_no_negative_cycle(self):
        """Test that normal graph has no negative cycle."""
        result = bellman_ford(self.graph, "A")
        self.assertFalse(result.has_negative_cycle)

    def test_negative_cycle_detection(self):
        """Test detection of negative-weight cycles."""
        graph = CityGraph(directed=True)
        graph.add_edge("A", "B", 1.0)
        graph.add_edge("B", "C", -3.0)
        graph.add_edge("C", "A", 1.0)
        result = bellman_ford(graph, "A")
        self.assertTrue(result.has_negative_cycle)

    def test_invalid_source(self):
        """Test with nonexistent source."""
        with self.assertRaises(ValueError):
            bellman_ford_shortest_path(self.graph, "Z", "A")


class TestAlgorithmConsistency(unittest.TestCase):
    """Test that both algorithms produce consistent results."""

    def test_same_distances_simple(self):
        """Both algorithms should find the same shortest distances."""
        graph = CityGraph(directed=False)
        graph.add_edge("A", "B", 4.0)
        graph.add_edge("A", "C", 2.0)
        graph.add_edge("B", "D", 3.0)
        graph.add_edge("C", "B", 1.0)
        graph.add_edge("C", "D", 5.0)

        dij = dijkstra(graph, "A")
        bf = bellman_ford(graph, "A")

        for vertex in graph.vertices:
            self.assertAlmostEqual(
                dij.distances[vertex], bf.distances[vertex],
                msg=f"Distance to {vertex} differs"
            )

    def test_same_distances_sample_city(self):
        """Both algorithms agree on the sample city graph."""
        city = create_sample_city()
        source = "City_Center"

        dij = dijkstra(city, source)
        bf = bellman_ford(city, source)

        for vertex in city.vertices:
            self.assertAlmostEqual(
                dij.distances[vertex], bf.distances[vertex], places=5,
                msg=f"Distance to {vertex} differs: "
                    f"Dijkstra={dij.distances[vertex]:.4f}, "
                    f"BF={bf.distances[vertex]:.4f}"
            )

    def test_same_distances_random_graph(self):
        """Both algorithms agree on a random graph."""
        graph = generate_random_city(50, 150, seed=12345)
        source = next(iter(graph.vertices))

        dij = dijkstra(graph, source)
        bf = bellman_ford(graph, source)

        for vertex in graph.vertices:
            self.assertAlmostEqual(
                dij.distances[vertex], bf.distances[vertex], places=5,
                msg=f"Distance to {vertex} differs"
            )


class TestGraph(unittest.TestCase):
    """Test graph data structure."""

    def test_add_vertex(self):
        g = CityGraph()
        g.add_vertex("A")
        self.assertTrue(g.has_vertex("A"))
        self.assertEqual(g.num_vertices, 1)

    def test_add_edge_undirected(self):
        g = CityGraph(directed=False)
        g.add_edge("A", "B", 5.0)
        self.assertTrue(g.has_edge("A", "B"))
        self.assertTrue(g.has_edge("B", "A"))

    def test_add_edge_directed(self):
        g = CityGraph(directed=True)
        g.add_edge("A", "B", 5.0)
        self.assertTrue(g.has_edge("A", "B"))
        self.assertFalse(g.has_edge("B", "A"))

    def test_sample_city_creation(self):
        city = create_sample_city()
        self.assertEqual(city.num_vertices, 16)
        self.assertTrue(city.has_vertex("City_Center"))
        self.assertTrue(city.has_vertex("Airport"))

    def test_random_city_generation(self):
        graph = generate_random_city(20, 40, seed=42)
        self.assertEqual(graph.num_vertices, 20)
        self.assertTrue(graph.num_edges > 0)

    def test_traffic_update(self):
        g = CityGraph(directed=False)
        g.add_edge("A", "B", 10.0)
        g.update_traffic("A", "B", 2.0)
        edges = g.get_neighbors("A")
        self.assertAlmostEqual(edges[0].effective_weight, 20.0)


if __name__ == "__main__":
    unittest.main()
