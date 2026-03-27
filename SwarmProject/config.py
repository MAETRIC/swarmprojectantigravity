import os

NUM_NODES = 3
CONTAMINATION_RATE = 0.05
CONSENSUS_THRESHOLD = 0.5
ANOMALY_SCORE_THRESHOLD = -0.05
NORMAL_SAMPLES = 200
ATTACK_SAMPLES = 50
FEATURES = [
    "packet_rate", "avg_packet_size", "unique_dst_ports", 
    "connection_frequency", "protocol_ratio", "burst_score"
]
LOG_FILE = "swarm_defence.log"
GRAPH_OUTPUT = "network_state.png"
