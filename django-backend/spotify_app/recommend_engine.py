# spotify_app/recommend_engine.py

import numpy as np
import json
import os
from annoy import AnnoyIndex

VECTOR_DIM = 28  # prepare_kaggle_dataset.py 에서 만든 vector 차원 그대로

ANNOY_DIR = "D:/annoy"

ANNOY_PATH = os.path.join(ANNOY_DIR, "spotify_annoy.ann")
TRACK_IDS_PATH = os.path.join(ANNOY_DIR, "kaggle_track_ids.json")

class AnnoyRecommender:
    def __init__(self):
        self.ann = AnnoyIndex(VECTOR_DIM, "euclidean")
        self.ann.load(ANNOY_PATH)

        with open(TRACK_IDS_PATH, "r", encoding="utf-8") as f:
            self.track_ids = json.load(f)

    def recommend_top_k(self, user_vectors, k=10):

        vectors = np.array(user_vectors)
        mean_vector = np.mean(vectors, axis=0)

        idxs = self.ann.get_nns_by_vector(mean_vector, k)

        result = []
        for i in idxs:
            key = str(i)
            if key in self.track_ids:
                result.append(self.track_ids[key])
            elif i in self.track_ids:
                result.append(self.track_ids[i])

        return result
