from sklearn.ensemble import IsolationForest
from config import CONTAMINATION_RATE

class EdgeNode:
    def __init__(self, node_id):
        self.node_id = f"Node{node_id}"
        # Isolation Forest is lightweight and suitable for edge-device constraints
        self.model = IsolationForest(contamination=CONTAMINATION_RATE, random_state=42 + node_id)
        self.is_trained = False
        
    def train(self, normal_data):
        self.model.fit(normal_data)
        self.is_trained = True
        
    def detect(self, sample):
        if not self.is_trained:
            raise Exception(f"{self.node_id} is not trained yet!")
            
        if len(sample.shape) == 1:
            sample = sample.reshape(1, -1)
            
        prediction = self.model.predict(sample)[0]
        score = self.model.decision_function(sample)[0]
        
        # Calculate a pseudo-confidence percentage mapping from score
        confidence = min(max(abs(score) * 200 + 50, 50.0), 99.9)
        
        return prediction, score, confidence
