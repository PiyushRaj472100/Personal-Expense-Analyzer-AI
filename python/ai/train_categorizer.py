import os
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from collections import defaultdict
import numpy as np

# ---------------- PATH SAFE CONFIG ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "expense_nlp_master_2500_v2.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "category_centroids.pkl")

TEXT_COL = "text_clean"
CATEGORY_COL = "category"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------- LOAD DATA ---------------- #

print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

# ---------------- LOAD MODEL ---------------- #

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# ---------------- ENCODE & BUILD CENTROIDS ---------------- #

category_embeddings = defaultdict(list)

print("Encoding texts...")
for _, row in df.iterrows():
    text = str(row[TEXT_COL])
    category = row[CATEGORY_COL]
    emb = model.encode(text)
    category_embeddings[category].append(emb)

print("Computing centroids...")
category_centroids = {
    cat: np.mean(vectors, axis=0)
    for cat, vectors in category_embeddings.items()
}

# ---------------- SAVE ---------------- #

with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(category_centroids, f)

print("✅ category_centroids.pkl saved successfully")
print(f"Categories trained: {list(category_centroids.keys())}")
