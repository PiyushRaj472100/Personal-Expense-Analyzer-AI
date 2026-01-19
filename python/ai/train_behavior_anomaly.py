import os
import pickle
import pandas as pd
from sklearn.ensemble import IsolationForest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "expense_nlp_master_2500_v2.csv")
MODEL_PATH = os.path.join(BASE_DIR, "behavior_anomaly_model.pkl")

print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

# Features for anomaly detection
features = df[["amount"]].copy()

print("Training anomaly detector...")
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(features)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("✅ behavior_anomaly_model.pkl saved")
