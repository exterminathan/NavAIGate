// ---------- Config ----------
const API_BASE = "http://127.0.0.1:5000";

const API = {
  graph: `${API_BASE}/graph`,
  vehicles: `${API_BASE}/vehicles`,
  updateNode: `${API_BASE}/update_node`,
  stepLights: `${API_BASE}/update_traffic_lights`,
};
const NODE_TYPES = ["nothing", "stop_sign", "traffic_light"];
const POLL_MS = 20; // tick rate for vehicles
const GRAPH_REFRESH_MS = 2000; // refresh graph occasionally (safe & light)

// ---------- State ----------
let graph = { nodes: {}, roads: {} };
let vehicles = [];
let lastGraphFetch = 0;

// drawing state
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const dpi = () => window.devicePixelRatio || 1;

// world -> screen transform
let bounds = { minX: 0, minY: 0, maxX: 1, maxY: 1 };
let padding = 40; // px
let scale = 1,
  offsetX = 0,
  offsetY = 0;

function resizeCanvas() {
  const d = dpi();
  canvas.width = Math.floor(canvas.clientWidth * d);
  canvas.height = Math.floor(canvas.clientHeight * d);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(d, d);
}

function computeBounds() {
  const ids = Object.keys(graph.nodes);
  if (!ids.length) {
    bounds = { minX: 0, minY: 0, maxX: 1, maxY: 1 };
    return;
  }
  let minX = Infinity,
    minY = Infinity,
    maxX = -Infinity,
    maxY = -Infinity;
  for (const id of ids) {
    const n = graph.nodes[id];
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x);
    maxY = Math.max(maxY, n.y);
  }
  // avoid zero-size
  if (maxX === minX) {
    maxX = minX + 1;
  }
  if (maxY === minY) {
    maxY = minY + 1;
  }
  bounds = { minX, minY, maxX, maxY };
}

function fitView() {
  computeBounds();
  const w = canvas.clientWidth - padding * 2;
  const h = canvas.clientHeight - padding * 2;
  const sx = w / (bounds.maxX - bounds.minX);
  const sy = h / (bounds.maxY - bounds.minY);
  scale = Math.min(sx, sy);
  // center
  const graphW = (bounds.maxX - bounds.minX) * scale;
  const graphH = (bounds.maxY - bounds.minY) * scale;
  offsetX = (canvas.clientWidth - graphW) / 2 - bounds.minX * scale;
  offsetY = (canvas.clientHeight - graphH) / 2 - bounds.minY * scale;
}

function worldToScreen(x, y) {
  return { x: x * scale + offsetX, y: y * scale + offsetY };
}

// ---------- Fetch helpers ----------
async function fetchGraph() {
  const res = await fetch(API.graph);
  if (!res.ok) throw new Error("Graph fetch failed");
  const data = await res.json();
  // normalize to id->node / id->road maps if needed
  graph = {
    nodes: Array.isArray(data.nodes)
      ? Object.fromEntries(data.nodes.map((n) => [n.id, n]))
      : data.nodes,
    roads: Array.isArray(data.roads)
      ? Object.fromEntries(data.roads.map((r) => [r.id, r]))
      : data.roads,
  };
  lastGraphFetch = performance.now();
}

async function fetchVehicles() {
  const res = await fetch(API.vehicles);
  if (!res.ok) throw new Error("Vehicles fetch failed");
  vehicles = await res.json();
}

async function cycleNodeType(nodeId) {
  const node = graph.nodes[nodeId];
  const idx = NODE_TYPES.indexOf(node.type);
  const nextType = NODE_TYPES[(idx + 1) % NODE_TYPES.length];
  const res = await fetch(API.updateNode, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: nodeId, type: nextType }),
  });
  if (!res.ok) throw new Error("Failed to update node");
  node.type = nextType; // optimistic
}

async function stepAllLights() {
  const res = await fetch(API.stepLights, { method: "POST" });
  if (!res.ok) throw new Error("Failed to step lights");
}

// ---------- Drawing ----------
function draw() {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

  // roads
  ctx.lineWidth = 2;
  ctx.strokeStyle = "#2a3852";
  for (const id in graph.roads) {
    const r = graph.roads[id];
    const a = graph.nodes[r.entrance];
    const b = graph.nodes[r.exit];
    if (!a || !b) continue;
    const p1 = worldToScreen(a.x, a.y);
    const p2 = worldToScreen(b.x, b.y);
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
    // direction arrow
    const dx = p2.x - p1.x,
      dy = p2.y - p1.y;
    const len = Math.hypot(dx, dy) || 1;
    const ux = dx / len,
      uy = dy / len;
    const mx = p1.x + dx * 0.5,
      my = p1.y + dy * 0.5;
    const arrow = 6;
    ctx.beginPath();
    ctx.moveTo(mx, my);
    ctx.lineTo(mx - uy * arrow, my + ux * arrow);
    ctx.lineTo(mx + uy * arrow, my - ux * arrow);
    ctx.closePath();
    ctx.fillStyle = "#2a3852";
    ctx.fill();
  }

  // intersections
  for (const id in graph.nodes) {
    const n = graph.nodes[id];
    const p = worldToScreen(n.x, n.y);
    const r = 7;
    let fill = "#9aa4b2";
    if (n.type === "stop_sign") fill = "#4aa3ff";
    if (n.type === "traffic_light") fill = "#ff4d4d";
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = "#0b0f14";
    ctx.lineWidth = 2;
    ctx.stroke();

    // id label
    ctx.fillStyle = "rgba(232,238,247,.8)";
    ctx.font = "12px system-ui";
    ctx.fillText(id, p.x + 10, p.y - 10);
  }

  // vehicles
  for (const v of vehicles) {
    const road = graph.roads[v.road];
    if (!road) continue;
    const a = graph.nodes[road.entrance];
    const b = graph.nodes[road.exit];
    if (!a || !b) continue;

    // position along road from tail -> head based on queue index
    const N = Math.max(1, road.size);
    // v.pos is 0 at head;
    const margin = 0.15;
    const rawT = N === 1 ? 1 : 1 - v.pos / (N - 1);

    const t = rawT;

    const x = a.x + (b.x - a.x) * t;
    const y = a.y + (b.y - a.y) * t;
    const p = worldToScreen(x, y);

    const baseSize = 6;
    const sz = v.is_finished ? baseSize * 2 : baseSize;

    ctx.fillStyle = v.is_finished ? "#ffff00" : "#e8eef7";

    ctx.fillRect(p.x - sz / 2, p.y - sz / 2, sz, sz);

    //opt glow
    if (v.is_finished) {
      ctx.strokeStyle = "fff";
      ctx.lineWidth = 2;
      ctx.strokeRect(p.x - sz / 2, p.y - sz / 2, sz, sz);
    }
  }
}

// ---------- Interaction ----------
function pickNodeAt(clientX, clientY) {
  // find nearest node within threshold
  const rect = canvas.getBoundingClientRect();
  const x = clientX - rect.left;
  const y = clientY - rect.top;

  let bestId = null,
    bestDist = 1e9;
  for (const id in graph.nodes) {
    const n = graph.nodes[id];
    const p = worldToScreen(n.x, n.y);
    const dx = p.x - x,
      dy = p.y - y;
    const d2 = dx * dx + dy * dy;
    if (d2 < bestDist) {
      bestDist = d2;
      bestId = id;
    }
  }
  const pxThreshold = 14; // radius in px
  return Math.sqrt(bestDist) <= pxThreshold ? bestId : null;
}

canvas.addEventListener("click", async (e) => {
  const id = pickNodeAt(e.clientX, e.clientY);
  if (!id) return;
  try {
    setStatus(`Updating ${id}…`);
    await cycleNodeType(id);
    setStatus(`Node ${id} set to ${graph.nodes[id].type}`);
  } catch (err) {
    console.error(err);
    setStatus("Error updating node");
  }
});

document.getElementById("btnStepLights").addEventListener("click", async () => {
  try {
    setStatus("Stepping lights…");
    await stepAllLights();
    setStatus("Lights advanced");
  } catch (e) {
    console.error(e);
    setStatus("Failed to advance lights");
  }
});

document.getElementById("btnFit").addEventListener("click", () => {
  fitView();
});

// ---------- Loop ----------
function setStatus(s) {
  document.getElementById("status").textContent = s;
}

async function tick() {
  try {
    // refresh graph occasionally (in case server-side changes occur)
    if (performance.now() - lastGraphFetch > GRAPH_REFRESH_MS) {
      await fetchGraph();
      fitView();
    }
    await fetchVehicles();
    setStatus(
      `${vehicles.length} vehicles | ${Object.keys(graph.nodes).length} nodes / ${Object.keys(graph.roads).length} roads`,
    );
  } catch (e) {
    console.error(e);
    setStatus("Disconnected (retrying)…");
  }
  setTimeout(tick, POLL_MS);
}

function loopDraw() {
  draw();
  requestAnimationFrame(loopDraw);
}

// ---------- Boot ----------
function onResize() {
  resizeCanvas();
  fitView();
  draw();
}
window.addEventListener("resize", onResize);

(async function init() {
  resizeCanvas();
  await fetchGraph();
  fitView();
  tick();
  loopDraw();
})();
