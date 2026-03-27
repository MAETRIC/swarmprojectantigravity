from config import FEATURES

class FeatureExtractor:
    def __init__(self):
        self.features = FEATURES
        
    def extract(self, raw_data_df):
        """
        Extract pre-configured features needed by the local Anomaly Detection Models
        """
        return raw_data_df[self.features]
