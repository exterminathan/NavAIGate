from graph import Graph
from heapq import heappop, heappush
from math import sqrt

class Vehicle:
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

    def graph_search(self, start, goal, graph):
        pathFound = False
        frontier = []
        heappush(frontier, (0, start))

        prev_node = dict()
        prev_node[start.id] = None
        pathcost = dict()
        pathcost[start.id] = 0

        while frontier:
            priority, current = heappop(frontier)
            if current == goal:
                pathFound = True
                break
            for neighbor in graph.neighbors(current):
                neighbor_cost, next = neighbor[0], neighbor[1]
                new_cost = pathcost[current.id] + neighbor_cost
                if next.id not in pathcost or new_cost < pathcost[next.id]:
                    pathcost[next.id] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heappush(frontier, (priority, next))
                    prev_node[next.id] = current
        
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
            "is_finished": self.is_finished
        }
