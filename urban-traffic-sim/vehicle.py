import itertools
from graph import Graph
from heapq import heappop, heappush
from math import sqrt
import random

class Vehicle:
    _counter = itertools.count()

    def __init__(self, id, start, goal, graph):
        self.id = id
        self.bt = None
        self.path = self.graph_search(start, goal, graph)
        road = graph.findEdge(graph.nodes[self.path[0]], graph.nodes[self.path[1]])
        self.road = road
        self.pos = self.road.size - 1
        self.current = start.id
        self.path.pop(0)
        self.direction = self.road.direction
        self.time = 0
        self.is_finished = False
        r = random.randint(100, 230)
        g = random.randint(100, 230)
        b = random.randint(100, 230)
        self.color = "#{:02x}{:02x}{:02x}".format(r, g, b)

    def graph_search(self, start, goal, graph):
        pathFound = False
        frontier = []
        heappush(frontier, (0, next(self._counter), start))

        prev_node = dict()
        prev_node[start.id] = None
        pathcost = dict()
        pathcost[start.id] = 0

        while frontier:
            priority, _, current = heappop(frontier)
            if current.id == goal.id:
                pathFound = True
                break

            for neighbor_size, neighbor_node in graph.neighbors(current):
                new_cost = pathcost[current.id] + neighbor_size

                if neighbor_node.id not in pathcost or new_cost < pathcost[neighbor_node.id]:
                    pathcost[neighbor_node.id] = new_cost
                    priority = new_cost + self.heuristic(goal, neighbor_node)
                    heappush(frontier, (priority, next(self._counter), neighbor_node))
                    prev_node[neighbor_node.id] = current
        
        if pathFound:
            current = goal
            path = []
            while current != start:
                path.insert(0, current.id)
                current = prev_node[current.id]
            path.insert(0, start.id)
            return path
        else:
            return []

    def heuristic(self, goal, current):
        estimate = round(sqrt((goal.x - current.x)**2 + (goal.y - current.y)**2))
        return estimate
    
    def update(self):
        self.bt.execute()

    
    def get_coordinates(self, graph):
        # Calculate coordinates based on the road and position
        start_node = graph.nodes[self.current]  # Get start node
        end_node = graph.nodes[self.path[0]]  # Get end node
        
        # Calculate position between start_node and end_node
        t = self.pos / self.road.size  # Normalize position
        x = start_node.x + t * (end_node.x - start_node.x)
        y = start_node.y + t * (end_node.y - start_node.y)
        return (x, y)

    '''
    def update_speed(self):
        if self.road:
            self.pos += self.speed
    '''
    
    def to_dict(self):
        return {
            "id": self.id,
            "pos": self.pos,
            "path": self.path,
            "current": self.current,
            "road": self.road.id,
            "time": self.time,
            "is_finished": self.is_finished,
            "color": self.color
        }
