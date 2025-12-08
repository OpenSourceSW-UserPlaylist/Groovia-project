import os
import json
import numpy as np
from annoy import AnnoyIndex
import shutil


# --------------------------------------------------------------
# Annoy 저장 경로 (안전 폴더: 깊은 경로에 저장할 경우 발생하는 오류 대응)
# --------------------------------------------------------------
ANNOY_DIR = "D:/dnnoy"
os.makedirs(ANNOY_DIR, exist_ok=True)

ANNOY_PATH = os.path.join(ANNOY_DIR, "spotify_annoy.ann")
TRACK_IDS_OUTPUT = os.path.join(ANNOY_DIR, "kaggle_track_ids.json")

# -----------------------------------------------------
# 입력 벡터: kaggle_vectors.npy
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "output"))

VECTORS_PATH = os.path.join(DATA_DIR, "kaggle_vectors.npy")
TRACK_IDS_PATH = os.path.join(DATA_DIR, "kaggle_track_ids.json")

print(f"\nLoading vectors from:\n{VECTORS_PATH}")

vectors = np.load(VECTORS_PATH)
VECTOR_DIM = vectors.shape[1]

print(f"Loaded {vectors.shape[0]} vectors.")
print(f"Vector Dimension: {VECTOR_DIM} (expected: 31)\n")


# -----------------------------------------------------
# Annoy Index 생성
# -----------------------------------------------------
print("Building Annoy index... (trees=50)")

ann = AnnoyIndex(VECTOR_DIM, "euclidean")

for idx, vec in enumerate(vectors):
    ann.add_item(idx, vec)

ann.build(50)  # 50 trees (추천값)

print("\nSaving Annoy index...")
ann.save(ANNOY_PATH)
print(f"Saved to: {ANNOY_PATH}")


# -----------------------------------------------------
# track_ids.json 복사
# -----------------------------------------------------
print("\nCopying track_ids.json...")
shutil.copy(TRACK_IDS_PATH, TRACK_IDS_OUTPUT)
print(f"Saved: {TRACK_IDS_OUTPUT}")


print("\nAnnoy index (31D) created successfully!\n")

