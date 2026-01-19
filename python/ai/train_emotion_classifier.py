import os
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "expense_nlp_master_2500_v2.csv")
MODEL_PATH = os.path.join(BASE_DIR, "emotion_classifier.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "emotion_label_encoder.pkl")

TEXT_COL = "text_clean"
EMOTION_COL = "emotion"   # must exist in CSV

print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

print("Encoding emotion labels...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df[EMOTION_COL])

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Encoding texts...")
X = model.encode(df[TEXT_COL].astype(str).tolist())

print("Training emotion classifier...")
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)

with open(ENCODER_PATH, "wb") as f:
    pickle.dump(label_encoder, f)

print("✅ emotion_classifier.pkl saved")
print("✅ emotion_label_encoder.pkl saved")
print("Emotions:", list(label_encoder.classes_))
