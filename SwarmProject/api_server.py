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
        # We only want to keep alive connections
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.append(connection)
        
        for dc in dead_connections:
            self.disconnect(dc)

manager = ConnectionManager()
simulation_running = False

async def run_simulation():
    global simulation_running
    if simulation_running:
        return
    simulation_running = True
    
    loader = DatasetLoader()
    loader.load_or_fallback()
    
    await asyncio.sleep(2) # Give clients time to connect
    await manager.broadcast({"type": "log", "message": "[System] Generating baseline CPS behaviour..."})
    train_data = generate_normal_traffic(NORMAL_SAMPLES)
    loader.fit(train_data)
    train_data = loader.normalize(train_data)
    
    system = SwarmDefenceSystem()
    await manager.broadcast({"type": "log", "message": "[System] Initializing Swarm Nodes and Training Edge Models..."})
    system.initialize(train_data)
    await asyncio.sleep(2)

    sample_id = 1
    
    try:
        # Phase 1: Normal Traffic Baseline
        for _ in range(3):
            test_data = loader.normalize(generate_normal_traffic(1))
            state = system.process_sample(test_data.iloc[[0]], sample_id, is_actual_attack=False)
            await manager.broadcast({"type": "state", "data": state})
            
            if state['is_attack_detected']:
                await manager.broadcast({"type": "log", "message": f"🚨 [Node Consensus] FALSE POSITIVE Detected (Score: {state['threat_level']:.2f})"})
            else:
                await manager.broadcast({"type": "log", "message": f"✅ [Node Consensus] Normal Traffic (Consensus: {state['attack_votes']}/{state['total_nodes']})"})
            
            sample_id += 1
            await asyncio.sleep(1.5)
        
        # Phase 2: Attack Injection Series
        attack_types = ['dos', 'fdi', 'lateral_movement']
        attacker_ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        
        for attack, ip in zip(attack_types, attacker_ips):
            await manager.broadcast({"type": "log", "message": f"🚩 INTEL ALERT: Simulated {attack.upper()} attack originating from {ip}..."})
            
            # Attack spike
            test_data = loader.normalize(generate_attack_traffic(attack, 1))
            state = system.process_sample(test_data.iloc[[0]], sample_id, is_actual_attack=True, attacker_ip=ip)
            
            await manager.broadcast({"type": "state", "data": state})
            
            if state['is_attack_detected']:
                await manager.broadcast({"type": "log", "message": f"⚠️ [Consensus Reached] THREAT CONFIRMED! ({state['attack_votes']}/{state['total_nodes']} nodes)"})
                await asyncio.sleep(0.5)
                await manager.broadcast({"type": "containment", "message": f"🔒 CONTAINMENT: Device {ip} ISOLATED autonomously."})
            
            sample_id += 1
            await asyncio.sleep(3.0)
            
        await manager.broadcast({"type": "log", "message": "🏁 SIMULATION COMPLETE. All systems secure. No further traffic expected."})
        
    except Exception as e:
        print(f"Simulation interrupted: {e}")
        simulation_running = False

@app.on_event("startup")
async def startup_event():
    # Start the simulation task in the background when the server starts
    asyncio.create_task(run_simulation())

@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection open, we don't expect client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
