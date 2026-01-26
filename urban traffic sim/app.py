from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import render_template
from graph import Graph, Direction
from math import sqrt
from vehicle import Vehicle
from vehicleManager import VehicleManager
from bt_bot import setup_behavior_tree

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Example graph data
nodes = [
    ["3", (50, 50), "nothing"],
    ["4", (140, 80), "stop_sign"],
    ["5", (250, 100), "nothing"],
    ["6", (380, 160), "stop_sign"],
    ["7", (500, 280), "stop_sign"],
    ["8", (550, 350), "nothing"],
    ["9", (450, 350), "stop_sign"],
    ["10", (450, 290), "traffic_light"],
    ["11", (310, 200), "nothing"],
    ["12", (350, 300), "traffic_light"],
    ["13", (320, 360), "traffic_light"],
    ["14", (200, 250), "traffic_light"],
    ["15", (180, 320), "traffic_light"],
    ["16", (100, 300), "nothing"],
    ["17", (80, 200), "stop_sign"],
    ["18", (150, 150), "nothing"]
    ]

edges = [
    ["3-4", 10, "3", "4", Direction.RIGHT],
    ["4-3", 10, "4", "3", Direction.LEFT],
    ["5-4", 10, "5", "4", Direction.UP],
    ["6-5", 10, "6", "5", Direction.UP],
    ["7-6", 10, "7", "6", Direction.UP],
    ["8-7", 10, "8", "7", Direction.UP],
    ["9-8", 10, "9", "8", Direction.RIGHT],
    ["13-9", 10, "13", "9", Direction.RIGHT],
    ["15-13", 10, "15", "13", Direction.RIGHT],
    ["16-15", 10, "16", "15", Direction.RIGHT],
    ["17-16", 10, "17", "16", Direction.DOWN],
    ["3-17", 10, "3", "17", Direction.DOWN],
    ["4-18", 10, "4", "18", Direction.DOWN],
    ["18-4", 10, "18", "4", Direction.UP],
    ["14-18", 10, "14", "18", Direction.UP],
    ["18-14", 10, "18", "14", Direction.DOWN],
    ["14-17", 10, "14", "17", Direction.LEFT],
    ["17-14", 10, "17", "14", Direction.RIGHT],
    ["14-15", 10, "14", "15", Direction.DOWN],
    ["15-14", 10, "15", "14", Direction.UP],
    ["14-12", 10, "14", "12", Direction.RIGHT],
    ["12-14", 10, "12", "14", Direction.LEFT],
    ["12-13", 10, "12", "13", Direction.DOWN],
    ["12-10", 10, "12", "10", Direction.RIGHT],
    ["10-12", 10, "10", "12", Direction.LEFT],
    ["10-9", 10, "10", "9", Direction.DOWN],
    ["10-7", 10, "10", "7", Direction.RIGHT],
    ["10-11", 10, "10", "11", Direction.UP],
    ["11-10", 10, "11", "10", Direction.DOWN],
    ["11-6", 10, "11", "6", Direction.RIGHT],
    ["6-11", 10, "6", "11", Direction.LEFT]
    ]

graph = Graph()
for node in nodes:
    graph.add_intersection(node)

for edge in edges:
    graph.add_road(edge)

# Initialize the VehicleManager and start its update loop
vehicle_manager = VehicleManager(graph)
vehicle_manager.start_update_loop(interval=.4)

@app.route('/')
def index():
    return render_template('visualizer.html')

@app.route('/graph')
def get_graph():
    return jsonify(graph.to_dict())

@app.route('/update_node', methods=['POST'])
def update_node():
    data = request.json
    node_id = data.get('id')
    new_type = data.get('type')
    
    if not node_id or not new_type:
        return jsonify({'error': 'Invalid request data'}), 400
    
    # Assuming `graph` has a method to update a node type
    success = graph.update_node_type(node_id, new_type)
    
    if success:
        return jsonify({'status': 'success', 'id': node_id, 'type': new_type})
    else:
        return jsonify({'error': 'Node not found or update failed'}), 404

@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    # Return the state of vehicles for the frontend
    return jsonify(vehicle_manager.get_vehicles())

@app.route('/update_traffic_lights', methods=['POST'])
def update_traffic_lights():
    for node in graph.nodes.values():
        if node.nodeType == "traffic_light":
            # Update the traffic light pattern here, for example:
            pattern = []
            for index in node.pattern:
                new_index = (index + 1) % 4
                pattern.insert(0, new_index)
            node.pattern = pattern
    return jsonify({"message": "Traffic lights updated"}), 200

if __name__ == '__main__':
    app.run(debug=True)
    # http://127.0.0.1:5000/
