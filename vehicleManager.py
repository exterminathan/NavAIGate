import threading
import time
import random
from vehicle import Vehicle
from graph import Graph
from bt_bot import setup_behavior_tree

class VehicleManager:
    def __init__(self, graph):
        self.vehicles = {}  # A dictionary to store vehicle objects
        self.remove_list  = []
        self.graph = graph
        self.vehicle_id = 0

    def update_vehicle_states(self):
        for vehicle in self.vehicles.values():
            vehicle.update()  # Update vehicle state using its Behavior Tree
            if not vehicle.path:
                self.remove_list.append(vehicle.id)
        
        for vehicle_id in self.remove_list:
            self.vehicles.pop(f"{vehicle_id}")
        self.remove_list = []

    def start_update_loop(self, interval=1):
        def loop():
            while True:
                if len(self.vehicles) < 30:
                    start_node = random.choice(list(self.graph.nodes.keys()))
                    goal_node = random.choice(list(self.graph.nodes.keys()))
                    while goal_node == start_node:
                        goal_node = random.choice(list(self.graph.nodes.keys()))
                    
                    vehicle = Vehicle(self.vehicle_id, self.graph.nodes[start_node], self.graph.nodes[goal_node], self.graph)
                    vehicle.bt = setup_behavior_tree(vehicle, self.graph)
                    self.vehicle_id += 1
                    self.add_vehicle(vehicle)
                self.update_vehicle_states()
                time.sleep(interval)
        
        # Start the update loop in a separate thread
        threading.Thread(target=loop, daemon=True).start()

    def add_vehicle(self, vehicle):
        self.vehicles[f"{vehicle.id}"] = vehicle

    def get_vehicles(self):
        # Return the current state of vehicles for the frontend
        return [vehicle.to_dict() for vehicle in self.vehicles.values()]
