import sys
from vehicle import Vehicle
from graph import Graph, Node, Road
from checks import *


# USED
def stop_light(vehicle, graph):
    """
    Basically just waits without changing anything.
    """

    # Return True for 1 tick
    vehicle.time += 1
    return True

def pass_intersection(vehicle, graph):
    """
    Attempt to Drive through an intersection.
    Swap roads correctly etc.
    """

    # pre-check for if at final node to exit early
    if len(vehicle.path) <= 1:
        if vehicle.road:
            vehicle.road.exit_road()
        vehicle.path = []
        return True


    next_node = graph.nodes[vehicle.path[0]]

    # if final destination node
    if len(vehicle.path) == 1:
        vehicle.path.pop(0)
        vehicle.road.exit_road()
        return True
    
    # next road in graph
    road = graph.findEdge(next_node, graph.nodes[vehicle.path[1]])

    # if road is clear, enter
    if road.queue[road.size - 1] == None:
        vehicle.road.exit_road()

        vehicle.current = graph.nodes[vehicle.path[0]].id
        vehicle.path.pop(0)
        vehicle.road = road
        vehicle.direction = road.direction
        vehicle.pos = road.size - 1
        vehicle.time = 0
        vehicle.road.enter(vehicle)

        # fix for when at intersection so vehicle does not stall
        if vehicle.road.advance(vehicle.pos):
            vehicle.pos -= 1

        return True
    vehicle.time += 1
    return True

def move_on_road(vehicle, graph):
    if vehicle.road and vehicle.road.advance(vehicle.pos):
        vehicle.pos -= 1
        # vehicle.update_speed()
    return True

# UNUSED
def continue_driving(vehicle, target_speed=10):
    """
    Continues driving the vehicle at the target speed.
    """
    if vehicle.speed < target_speed:
        vehicle.speed = target_speed
    vehicle.update_speed()
    return True

def slow_to_stop(vehicle, speed_reduction):
    """
    Gradually slows the vehicle down to a stop.
    """
    if vehicle.speed > speed_reduction:
        vehicle.speed -= speed_reduction
    else:
        vehicle.speed = 0

    vehicle.update_speed()

    return vehicle.speed == 0

def recalculate_path_if_congested(vehicle, graph):
    next_node = graph.nodes[vehicle.path[0]] if vehicle.path else None
    if is_road_busy(vehicle, graph):
        vehicle.path = vehicle.graph_search(vehicle.current, vehicle.path[-1], graph)
        return True
    return False

def minimize_congestion(vehicle, graph):
    """
    Prioritizes routes with shorter queues to avoid congestion

    """
    if vehicle.path:
        next_node = graph.nodes[vehicle.path[0]]
        road = graph.findEdge(vehicle.current, next_node)
        if road:
            # only if road is half full or less
            return len([v for v in road.queue if v is not None]) < road.size // 2
    return False

def slow_for_congestion(vehicle):
    if vehicle.speed > 2:
        vehicle.speed -=2
    
    vehicle.update_speed()
    return True


