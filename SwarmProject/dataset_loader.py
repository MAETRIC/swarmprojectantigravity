import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from config import FEATURES

class DatasetLoader:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def load_or_fallback(self, file_path="dataset/UNSW_NB15.csv"):
        if os.path.exists(file_path):
            print(f"Loading real dataset from {file_path}...")
            try:
                df = pd.read_csv(file_path)
                return df
            except Exception as e:
                print(f"Failed to load dataset: {e}. Falling back to synthetic.")
        
        print("Using synthetic data source (CPS Simulation).")
        return None
        
    def fit(self, df):
        if df is not None and len(df) > 0:
            self.scaler.fit(df[FEATURES])
            self.is_fitted = True
            
    def normalize(self, df):
        if df is None or len(df) == 0:
            return df
            
        if not self.is_fitted:
            self.fit(df)
            
        scaled_features = self.scaler.transform(df[FEATURES])
        df_normalized = df.copy()
        df_normalized[FEATURES] = scaled_features
        return df_normalized
