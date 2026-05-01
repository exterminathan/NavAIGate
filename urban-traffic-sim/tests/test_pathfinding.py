from graph import Direction, Graph
from vehicle import Vehicle


def _build(nodes, edges):
    g = Graph()
    for n in nodes:
        g.add_intersection(n)
    for e in edges:
        g.add_road(e)
    return g


def test_astar_picks_shorter_route():
    """Two routes from A to D: via B (cheap) or via C (expensive)."""
    nodes = [
        ["A", (0, 0), "nothing"],
        ["B", (5, 0), "nothing"],
        ["C", (0, 5), "nothing"],
        ["D", (10, 10), "nothing"],
    ]
    edges = [
        ["A-B", 5, "A", "B", Direction.RIGHT],
        ["B-D", 5, "B", "D", Direction.RIGHT],
        ["A-C", 100, "A", "C", Direction.DOWN],
        ["C-D", 100, "C", "D", Direction.RIGHT],
    ]
    g = _build(nodes, edges)
    v = Vehicle(0, g.nodes["A"], g.nodes["D"], g)

    # Vehicle.__init__ pops the start node off self.path; remaining steps
    # should be the cheaper B-D route, not the C-D route.
    assert v.path == ["B", "D"]


def test_astar_disconnected_returns_empty():
    """C is unreachable from A so graph_search should return []."""
    nodes = [
        ["A", (0, 0), "nothing"],
        ["B", (5, 0), "nothing"],
        ["C", (50, 50), "nothing"],
    ]
    edges = [
        ["A-B", 5, "A", "B", Direction.RIGHT],
        ["B-A", 5, "B", "A", Direction.LEFT],
    ]
    g = _build(nodes, edges)

    # Build the vehicle on a connected pair so __init__ succeeds, then call
    # graph_search directly with the disconnected goal.
    v = Vehicle(0, g.nodes["A"], g.nodes["B"], g)
    assert v.graph_search(g.nodes["A"], g.nodes["C"], g) == []


def test_vehicle_init_state_after_astar():
    """After construction the start node is popped and the vehicle sits at the
    rear of the first road in the planned path."""
    nodes = [
        ["A", (0, 0), "nothing"],
        ["B", (5, 0), "nothing"],
    ]
    edges = [
        ["A-B", 5, "A", "B", Direction.RIGHT],
    ]
    g = _build(nodes, edges)
    v = Vehicle(0, g.nodes["A"], g.nodes["B"], g)

    assert v.path == ["B"]
    assert v.current == "A"
    assert v.road.id == "A-B"
    assert v.pos == v.road.size - 1
    assert v.direction == Direction.RIGHT
