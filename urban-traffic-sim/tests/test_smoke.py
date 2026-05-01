"""End-to-end exercise of the BT + graph + vehicle stack without Flask.

We deliberately bypass VehicleManager.start_update_loop so no daemon thread
is spawned during the test run.
"""
from bt_bot import setup_behavior_tree
from graph import Direction, Graph
from vehicle import Vehicle
from vehicleManager import VehicleManager


def _build_smoke_graph():
    """Linear A -> B -> C -> D route covering all three intersection types."""
    g = Graph()
    nodes = [
        ["A", (0, 0), "nothing"],
        ["B", (10, 0), "stop_sign"],
        ["C", (20, 0), "traffic_light"],
        ["D", (30, 0), "nothing"],
    ]
    edges = [
        ["A-B", 5, "A", "B", Direction.RIGHT],
        ["B-A", 5, "B", "A", Direction.LEFT],
        ["B-C", 5, "B", "C", Direction.RIGHT],
        ["C-B", 5, "C", "B", Direction.LEFT],
        ["C-D", 5, "C", "D", Direction.RIGHT],
        ["D-C", 5, "D", "C", Direction.LEFT],
    ]
    for n in nodes:
        g.add_intersection(n)
    for e in edges:
        g.add_road(e)
    return g


def _spawn(manager, graph, vehicle_id, start, goal):
    v = Vehicle(vehicle_id, graph.nodes[start], graph.nodes[goal], graph)
    v.bt = setup_behavior_tree(v, graph)
    manager.add_vehicle(v)
    return v


def test_single_vehicle_reaches_goal():
    g = _build_smoke_graph()
    vm = VehicleManager(g)

    _spawn(vm, g, 0, "A", "D")
    assert len(vm.vehicles) == 1

    for _ in range(100):
        vm.update_vehicle_states()
        if not vm.vehicles:
            break

    assert not vm.vehicles, "vehicle did not reach its goal within 100 ticks"


def test_multiple_vehicles_no_exceptions():
    g = _build_smoke_graph()
    vm = VehicleManager(g)

    for i in range(3):
        _spawn(vm, g, i, "A", "D")

    # No assertion about exact movement here — just that the BT loop survives
    # 100 ticks of a congested route without raising.
    for _ in range(100):
        vm.update_vehicle_states()

    # population is bounded by what we spawned (manager only auto-spawns inside
    # start_update_loop, which we never called)
    assert len(vm.vehicles) <= 3
