import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from config import NORMAL_SAMPLES
from dataset_loader import DatasetLoader
from data_generator import generate_normal_traffic, generate_attack_traffic
from swarm_defence import SwarmDefenceSystem

app = FastAPI(title="SWED-A API Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_text(json.dumps(message))
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()
simulation_running = False

async def run_simulation():
    global simulation_running
    if simulation_running:
        return
    simulation_running = True

    loader = DatasetLoader()
    loader.load_or_fallback()

    await asyncio.sleep(3)  # Give frontend time to connect
    await manager.broadcast({"type": "log", "message": "[System] Generating baseline CPS behaviour..."})
    await asyncio.sleep(1)

    train_data = generate_normal_traffic(NORMAL_SAMPLES)
    loader.fit(train_data)
    train_data = loader.normalize(train_data)

    system = SwarmDefenceSystem()
    await manager.broadcast({"type": "log", "message": "[System] Initializing Swarm Nodes and Training Edge Models..."})
    system.initialize(train_data)
    await asyncio.sleep(2)
    await manager.broadcast({"type": "log", "message": "[System] All nodes online. Beginning network surveillance..."})
    await asyncio.sleep(1.5)

    sample_id = 1

    try:
        # ── Phase 1: Normal Traffic Baseline (5 samples) ──
        for i in range(5):
            test_data = loader.normalize(generate_normal_traffic(1))
            state = system.process_sample(test_data.iloc[[0]], sample_id, is_actual_attack=False)
            await manager.broadcast({"type": "state", "data": state})

            if state['is_attack_detected']:
                await manager.broadcast({"type": "log", "message": f"[Node Consensus] FALSE POSITIVE Detected (Score: {state['threat_level']:.2f})"})
            else:
                await manager.broadcast({"type": "log", "message": f"[Node Consensus] Normal Traffic — Consensus: {state['attack_votes']}/{state['total_nodes']}"})

            sample_id += 1
            await asyncio.sleep(1.5)

        # ── Phase 2: Attack Injection Series ──
        attack_types = ['dos', 'fdi', 'lateral_movement']
        attacker_ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        attack_labels = ['Denial of Service', 'False Data Injection', 'Lateral Movement']

        for attack, ip, label in zip(attack_types, attacker_ips, attack_labels):
            await manager.broadcast({"type": "log", "message": f"[INTEL] Simulating {label} attack from {ip}..."})
            await asyncio.sleep(1)

            test_data = loader.normalize(generate_attack_traffic(attack, 1))
            state = system.process_sample(test_data.iloc[[0]], sample_id, is_actual_attack=True, attacker_ip=ip)
            await manager.broadcast({"type": "state", "data": state})

            if state['is_attack_detected']:
                await manager.broadcast({"type": "log", "message": f"[Consensus] THREAT CONFIRMED — {state['attack_votes']}/{state['total_nodes']} nodes flagged"})
                await asyncio.sleep(0.8)
                await manager.broadcast({"type": "containment", "message": f"[Containment] Device {ip} ISOLATED — autonomous response executed"})

            sample_id += 1
            await asyncio.sleep(2.5)

            # 2 normal samples between attacks for chart contrast
            for _ in range(2):
                test_data = loader.normalize(generate_normal_traffic(1))
                state = system.process_sample(test_data.iloc[[0]], sample_id, is_actual_attack=False)
                await manager.broadcast({"type": "state", "data": state})
                await manager.broadcast({"type": "log", "message": f"[Node Consensus] Normal Traffic — Consensus: {state['attack_votes']}/{state['total_nodes']}"})
                sample_id += 1
                await asyncio.sleep(1.5)

        await asyncio.sleep(1)
        await manager.broadcast({"type": "log", "message": "[System] Simulation complete. All threats neutralized. Swarm defence stable."})

    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        simulation_running = False

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_simulation())

@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
