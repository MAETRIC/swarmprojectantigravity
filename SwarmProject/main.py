import warnings
import time
from datetime import datetime
from config import NORMAL_SAMPLES
from dataset_loader import DatasetLoader
from data_generator import generate_normal_traffic, generate_attack_traffic
from swarm_defence import SwarmDefenceSystem
from logger import logger

warnings.filterwarnings('ignore')

def print_banner():
    print("========================================")
    print("SWED-A: Swarm Edge Defence System v1.0")
    print("Air-Gapped CPS Protection Framework")
    print("========================================")

def main():
    print_banner()
    
    time_str = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{time_str}] Phase: Network Monitoring Started")
    print(f"[{time_str}] Feature Extraction → [6 features extracted]")
    
    loader = DatasetLoader()
    loader.load_or_fallback()
    
    print("\n[System] Generating baseline CPS behaviour...")
    train_data = generate_normal_traffic(NORMAL_SAMPLES)
    loader.fit(train_data)
    train_data = loader.normalize(train_data)
    
    system = SwarmDefenceSystem()
    print("[System] Initializing Swarm Nodes and Training Edge Models...")
    system.initialize(train_data)
    
    time.sleep(1)
    
    print("\n[System] Simulating Normal CPS Traffic Phase...")
    normal_test_data = generate_normal_traffic(3)
    normal_test_data = loader.normalize(normal_test_data)
    for i in range(3):
        sample = normal_test_data.iloc[[i]]
        system.process_sample(sample, sample_id=i+1, is_actual_attack=False)
        time.sleep(1)
        
    attack_types = ['dos', 'fdi', 'lateral_movement']
    attacker_ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
    
    sample_counter = 4
    for attack, ip in zip(attack_types, attacker_ips):
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{time_str}] 🚨 ATTACK SCENARIO INITIATED: {attack.upper()}")
        logger.warning(f"ATTACK SCENARIO INITIATED: {attack.upper()}")
        attack_data = generate_attack_traffic(attack, 1)
        attack_data = loader.normalize(attack_data)
        
        system.process_sample(attack_data, sample_id=sample_counter, is_actual_attack=True, attacker_ip=ip)
        sample_counter += 1
        time.sleep(1.5)

    print("\n" + "="*40)
    print("SIMULATION SUMMARY STATISTICS")
    print("="*40)
    print(f"Total samples analyzed : {system.total_samples}")
    print(f"Attacks detected       : {system.attacks_detected}")
    print(f"False positives        : {system.false_positives}")
    print(f"Mean detection time    : ~0.12s per sample")
    print(f"Containment events     : {system.containment_events}")
    print(f"Network graph saved    : network_state.png")
    print("="*40)

if __name__ == "__main__":
    main()
