import numpy as np
import pandas as pd
from config import FEATURES

def generate_normal_traffic(n_samples):
    """Simulate realistic normal CPS traffic combinations"""
    packet_rate = np.random.normal(10, 2, n_samples)
    avg_packet_size = np.random.normal(256, 20, n_samples)
    unique_dst_ports = np.random.randint(1, 4, n_samples)
    connection_frequency = np.random.normal(5, 1, n_samples)
    protocol_ratio = np.random.normal(0.8, 0.05, n_samples)
    burst_score = np.random.normal(0.1, 0.02, n_samples)
    
    data = np.column_stack((packet_rate, avg_packet_size, unique_dst_ports, 
                            connection_frequency, protocol_ratio, burst_score))
    df = pd.DataFrame(data, columns=FEATURES)
    df = df.clip(lower=0)
    return df

def generate_attack_traffic(attack_type, n_samples):
    """Simulate different types of attack scenarios"""
    if attack_type == "dos":
        packet_rate = np.random.normal(500, 50, n_samples)
        avg_packet_size = np.random.normal(1500, 100, n_samples)
        unique_dst_ports = np.random.randint(1, 3, n_samples)
        connection_frequency = np.random.normal(200, 20, n_samples)
        protocol_ratio = np.random.normal(0.9, 0.05, n_samples)
        burst_score = np.random.normal(0.9, 0.05, n_samples)
    elif attack_type == "fdi":
        packet_rate = np.random.normal(12, 3, n_samples)
        avg_packet_size = np.random.normal(300, 30, n_samples)
        unique_dst_ports = np.random.randint(2, 5, n_samples)
        connection_frequency = np.random.normal(6, 1.5, n_samples)
        protocol_ratio = np.random.normal(0.6, 0.1, n_samples)
        burst_score = np.random.normal(0.2, 0.05, n_samples)
    elif attack_type == "lateral_movement":
        packet_rate = np.random.normal(30, 5, n_samples)
        avg_packet_size = np.random.normal(100, 10, n_samples)
        unique_dst_ports = np.random.randint(20, 100, n_samples)
        connection_frequency = np.random.normal(50, 10, n_samples)
        protocol_ratio = np.random.normal(0.4, 0.1, n_samples)
        burst_score = np.random.normal(0.3, 0.05, n_samples)
    else:
        raise ValueError("Unknown attack type")
        
    data = np.column_stack((packet_rate, avg_packet_size, unique_dst_ports, 
                            connection_frequency, protocol_ratio, burst_score))
    df = pd.DataFrame(data, columns=FEATURES)
    df = df.clip(lower=0)
    return df
