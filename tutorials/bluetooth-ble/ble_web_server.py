#!/usr/bin/env python3
"""
BLE Web Server — connects to ESP32 BLE peripheral and streams
sensor data to a browser dashboard via WebSocket.

Prerequisites:
  pip3 install bleak aiohttp

Usage:
  python3 ble_web_server.py
  Then open http://localhost:8080
"""

import asyncio
import json
import time

from aiohttp import web
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

DEVICE_NAME = "ESP32"
SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
SENSOR_CHAR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
LED_CHAR_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214"

HOST = "0.0.0.0"
PORT = 8080

BLE_SCAN_TIMEOUT = 10.0
BLE_RECONNECT_DELAY = 3.0


class BleWebBridge:
    def __init__(self):
        self.ws_clients: set[web.WebSocketResponse] = set()
        self.ble_client: BleakClient | None = None
        self.connected = False
        self.last_value: str | None = None
        self.history: list[dict] = []

    async def broadcast(self, msg: dict):
        payload = json.dumps(msg)
        stale = set()
        for ws in self.ws_clients:
            try:
                await ws.send_str(payload)
            except ConnectionResetError:
                stale.add(ws)
        self.ws_clients -= stale

    async def on_notify(self, _sender, data: bytearray):
        value = data.decode("utf-8", errors="replace")
        self.last_value = value
        entry = {"value": value, "ts": time.time()}
        self.history.append(entry)
        if len(self.history) > 200:
            self.history = self.history[-200:]
        await self.broadcast({"type": "sensor", **entry})

    async def ble_loop(self):
        while True:
            try:
                await self.broadcast({"type": "status", "state": "scanning"})
                print(f"Scanning for '{DEVICE_NAME}' ...")
                device = await BleakScanner.find_device_by_name(
                    DEVICE_NAME, timeout=BLE_SCAN_TIMEOUT
                )

                if device is None:
                    print(f"'{DEVICE_NAME}' not found, retrying ...")
                    await self.broadcast(
                        {"type": "status", "state": "not_found"}
                    )
                    await asyncio.sleep(BLE_RECONNECT_DELAY)
                    continue

                print(f"Found {device.name} ({device.address})")
                await self.broadcast(
                    {"type": "status", "state": "connecting", "address": device.address}
                )

                async with BleakClient(device) as client:
                    self.ble_client = client
                    self.connected = True
                    print(f"Connected to {device.name}")
                    await self.broadcast(
                        {"type": "status", "state": "connected", "address": device.address}
                    )

                    initial = await client.read_gatt_char(SENSOR_CHAR_UUID)
                    await self.on_notify(None, initial)

                    await client.start_notify(SENSOR_CHAR_UUID, self.on_notify)

                    while client.is_connected:
                        await asyncio.sleep(1)

                    print("BLE connection lost")

            except (BleakError, TimeoutError, OSError) as e:
                print(f"BLE error: {e}")
            finally:
                self.ble_client = None
                self.connected = False
                await self.broadcast({"type": "status", "state": "disconnected"})

            await asyncio.sleep(BLE_RECONNECT_DELAY)

    async def handle_led(self, state: int):
        if self.ble_client and self.connected:
            try:
                await self.ble_client.write_gatt_char(
                    LED_CHAR_UUID, state.to_bytes(1, "big")
                )
                await self.broadcast({"type": "led", "state": state})
                return True
            except (BleakError, OSError) as e:
                print(f"LED write error: {e}")
        return False


bridge = BleWebBridge()

HTML_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ESP32 BLE Dashboard</title>
<style>
  :root { --bg: #0f172a; --card: #1e293b; --border: #334155;
          --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
          --green: #4ade80; --red: #f87171; --yellow: #fbbf24; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: system-ui, -apple-system, sans-serif;
         background: var(--bg); color: var(--text); padding: 1.5rem; }
  h1 { font-size: 1.4rem; font-weight: 600; margin-bottom: 1.5rem; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1rem; margin-bottom: 1rem; }
  .card { background: var(--card); border: 1px solid var(--border);
          border-radius: 0.75rem; padding: 1.25rem; }
  .card h2 { font-size: 0.85rem; color: var(--muted); text-transform: uppercase;
             letter-spacing: 0.05em; margin-bottom: 0.75rem; }

  .status-dot { display: inline-block; width: 10px; height: 10px;
                border-radius: 50%; margin-right: 0.5rem; vertical-align: middle; }
  .status-dot.connected    { background: var(--green); }
  .status-dot.scanning     { background: var(--yellow); animation: pulse 1s infinite; }
  .status-dot.disconnected { background: var(--red); }
  .status-dot.connecting   { background: var(--yellow); animation: pulse 0.5s infinite; }
  .status-dot.not_found    { background: var(--red); }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

  #status-text { font-size: 0.95rem; }
  #address { color: var(--muted); font-size: 0.8rem; margin-top: 0.25rem; }

  .value-big { font-size: 3rem; font-weight: 700; color: var(--accent);
               font-variant-numeric: tabular-nums; }
  #last-update { color: var(--muted); font-size: 0.8rem; margin-top: 0.5rem; }

  canvas { width: 100%; height: 180px; display: block; margin-top: 0.5rem; }

  .led-row { display: flex; gap: 0.75rem; margin-top: 0.75rem; }
  .led-btn { padding: 0.5rem 1.25rem; border: 1px solid var(--border);
             border-radius: 0.5rem; background: var(--card); color: var(--text);
             cursor: pointer; font-size: 0.9rem; transition: background 0.15s; }
  .led-btn:hover { background: var(--border); }
  .led-btn.active { border-color: var(--accent); background: #0c4a6e; }

  .log { max-height: 200px; overflow-y: auto; font-family: monospace;
         font-size: 0.8rem; color: var(--muted); line-height: 1.6; }
</style>
</head>
<body>
<h1>ESP32 BLE Dashboard</h1>

<div class="grid">
  <div class="card">
    <h2>Connection</h2>
    <div><span id="status-dot" class="status-dot disconnected"></span>
         <span id="status-text">Disconnected</span></div>
    <div id="address"></div>
  </div>

  <div class="card">
    <h2>Sensor Value</h2>
    <div id="sensor-value" class="value-big">--</div>
    <div id="last-update"></div>
  </div>

  <div class="card">
    <h2>LED Control</h2>
    <div class="led-row">
      <button class="led-btn" onclick="sendLed(1)">ON</button>
      <button class="led-btn" onclick="sendLed(0)">OFF</button>
    </div>
  </div>
</div>

<div class="card" style="margin-bottom:1rem">
  <h2>Sensor History</h2>
  <canvas id="chart"></canvas>
</div>

<div class="card">
  <h2>Event Log</h2>
  <div id="log" class="log"></div>
</div>

<script>
const MAX_POINTS = 100;
const history = [];
let ws;

function connect() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === "sensor") onSensor(msg);
    else if (msg.type === "status") onStatus(msg);
    else if (msg.type === "led") onLed(msg);
  };
  ws.onclose = () => setTimeout(connect, 2000);
}

function onSensor(msg) {
  document.getElementById("sensor-value").textContent = msg.value;
  const d = new Date(msg.ts * 1000);
  document.getElementById("last-update").textContent = d.toLocaleTimeString();
  const num = parseFloat(msg.value);
  if (!isNaN(num)) {
    history.push({ v: num, t: msg.ts });
    if (history.length > MAX_POINTS) history.shift();
    drawChart();
  }
  addLog(`Sensor: ${msg.value}`);
}

function onStatus(msg) {
  const dot = document.getElementById("status-dot");
  const txt = document.getElementById("status-text");
  const addr = document.getElementById("address");
  dot.className = "status-dot " + msg.state;
  const labels = { scanning: "Scanning...", connecting: "Connecting...",
                   connected: "Connected", disconnected: "Disconnected",
                   not_found: "Device not found" };
  txt.textContent = labels[msg.state] || msg.state;
  addr.textContent = msg.address || "";
  addLog(`Status: ${msg.state}` + (msg.address ? ` (${msg.address})` : ""));
}

function onLed(msg) {
  document.querySelectorAll(".led-btn").forEach((b, i) => {
    b.classList.toggle("active", (i === 0 && msg.state === 1) ||
                                  (i === 1 && msg.state === 0));
  });
  addLog(`LED: ${msg.state ? "ON" : "OFF"}`);
}

function sendLed(state) {
  if (ws && ws.readyState === 1) ws.send(JSON.stringify({ cmd: "led", state }));
}

function addLog(text) {
  const el = document.getElementById("log");
  const t = new Date().toLocaleTimeString();
  el.innerHTML += `<div>${t} — ${text}</div>`;
  el.scrollTop = el.scrollHeight;
}

function drawChart() {
  const canvas = document.getElementById("chart");
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  const W = rect.width, H = rect.height;
  const pad = { t: 10, r: 10, b: 24, l: 40 };
  const cw = W - pad.l - pad.r, ch = H - pad.t - pad.b;

  ctx.clearRect(0, 0, W, H);

  if (history.length < 2) return;

  const vals = history.map(h => h.v);
  let min = Math.min(...vals), max = Math.max(...vals);
  if (min === max) { min -= 1; max += 1; }
  const range = max - min;

  // grid
  ctx.strokeStyle = "#334155";
  ctx.lineWidth = 0.5;
  ctx.fillStyle = "#94a3b8";
  ctx.font = "11px system-ui";
  ctx.textAlign = "right";
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + ch - (i / 4) * ch;
    const v = min + (i / 4) * range;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + cw, y); ctx.stroke();
    ctx.fillText(v.toFixed(1), pad.l - 6, y + 4);
  }

  // line
  ctx.strokeStyle = "#38bdf8";
  ctx.lineWidth = 2;
  ctx.lineJoin = "round";
  ctx.beginPath();
  history.forEach((h, i) => {
    const x = pad.l + (i / (history.length - 1)) * cw;
    const y = pad.t + ch - ((h.v - min) / range) * ch;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();

  // time labels
  ctx.fillStyle = "#94a3b8";
  ctx.textAlign = "center";
  const first = new Date(history[0].t * 1000).toLocaleTimeString();
  const last = new Date(history[history.length - 1].t * 1000).toLocaleTimeString();
  ctx.fillText(first, pad.l, H - 4);
  ctx.fillText(last, pad.l + cw, H - 4);
}

window.addEventListener("resize", drawChart);
connect();
</script>
</body>
</html>
"""


async def handle_index(_request):
    return web.Response(text=HTML_PAGE, content_type="text/html")


async def handle_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    bridge.ws_clients.add(ws)

    state = "connected" if bridge.connected else "disconnected"
    await ws.send_str(json.dumps({"type": "status", "state": state}))

    for entry in bridge.history[-100:]:
        await ws.send_str(json.dumps({"type": "sensor", **entry}))

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data.get("cmd") == "led":
                    await bridge.handle_led(int(data["state"]))
    finally:
        bridge.ws_clients.discard(ws)

    return ws


async def start_ble_background(app):
    app["ble_task"] = asyncio.create_task(bridge.ble_loop())


async def stop_ble_background(app):
    app["ble_task"].cancel()
    try:
        await app["ble_task"]
    except asyncio.CancelledError:
        pass


def main():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/ws", handle_ws)
    app.on_startup.append(start_ble_background)
    app.on_cleanup.append(stop_ble_background)

    print(f"Starting BLE Web Server on http://localhost:{PORT}")
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
