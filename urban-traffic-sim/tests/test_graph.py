import pytest

from graph import Direction, Graph, Road


class _FakeCar:
    def __init__(self, car_id):
        self.id = car_id


def test_road_enter_advance_exit_cycle():
    road = Road("R1", 3, "X", "Y", Direction.RIGHT)
    assert road.queue == [None, None, None]

    a, b = _FakeCar("A"), _FakeCar("B")

    assert road.enter(a) is True
    assert road.queue == [None, None, "A"]

    # rear cell occupied -> next entry rejected
    assert road.enter(b) is False

    # advance "A" forward one cell
    assert road.advance(2) is True
    assert road.queue == [None, "A", None]

    # rear is free again
    assert road.enter(b) is True
    assert road.queue == [None, "A", "B"]

    # "B" cannot advance through "A"
    assert road.advance(2) is False

    # "A" advances to the front
    assert road.advance(1) is True
    assert road.queue == ["A", None, "B"]

    # front cell cannot advance further
    assert road.advance(0) is False

    # exit pops the front
    assert road.exit_road() is True
    assert road.queue == [None, None, "B"]

    # exit on empty front returns False
    assert road.exit_road() is False


def test_graph_add_intersection_stores_node():
    g = Graph()
    g.add_intersection(["1", (10, 20), "stop_sign"])

    assert "1" in g.nodes
    node = g.nodes["1"]
    assert node.nodeType == "stop_sign"
    assert (node.x, node.y) == (10, 20)
    # stop_sign node has empty pattern; only traffic_light gets a real pattern
    assert node.pattern == [None, None, None, None]


def test_graph_add_road_with_missing_endpoint_raises():
    g = Graph()
    g.add_intersection(["1", (0, 0), "nothing"])
    # endpoint "2" was never added
    with pytest.raises(ValueError):
        g.add_road(["1-2", 5, "1", "2", Direction.RIGHT])


def test_graph_find_edge_and_neighbors():
    g = Graph()
    g.add_intersection(["A", (0, 0), "nothing"])
    g.add_intersection(["B", (10, 0), "nothing"])
    g.add_intersection(["C", (20, 0), "nothing"])

    g.add_road(["A-B", 5, "A", "B", Direction.RIGHT])
    g.add_road(["B-C", 7, "B", "C", Direction.RIGHT])

    edge = g.findEdge(g.nodes["A"], g.nodes["B"])
    assert edge is not None and edge.id == "A-B"

    # no edge in the reverse direction
    assert g.findEdge(g.nodes["B"], g.nodes["A"]) is None

    neighbors = g.neighbors(g.nodes["B"])
    assert len(neighbors) == 1
    cost, node = neighbors[0]
    assert cost == 7
    assert node.id == "C"


def test_graph_update_node_type_resets_pattern():
    g = Graph()
    g.add_intersection(["1", (0, 0), "nothing"])
    assert g.nodes["1"].pattern == [None, None, None, None]

    assert g.update_node_type("1", "traffic_light") is True
    assert g.nodes["1"].nodeType == "traffic_light"
    assert g.nodes["1"].pattern == [0, 2, 0, 2]

    assert g.update_node_type("1", "stop_sign") is True
    assert g.nodes["1"].pattern == [None, None, None, None]
