from config import CONSENSUS_THRESHOLD, ANOMALY_SCORE_THRESHOLD

class ConsensusEngine:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        
    def run_consensus(self, node_results):
        attack_votes = 0
        total_nodes = len(node_results)
        
        for node_id, result in node_results.items():
            if result['prediction'] == -1 or result['score'] < ANOMALY_SCORE_THRESHOLD:
                attack_votes += 1
                
        is_attack = (attack_votes / total_nodes) > CONSENSUS_THRESHOLD
        return is_attack, attack_votes, total_nodes
