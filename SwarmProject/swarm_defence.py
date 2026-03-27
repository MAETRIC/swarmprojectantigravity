from config import NUM_NODES
from edge_node import EdgeNode
from consensus_engine import ConsensusEngine
from containment_manager import ContainmentManager
from feature_extractor import FeatureExtractor
from network_graph import NetworkGraph
import numpy as np

class SwarmDefenceSystem:
    def __init__(self):
        self.nodes = [EdgeNode(i+1) for i in range(NUM_NODES)]
        self.consensus = ConsensusEngine(NUM_NODES)
        self.containment = ContainmentManager()
        self.feature_extractor = FeatureExtractor()
        self.graph = NetworkGraph(NUM_NODES)
        
        self.total_samples = 0
        self.attacks_detected = 0
        self.false_positives = 0
        self.containment_events = 0
        
    def initialize(self, normal_training_data):
        features_df = self.feature_extractor.extract(normal_training_data)
        
        for node in self.nodes:
            noise = np.random.normal(0, 0.01, features_df.shape)
            node.train(features_df + noise)
            
        self.graph.update_graph(is_attack=False)
            
    def process_sample(self, sample_df, sample_id, is_actual_attack=False, attacker_ip=None):
        self.total_samples += 1
        features = self.feature_extractor.extract(sample_df).iloc[0].values
        
        node_results = {}
        for node in self.nodes:
            pred, score, conf = node.detect(features)
            status = "ATTACK" if (pred == -1 or score < -0.05) else "NORMAL"
            node_results[node.node_id] = {
                'prediction': pred,
                'score': score,
                'confidence': conf,
                'status': status
            }
            
        print(f"\n🔍 Swarm Detection Phase — Sample #{sample_id}")
        print("─────────────────────────────────────")
        for node_id, res in node_results.items():
            status = res['status']
            print(f"{node_id}  │ Score: {res['score']:+.3f} │ Status: {status:<8} │ Confidence: {res['confidence']:.1f}%")
        print("─────────────────────────────────────")
        
        is_attack_detected, attack_votes, total = self.consensus.run_consensus(node_results)
        
        avg_score = np.mean([res['score'] for res in node_results.values()])
        threat_level = max(0, -avg_score) if is_attack_detected else 0
        
        if is_attack_detected:
            print(f"⚠️  Consensus: ATTACK CONFIRMED ({attack_votes}/{total} nodes detect threat)")
            self.attacks_detected += 1
            if not is_actual_attack:
                self.false_positives += 1
                
            isolated = self.containment.isolate_device('10.0.1.5')
            if isolated:
                self.containment_events += 1
                print(f"🚨 Autonomous Response Triggered")
                print(f"🔒 Containment: Device '10.0.1.5' ISOLATED from network")
                print(f"📋 Incident logged: {self.containment.log_file_ref()}")
            print(f"🎯 Final Decision: THREAT NEUTRALIZED")
        else:
            print(f"✅ Consensus: NORMAL TRAFFIC ({total-attack_votes}/{total} nodes agree)")
            print(f"🎯 Final Decision: NO THREAT DETECTED")
            
        self.graph.update_graph(is_attack=is_attack_detected, attacker_ip=attacker_ip, threat_level=threat_level)
        
        # Return state for API
        return {
            'sample_id': sample_id,
            'is_actual_attack': is_actual_attack,
            'attacker_ip': attacker_ip,
            'is_attack_detected': is_attack_detected,
            'attack_votes': attack_votes,
            'total_nodes': total,
            'threat_level': float(threat_level),
            'node_results': {k: {'prediction': int(v['prediction']), 'score': float(v['score']), 'confidence': float(v['confidence']), 'status': v['status']} for k,v in node_results.items()},
            'stats': {
                'total_samples': self.total_samples,
                'attacks_detected': self.attacks_detected,
                'false_positives': self.false_positives,
                'containment_events': self.containment_events
            }
        }
