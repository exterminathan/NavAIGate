# NavAIGate

An urban traffic simulator. Vehicles plan routes with **A\*** and make per-tick decisions at intersections (stop signs, traffic lights, right-of-way) via **behavior trees**, all rendered live in a browser canvas.

<!-- TODO: drop a screenshot or GIF at docs/preview.png -->
![NavAIGate visualizer](docs/preview.png)

## Quickstart

```bash
git clone https://github.com/exterminathan/NavAIGate.git
cd NavAIGate
```

**Linux / macOS:**
```bash
./start.sh
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

The bootstrap script installs dependencies, runs the test suite, then launches Flask. Open <http://127.0.0.1:5000/> once it prints `Running on ...`.

Click any intersection in the visualizer to cycle its type (`nothing` → `stop_sign` → `traffic_light`).

## Manual setup

<details>
<summary>Prefer to run each step yourself?</summary>

Recommended: use a virtual environment so dependencies don't pollute your system Python.

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r urban-traffic-sim/requirements.txt
pytest urban-traffic-sim/tests
python urban-traffic-sim/app.py
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r urban-traffic-sim/requirements.txt
pytest urban-traffic-sim/tests
python urban-traffic-sim/app.py
```

Python 3.10+ is recommended (the repo pins `3.10` in [.python-version](.python-version)). The `.venv/` folder is gitignored.
</details>

## Project layout

```
urban-traffic-sim/    Flask app, simulation core, BT, frontend assets
  tests/              pytest suite (graph, A*, BT smoke test)
docs/                 screenshots / preview assets
start.{sh,ps1}        one-command bootstrap
CLAUDE.md             deeper architecture notes
```

## Credits

Originally built as the final project for **CMPM 146 (Game AI)** at UC Santa Cruz by:

- [@exterminathan](https://github.com/exterminathan)
- [@calstephano](https://github.com/calstephano)
- [@Shredderman64](https://github.com/Shredderman64)
- [@ssinha8](https://github.com/ssinha8)

The original repo was private; this re-upload contains follow-up fixes and improvements. For deeper architecture notes see [CLAUDE.md](CLAUDE.md).
