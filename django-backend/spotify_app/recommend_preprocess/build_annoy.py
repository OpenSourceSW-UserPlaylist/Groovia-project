import os
import json
import numpy as np
from annoy import AnnoyIndex

# -----------------------------------------------------
# 🚨 Annoy 전용 안전 경로 (ASCII-only, 최상위 폴더)
# -----------------------------------------------------
ANNOY_DIR = "D:/annoy"
os.makedirs(ANNOY_DIR, exist_ok=True)

ANNOY_PATH = os.path.join(ANNOY_DIR, "spotify_annoy.ann")
TRACK_IDS_OUTPUT = os.path.join(ANNOY_DIR, "kaggle_track_ids.json")

# -----------------------------------------------------
# 입력 데이터는 spotify_app/data/output 안에서 가져옴
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "output"))

VECTORS_PATH = os.path.join(DATA_DIR, "kaggle_vectors.npy")
TRACK_IDS_PATH = os.path.join(DATA_DIR, "kaggle_track_ids.json")

print(f"\n📥 Loading vectors from:\n{VECTORS_PATH}")

vectors = np.load(VECTORS_PATH)
VECTOR_DIM = vectors.shape[1]

print(f"✔ Loaded {vectors.shape[0]} vectors ({VECTOR_DIM}-dim)")

u = AnnoyIndex(VECTOR_DIM, 'euclidean')

print("\n🎛 Building Annoy index...")
for i in range(len(vectors)):
    u.add_item(i, vectors[i])

u.build(50)

print(f"\n💾 Saving Annoy index to: {ANNOY_PATH}")
u.save(ANNOY_PATH)

# track_ids.json도 D:/annoy 안에 복사
import shutil
shutil.copy(TRACK_IDS_PATH, TRACK_IDS_OUTPUT)

print(f"💾 Saved track_id mapping to: {TRACK_IDS_OUTPUT}")

print("\n✅ Annoy index created successfully!")
