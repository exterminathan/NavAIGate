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
    ["1", (50, 80), "nothing"],
    ["2", (180, 60), "stop_sign"],
    ["3", (320, 50), "nothing"],
    ["4", (480, 90), "stop_sign"],
    ["5", (580, 200), "nothing"],
    ["6", (450, 220), "traffic_light"],
    ["7", (300, 180), "nothing"],
    ["8", (150, 220), "traffic_light"],
    ["9", (60, 350), "nothing"],
    ["10", (220, 380), "stop_sign"],
    ["11", (380, 350), "traffic_light"],
    ["12", (550, 380), "nothing"],
    ["13", (480, 500), "stop_sign"],
    ["14", (320, 480), "nothing"],
    ["15", (150, 520), "nothing"],
    ["16", (50, 450), "stop_sign"],
    ["17", (280, 300), "traffic_light"]
]

edges = [
    ["1-2", 10, "1", "2", Direction.RIGHT], ["2-1", 10, "2", "1", Direction.LEFT],
    ["2-3", 12, "2", "3", Direction.RIGHT], ["3-2", 12, "3", "2", Direction.LEFT],
    ["3-4", 10, "3", "4", Direction.RIGHT], ["4-3", 10, "4", "3", Direction.LEFT],
    
    ["4-5", 15, "4", "5", Direction.DOWN], ["5-4", 15, "5", "4", Direction.UP],
    ["5-12", 10, "5", "12", Direction.DOWN], ["12-5", 10, "12", "5", Direction.UP],
    
    ["12-13", 10, "12", "13", Direction.DOWN], ["13-12", 10, "13", "12", Direction.UP],
    ["13-14", 12, "13", "14", Direction.LEFT], ["14-13", 12, "14", "13", Direction.RIGHT],
    ["14-15", 10, "14", "15", Direction.LEFT], ["15-14", 10, "15", "14", Direction.RIGHT],
    ["15-16", 10, "15", "16", Direction.LEFT], ["16-15", 10, "16", "15", Direction.RIGHT],
    
    ["16-9", 10, "16", "9", Direction.UP], ["9-16", 10, "9", "16", Direction.DOWN],
    ["9-1", 15, "9", "1", Direction.UP], ["1-9", 15, "1", "9", Direction.DOWN],

    ["2-8", 10, "2", "8", Direction.DOWN], ["8-2", 10, "8", "2", Direction.UP],
    ["8-10", 12, "8", "10", Direction.DOWN], ["10-8", 12, "10", "8", Direction.UP],
    ["3-7", 10, "3", "7", Direction.DOWN], ["7-3", 10, "7", "3", Direction.UP],
    ["6-4", 10, "6", "4", Direction.UP], ["4-6", 10, "4", "6", Direction.DOWN],
    ["7-11", 15, "7", "11", Direction.DOWN], ["11-7", 15, "11", "7", Direction.UP],
    ["10-14", 10, "10", "14", Direction.DOWN], ["14-10", 10, "14", "10", Direction.UP],
    
    ["17-7", 8, "17", "7", Direction.UP], ["7-17", 8, "7", "17", Direction.DOWN],
    ["17-11", 8, "17", "11", Direction.DOWN], ["11-17", 8, "11", "17", Direction.UP],
    ["17-6", 8, "17", "6", Direction.RIGHT], ["6-17", 8, "6", "17", Direction.LEFT],
    ["17-8", 8, "17", "8", Direction.LEFT], ["8-17", 8, "8", "17", Direction.RIGHT],

    ["6-5", 10, "6", "5", Direction.RIGHT],
    ["11-12", 10, "11", "12", Direction.RIGHT],
    ["10-9", 10, "10", "9", Direction.LEFT]
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
