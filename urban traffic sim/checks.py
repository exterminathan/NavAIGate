from graph import Graph, Node, Road, Direction

lights = ["RedLight", "YellowLight", "GreenLight", "YellowLight"]

def front_of_queue(vehicle, graph):
    """
    Returns true if vehicle is at front of queue
    Returns false otherwise
    """
    if vehicle.road:
        if vehicle.pos == 0:
            return True
    return False

def get_traffic_light_RY(vehicle, graph):
    """
    Checks if there is an upcoming traffic light.
    Returns the color of the traffic light if present.
    Returns None if there is no traffic light.
    """
    if vehicle.path:
        next_node = graph.nodes[vehicle.path[0]]
        """
        road = graph.findEdge(vehicle.current, next_node)
        if road and road.roadType in ["RedLight", "YellowLight", "GreenLight"]:
            return road.roadType
        """
        if next_node.nodeType == "traffic_light":
            light_color = lights[next_node.pattern[vehicle.direction.value]]
            if light_color == "RedLight" or light_color == "YellowLight":
                return True
    return False

def get_traffic_light_green(vehicle, graph):
    """
    Checks if there is an upcoming traffic light.
    Returns the color of the traffic light if present.
    Returns None if there is no traffic light.
    """
    if vehicle.path:
        next_node = graph.nodes[vehicle.path[0]]
        """
        road = graph.findEdge(vehicle.current, next_node)
        if road and road.roadType in ["RedLight", "YellowLight", "GreenLight"]:
            return road.roadType
        """
        if next_node.nodeType == "traffic_light":
            light_color = lights[next_node.pattern[vehicle.direction.value]]
            return light_color == "GreenLight"
    return False

def check_empty_intersection(vehicle, graph):
    """
    Checks if there is an upcoming traffic light.
    Returns the color of the traffic light if present.
    Returns None if there is no traffic light.
    """
    if vehicle.path:
        next_node = graph.nodes[vehicle.path[0]]
        """
        road = graph.findEdge(vehicle.current, next_node)
        if road and road.roadType in ["RedLight", "YellowLight", "GreenLight"]:
            return road.roadType
        """
        if next_node.nodeType == "nothing":
            return True
    return False

def has_stop_sign(vehicle, graph):
    """
    Checks if there is a stop sign at the current road the vehicle is on.
    """
    if vehicle.path:
        next_node = graph.nodes[vehicle.path[0]]
        """
        road = graph.findEdge(vehicle.current, next_node)
        if road and road.roadType == "StopSign":
            return True
        """
        if next_node.nodeType == "stop_sign":
            return True
    return False

def check_other_vehicles(vehicle, graph):
    """
    Checks if there are other vehicles waiting at the intersection
    """
    def is_rhs(v, other_v):
        rhs_dir = (v.direction + 1) % len(Direction)
        if other_v.direction == rhs_dir:
            return True
        return False

    # finds the next node in vehicle's path
    next_node = vehicle.path[0]
    # iterates through other entrances at that node
    for road in next_node.entrances:
        if road != vehicle.road and road.queue[0] != None:
            other_v = road.queue[0]
            # if other car has been waiting longer
            if other_v.time > vehicle.time:
                return False
            # if other car is on right hand side
            elif other_v.time == vehicle.time and is_rhs(vehicle, other_v):
                return False
    return True

def check_rhs(vehicle, graph):
    """
    Checks the road to the vehicle's right
    """
    rhs_direction = (vehicle.direction + 1) % len(Direction)
    for road in vehicle.current.entrances:
        if road.direction == Direction(rhs_direction).name:
            return road.queue[0] is not None
    
    return False
    
    
def check_lhs(vehicle, graph):
    """
    Checks the road to the vehicle's left
    """
    lhs_direction = (vehicle.direction + 3) % len(Direction)
    for road in vehicle.current.entrances:
        if road.direction == Direction(lhs_direction).name:
            return road.queue[0] is not None
    
    return False

def is_intersection_clear(vehicle, graph):
    """
    Checks if intersection is clear after stop sign
    """
    next_node = graph.nodes[vehicle.path[0]] if vehicle.path else None
    if next_node and next_node.nodeType == "stop_sign":
        return all(road.queue[0] is None for road in next_node.entrances)
    return True

def has_fully_stopped(vehicle):
    return vehicle.speed == 0

def has_not_stopped(vehicle, graph):
    return vehicle.time == 0

def is_road_busy(vehicle, graph, threshold=0.8):
    next_node = vehicle.path[0] if vehicle.path else None
    if next_node:
        road = graph.findEdge(vehicle.current, next_node)
        if road:
            congestion_ratio = len([v for v in road.queue if v]) / road.size
            return congestion_ratio >= threshold
    return False

def is_at_intersection(vehicle, graph):
    current_node = graph.nodes[vehicle.path[0]] if vehicle.path else None
    if current_node and current_node.nodeType in ["traffic_light", "stop_sign"]:
        return True
    return False



# Alternate Checks
# because im dumb
def is_intersection_clear_after_stop(vehicle, graph):
    return is_intersection_clear(vehicle, graph) and has_fully_stopped(vehicle)
