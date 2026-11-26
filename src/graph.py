"""
Graph data structure for representing the city road network.

Locations are represented as vertices and roads as weighted edges.
Supports both directed and undirected graphs.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Edge:
    """Represents a road between two locations."""
    source: str
    destination: str
    weight: float  # Distance or travel time
    road_name: Optional[str] = None
    traffic_factor: float = 1.0  # Multiplier for traffic conditions

    @property
    def effective_weight(self) -> float:
        """Weight adjusted for current traffic conditions."""
        return self.weight * self.traffic_factor

    def __repr__(self) -> str:
        name = f" ({self.road_name})" if self.road_name else ""
        return f"{self.source} --{self.effective_weight:.1f}{name}--> {self.destination}"


@dataclass
class Vertex:
    """Represents a location/intersection in the city."""
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    location_type: str = "intersection"  # intersection, landmark, etc.

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vertex):
            return self.name == other.name
        return NotImplemented


class CityGraph:
    """
    Graph representation of a city road network.

    Uses an adjacency list for efficient storage and traversal.
    Supports weighted edges (road distances/travel times).
    """

    def __init__(self, directed: bool = False):
        """
        Initialize the city graph.

        Args:
            directed: If True, roads are one-way. If False, roads are two-way.
        """
        self.directed = directed
        self.vertices: Dict[str, Vertex] = {}
        self.adjacency_list: Dict[str, List[Edge]] = {}
        self._edge_count = 0

    def add_vertex(self, name: str, latitude: float = 0.0,
                   longitude: float = 0.0, location_type: str = "intersection") -> Vertex:
        """Add a location to the city map."""
        if name not in self.vertices:
            vertex = Vertex(name, latitude, longitude, location_type)
            self.vertices[name] = vertex
            self.adjacency_list[name] = []
        return self.vertices[name]

    def add_edge(self, source: str, destination: str, weight: float,
                 road_name: Optional[str] = None, traffic_factor: float = 1.0) -> None:
        """
        Add a road between two locations.

        Args:
            source: Starting location name
            destination: Ending location name
            weight: Distance or travel time
            road_name: Optional name of the road
            traffic_factor: Traffic multiplier (1.0 = normal, >1 = congested)
        """
        # Auto-add vertices if they don't exist
        self.add_vertex(source)
        self.add_vertex(destination)

        edge = Edge(source, destination, weight, road_name, traffic_factor)
        self.adjacency_list[source].append(edge)
        self._edge_count += 1

        if not self.directed:
            reverse_edge = Edge(destination, source, weight, road_name, traffic_factor)
            self.adjacency_list[destination].append(reverse_edge)
            self._edge_count += 1

    def get_neighbors(self, vertex_name: str) -> List[Edge]:
        """Get all roads from a given location."""
        return self.adjacency_list.get(vertex_name, [])

    def get_all_edges(self) -> List[Edge]:
        """Get all edges in the graph (each direction counted once)."""
        edges = []
        for vertex in self.adjacency_list:
            for edge in self.adjacency_list[vertex]:
                edges.append(edge)
        return edges

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    @property
    def num_edges(self) -> int:
        return self._edge_count

    def has_vertex(self, name: str) -> bool:
        return name in self.vertices

    def has_edge(self, source: str, destination: str) -> bool:
        if source not in self.adjacency_list:
            return False
        return any(e.destination == destination for e in self.adjacency_list[source])

    def update_traffic(self, source: str, destination: str, factor: float) -> None:
        """Update traffic conditions on a road."""
        for edge in self.adjacency_list.get(source, []):
            if edge.destination == destination:
                edge.traffic_factor = factor
        if not self.directed:
            for edge in self.adjacency_list.get(destination, []):
                if edge.source == destination and edge.destination == source:
                    edge.traffic_factor = factor

    def __repr__(self) -> str:
        return (f"CityGraph(vertices={self.num_vertices}, "
                f"edges={self.num_edges}, directed={self.directed})")

    def display(self) -> str:
        """Return a string representation of the entire graph."""
        lines = [f"City Road Network ({self})", "=" * 50]
        for vertex_name in sorted(self.adjacency_list.keys()):
            edges = self.adjacency_list[vertex_name]
            if edges:
                connections = ", ".join(
                    f"{e.destination}({e.effective_weight:.1f})" for e in edges
                )
                lines.append(f"  {vertex_name} → {connections}")
            else:
                lines.append(f"  {vertex_name} → (no outgoing roads)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Graph generators for benchmarking
# ---------------------------------------------------------------------------

def generate_random_city(num_locations: int, num_roads: int,
                         min_weight: float = 1.0, max_weight: float = 20.0,
                         directed: bool = False, seed: int | None = None) -> CityGraph:
    """
    Generate a random city graph for testing and benchmarking.

    Args:
        num_locations: Number of locations (vertices)
        num_roads: Number of roads (edges)
        min_weight: Minimum road weight
        max_weight: Maximum road weight
        directed: Whether roads are one-way
        seed: Random seed for reproducibility

    Returns:
        A randomly generated CityGraph
    """
    if seed is not None:
        random.seed(seed)

    graph = CityGraph(directed=directed)

    # Create location names
    locations = [f"Loc_{i}" for i in range(num_locations)]
    for loc in locations:
        graph.add_vertex(
            loc,
            latitude=random.uniform(12.9, 13.1),
            longitude=random.uniform(77.5, 77.7),
        )

    # Ensure connectivity: build a spanning tree first
    shuffled = locations[:]
    random.shuffle(shuffled)
    for i in range(1, len(shuffled)):
        weight = round(random.uniform(min_weight, max_weight), 1)
        graph.add_edge(shuffled[i - 1], shuffled[i], weight,
                       road_name=f"Road_{shuffled[i-1]}_{shuffled[i]}")

    # Add remaining random edges
    added = num_locations - 1  # edges from spanning tree
    attempts = 0
    while added < num_roads and attempts < num_roads * 10:
        src = random.choice(locations)
        dst = random.choice(locations)
        if src != dst and not graph.has_edge(src, dst):
            weight = round(random.uniform(min_weight, max_weight), 1)
            graph.add_edge(src, dst, weight,
                           road_name=f"Road_{src}_{dst}")
            added += 1
        attempts += 1

    return graph


def create_sample_city() -> CityGraph:
    """
    Create a sample city graph representing a small city with named locations.

    Returns a graph with realistic city locations and road connections.
    """
    graph = CityGraph(directed=False)

    # Add city locations
    locations = {
        "City_Center":    (12.9716, 77.5946, "landmark"),
        "Railway_Station": (12.9779, 77.5710, "landmark"),
        "Airport":        (13.1989, 77.7068, "landmark"),
        "University":     (12.9352, 77.6245, "landmark"),
        "Hospital":       (12.9563, 77.6033, "landmark"),
        "Mall":           (12.9900, 77.6150, "landmark"),
        "Park":           (12.9850, 77.5900, "landmark"),
        "Stadium":        (12.9690, 77.5995, "landmark"),
        "Library":        (12.9450, 77.5800, "landmark"),
        "Market":         (12.9600, 77.5750, "landmark"),
        "Bus_Station":    (12.9510, 77.5700, "landmark"),
        "Tech_Park":      (12.9280, 77.6300, "landmark"),
        "Museum":         (12.9750, 77.5650, "landmark"),
        "Hotel_Zone":     (12.9820, 77.6050, "landmark"),
        "Residential_A":  (12.9400, 77.5900, "intersection"),
        "Residential_B":  (13.0000, 77.5800, "intersection"),
    }

    for name, (lat, lon, loc_type) in locations.items():
        graph.add_vertex(name, lat, lon, loc_type)

    # Add roads with realistic distances (km)
    roads = [
        ("City_Center", "Railway_Station", 3.2, "MG Road"),
        ("City_Center", "Hospital", 2.5, "Brigade Road"),
        ("City_Center", "Mall", 3.0, "Commercial Street"),
        ("City_Center", "Park", 1.5, "Cubbon Road"),
        ("City_Center", "Stadium", 1.8, "Stadium Road"),
        ("City_Center", "Market", 2.0, "Market Road"),
        ("Railway_Station", "Museum", 1.5, "Station Road"),
        ("Railway_Station", "Bus_Station", 3.0, "Ring Road North"),
        ("Airport", "Mall", 25.0, "Airport Highway"),
        ("Airport", "Hotel_Zone", 22.0, "Airport Express"),
        ("University", "Tech_Park", 2.0, "University Road"),
        ("University", "Hospital", 3.5, "Campus Road"),
        ("University", "Library", 4.0, "Knowledge Lane"),
        ("Hospital", "Mall", 4.0, "Health Avenue"),
        ("Hospital", "Stadium", 2.0, "Emergency Route"),
        ("Mall", "Hotel_Zone", 1.5, "Luxury Lane"),
        ("Mall", "Park", 2.5, "Garden Path"),
        ("Park", "Museum", 3.0, "Heritage Walk"),
        ("Park", "Residential_B", 2.0, "Green Corridor"),
        ("Stadium", "Market", 1.5, "Fan Walk"),
        ("Library", "Residential_A", 1.8, "Library Lane"),
        ("Library", "Bus_Station", 2.5, "Transit Road"),
        ("Market", "Bus_Station", 1.0, "Bazaar Street"),
        ("Bus_Station", "Residential_A", 2.0, "Suburb Road"),
        ("Tech_Park", "Residential_A", 5.0, "Tech Highway"),
        ("Hotel_Zone", "Residential_B", 3.0, "Hotel Boulevard"),
        ("Museum", "Residential_B", 4.0, "Culture Drive"),
        ("Residential_A", "Residential_B", 7.0, "Cross City Road"),
    ]

    for src, dst, weight, name in roads:
        graph.add_edge(src, dst, weight, road_name=name)

    return graph
