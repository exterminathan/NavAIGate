from queue import Queue
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Graph:
    # each item in nodes is a list:
    # [id: string, nodeType: object, coords: (int, int)]

    # each item in connections is a list:
    # {id: string, length: int, entrance_id: node_id, exit_id: node_id, direction: int}
    #       length: maximum size of queue
    #       endpoints: entry and exit nodes by symbol  Ex: (12, 2)
    #       direction: direction of exit into node
    lights = ["RedLight", "YellowLight", "GreenLight", "YellowLight"]

    def __init__(self):
        self.roads = {}
        self.nodes = {}

    def add_road(self, road):
        entrance_node = self.nodes.get(road[2])
        exit_node = self.nodes.get(road[3])
        
        road_id = road[0]
        if entrance_node and exit_node:
            road = Road(*road)
            self.roads[road_id] = road
            entrance_node.add_exit(road_id)
            exit_node.add_entrance(road_id)
        else:
            raise ValueError("Entrance or exit node not found")
    
    def add_intersection(self, node):
        self.nodes[node[0]] = Node(*node)
        '''
        # sort entrances by direction
        newNode.entrances = sorted(newNode.entrances, key=lambda e :
                            Direction[e.direction].value)
        '''
    
    def neighbors(self, node):
        adj = []
        for road_id in node.exits:
            road = self.roads[road_id]
            adj.append((road.size, self.nodes[road.exit]))
        return adj
    
    def findEdge(self, start, end):
        for road_id in start.exits:
            road = self.roads[road_id]
            node_id = road.exit
            if self.nodes[node_id] == end:
                return self.roads[road_id]
        print(f"No edge found between {start.id} and {end.id}")
        return None
    
    def update(self):
        for road_id, road in self.roads:
            if road.queue[0] != None:
                road.queue[0].time += 1
        pass
    
    def update_node_type(self, id, new_type):
        node = self.nodes[id]
        node.nodeType = new_type
        if new_type == "traffic_light":
            node.pattern = [0, 2, 0, 2]
        else:
            node.pattern = [None, None, None, None]
        if self.nodes[id].nodeType == new_type:
            return True
        else:
            return False

    def to_dict(self):
        nodes = [node.to_dict() for node in self.nodes.values()]
        roads = [road.to_dict() for road in self.roads.values()]
        return {
            "nodes": nodes,
            "roads": roads
        }

class Road:
    def __init__(self, road_id, length, entrance_id, exit_id, direction):
        self.id = road_id
        self.size = length
        self.queue = [None] * length
        self.entrance = entrance_id
        self.exit = exit_id
        self.direction = direction

    # enters car into queue
    def enter(self, car):
        if self.queue[-1] == None:
            self.queue[-1] = car.id
            return True
        return False
    
    # advanced car along queue if there is space
    def advance(self, i):
        if i != 0 and self.queue[i-1] == None:
            self.queue.pop(i-1)
            self.queue.insert(i, None)
            return True
        return False
    
    # returns car at front of queue and sets location
    def exit_road(self):
        if self.queue[0] != None:
            car = self.queue.pop(0)
            self.queue.insert(0, None)
            return True
        return False

    def printQueue(self):
        print(self.queue)
    
    def to_dict(self):
        return {
            "id": self.id,
            "size": self.size,
            "queue": self.queue,
            "entrance": self.entrance,
            "exit": self.exit
        }

class Node:
    def __init__(self, node_id, coords, nodeType):
        self.id = node_id 
        self.entrances = []
        self.exits = []
        self.nodeType = nodeType
        if self.nodeType == "traffic_light":
            self.pattern = [0, 2, 0, 2]
        else:
            self.pattern = [None, None, None, None]
        self.x, self.y = coords[0], coords[1]

    def add_entrance(self, road_id):
        self.entrances.append(road_id)

    def add_exit(self, road_id):
        self.exits.append(road_id)
    
    # return dict version of the class for the Frontend
    def to_dict(self):
        return {
            "id": self.id,
            "entrances": self.entrances,
            "exits": self.exits,
            "type": self.nodeType,
            "pattern": self.pattern,
            "x": self.x,
            "y": self.y
        }


# TESTING/DEBUGGING
"""
graph = Graph()
graph.add_intersection(("A", (10, 10), "nothing"))
graph.add_intersection(("B", (20, 10), "nothing"))
graph.add_intersection(("B", (15, 30), "nothing"))
"""

"""
class TrafficQueue:
    # length: size of queue
    # dest: exit node of queue
    def __init__(self, length, dest):
        self.size = length
        self.queue = [None] * length
        self.dest = dest
    
    # enters car into queue
    def enter(self, car):
        if self.queue[-1] == None:
            self.queue[-1] = car
            return True
        return False
    
    # advanced car along queue if there is space
    def advance(self, i):
        if i != 0 and self.queue[i-1] == None:
            self.queue.pop(i-1)
            self.queue.insert(i, None)
            return True
        return False
    
    # returns car at front of queue and sets location
    def exit(self):
        if self.queue[0] != None:
            car = self.queue.pop(0)
            self.queue.insert(0, None)
            return car
        return None

    def printQueue(self):
        print(self.queue)
"""