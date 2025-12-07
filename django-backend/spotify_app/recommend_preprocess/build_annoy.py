import os
import json
import numpy as np
from annoy import AnnoyIndex
import shutil


# -----------------------------------------------------
# Annoy 저장 경로 (ASCII-only, 안전 폴더)
# -----------------------------------------------------
ANNOY_DIR = "D:/dnnoy"
os.makedirs(ANNOY_DIR, exist_ok=True)

ANNOY_PATH = os.path.join(ANNOY_DIR, "spotify_annoy.ann")
TRACK_IDS_OUTPUT = os.path.join(ANNOY_DIR, "kaggle_track_ids.json")

# -----------------------------------------------------
# 입력 벡터: spotify_app/data/output/kaggle_vectors.npy
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "output"))

VECTORS_PATH = os.path.join(DATA_DIR, "kaggle_vectors.npy")
TRACK_IDS_PATH = os.path.join(DATA_DIR, "kaggle_track_ids.json")

print(f"\n📥 Loading vectors from:\n{VECTORS_PATH}")

vectors = np.load(VECTORS_PATH)
VECTOR_DIM = vectors.shape[1]

print(f"✔ Loaded {vectors.shape[0]} vectors.")
print(f"✔ Vector Dimension: {VECTOR_DIM} (expected: 31)\n")


# -----------------------------------------------------
# Annoy Index 생성
# -----------------------------------------------------
print("🎛 Building Annoy index... (trees=50)")

ann = AnnoyIndex(VECTOR_DIM, "euclidean")

for idx, vec in enumerate(vectors):
    ann.add_item(idx, vec)

ann.build(50)  # 50 trees (추천값)

print("\n💾 Saving Annoy index...")
ann.save(ANNOY_PATH)
print(f"✔ Saved to: {ANNOY_PATH}")


# -----------------------------------------------------
# track_ids.json 복사
# -----------------------------------------------------
print("\n📁 Copying track_ids.json...")
shutil.copy(TRACK_IDS_PATH, TRACK_IDS_OUTPUT)
print(f"✔ Saved: {TRACK_IDS_OUTPUT}")


print("\n✅ Annoy index (31D) created successfully!\n")

'''
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
'''