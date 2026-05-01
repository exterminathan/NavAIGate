# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

NavAIGate is an urban traffic simulator originally built for CMPM 146 (Game AI). A Flask backend simulates vehicles navigating a directed graph of roads/intersections; behavior trees drive each vehicle's decisions at intersections (traffic lights, stop signs, RHS yielding). A canvas-based frontend polls the backend and renders the live state.

All source lives under `urban-traffic-sim/`.

## Run / develop

The fastest path is the bootstrap script at the repo root: `.\start.ps1` (Windows) or `./start.sh` (Linux/macOS). It pip-installs from [urban-traffic-sim/requirements.txt](urban-traffic-sim/requirements.txt), runs the pytest suite, then launches Flask. The bootstrap calls the system `python` — if a `.venv/` exists at the repo root, activate it first and use the manual flow below.

For an iterative inner loop, work inside a venv:

```powershell
python -m venv .venv                              # one-time
.\.venv\Scripts\Activate.ps1                       # PowerShell; bash: source .venv/bin/activate
pip install -r urban-traffic-sim/requirements.txt
pytest urban-traffic-sim/tests                    # 10 tests, <1s
python urban-traffic-sim/app.py                   # serves http://127.0.0.1:5000/
```

Run a single test with `python -m pytest urban-traffic-sim/tests/test_graph.py::test_graph_find_edge_and_neighbors`.

Flask runs in debug mode (auto-reload). Each run truncates `bt_bot.log` and writes the BT structure on every vehicle spawn (`logging.basicConfig(..., filemode='w')` in `bt_bot.py`). Tests intentionally bypass `VehicleManager.start_update_loop` so no daemon thread leaks between tests.

## Architecture

The system has three concurrent loops:

1. **Server tick** ([vehicleManager.py](urban-traffic-sim/vehicleManager.py)): a daemon thread started in [app.py](urban-traffic-sim/app.py) sleeps `interval=0.4s`, spawns vehicles up to `num_vehicles=30`, and calls `vehicle.update()` (which executes the BT root) on each.
2. **Frontend poll** ([static/visualizer.js](urban-traffic-sim/static/visualizer.js)): polls `/vehicles` every `POLL_MS=20ms`, refreshes `/graph` every `GRAPH_REFRESH_MS=2000ms`, and triggers `/update_traffic_lights` once per `TRAFFIC_TIMER=5s` cycle (the clock in the toolbar).
3. **Frontend draw**: `requestAnimationFrame` loop that interpolates positions from the last polled snapshot.

The traffic-light cycle is **driven by the frontend clock**, not the server. If you change cycle timing, edit `TRAFFIC_TIMER` in `visualizer.js`. The server endpoint just rotates `node.pattern` by one slot when called.

### Graph model ([graph.py](urban-traffic-sim/graph.py))

- **Roads are one-directional queue-based cells**, not continuous space. A `Road` has a fixed `size` and a `queue` array of length `size`; index `0` is the front (closest to the exit node), `size-1` is the rear. Bidirectional connections require two `Road` entries (e.g. `1-2` and `2-1`).
- A vehicle's `pos` is its index into `road.queue`. `road.advance(i)` moves it from `i` to `i-1` if that cell is empty. `road.exit_road()` pops the front car.
- `Direction` is an `Enum` (UP=0, RIGHT=1, DOWN=2, LEFT=3). Traffic light state is a 4-element `pattern` indexed by `Direction.value`; the global `lights` list (`["RedLight","YellowLight","GreenLight","YellowLight"]`) maps pattern values to colors. RHS yielding uses `(direction + 1) % 4`.
- Node types: `"nothing"`, `"stop_sign"`, `"traffic_light"`. Clicking a node in the UI cycles through these via `/update_node`.

### Pathfinding ([vehicle.py](urban-traffic-sim/vehicle.py))

A* over the graph: cost = sum of road sizes, heuristic = euclidean distance between node `(x,y)` coords. Uses `itertools.count()` as a class-level tiebreaker for `heapq`. `Vehicle.__init__` immediately enters the first road's rear cell — the start node is popped from `path` before the BT ever runs.

### Behavior tree ([bt_bot.py](urban-traffic-sim/bt_bot.py), [bt_nodes.py](urban-traffic-sim/bt_nodes.py), [behaviors.py](urban-traffic-sim/behaviors.py), [checks.py](urban-traffic-sim/checks.py))

A fresh tree is constructed **per vehicle** in `setup_behavior_tree(vehicle, graph)` — `Check` and `Action` leaves bind the vehicle/graph references at construction time, so the tree is not shareable across vehicles.

Top-level shape:
```
Selector (root)
├── Sequence "Reached Intersection"           # only if at front of queue
│   ├── Check front_of_queue
│   └── Selector "Intersection Strategies"
│       ├── Selector "Traffic Light Strategy" # red/yellow → stop, green → pass
│       ├── Sequence "Stop Sign Strategy"     # stop one tick, then pass
│       └── Sequence "Empty Intersection"     # nodeType == "nothing" → pass
└── Action move_on_road                        # default: advance one cell
```

Key conventions in `bt_nodes.py`: `Selector` returns success on first child success; `Sequence` returns failure on first child failure. `Check` and `Action` leaves return bool but **most actions return `True` unconditionally** — failure is signalled by `Check` nodes upstream, not by action results. `bt_bot.py` contains a large commented-out block of congestion-avoidance / timeout strategies; `behaviors.py` and `checks.py` are explicitly split between `# USED` and `# UNUSED` sections — the unused functions are kept for reference.

### Graph configuration

The active graph is hardcoded in [app.py](urban-traffic-sim/app.py) (`nodes` and `edges` lists). [graphOptions.txt](urban-traffic-sim/graphOptions.txt) holds alternate map layouts that can be pasted in. There is no loader — to switch maps, replace the literals.

## Frontend ↔ backend contract

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Renders `templates/visualizer.html` |
| `/graph` | GET | `{nodes, roads}` — full graph snapshot, polled every 2s |
| `/vehicles` | GET | List of vehicle dicts, polled every 20ms |
| `/update_node` | POST | `{id, type}` cycles a node's type (also resets `pattern`) |
| `/update_traffic_lights` | POST | Advances every traffic-light node's pattern by one slot |

`Vehicle.to_dict()` and `Road.to_dict()`/`Node.to_dict()` define the wire shape — touching field names here means updating `visualizer.js` (which references `v.road`, `v.pos`, `v.is_finished`, `v.color`, `road.entrance`/`exit`/`size`, `node.x`/`y`/`type`).
