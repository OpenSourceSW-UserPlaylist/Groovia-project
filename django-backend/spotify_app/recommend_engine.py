# spotify_app/recommend_engine.py

import numpy as np
import json
import os
from annoy import AnnoyIndex
from django.conf import settings

VECTOR_DIM = int(getattr(settings, "SPOTIFY_VECTOR_DIM", 31))

ANNOY_PATH = os.path.join(settings.ANNOY_DIR, "spotify_annoy.ann")
TRACK_IDS_PATH = os.path.join(settings.ANNOY_DIR, "kaggle_track_ids.json")

class AnnoyRecommender:
    def __init__(self):

        # kaggle_vectors.npy 의 벡터 차원 자동 추출
        with open(TRACK_IDS_PATH, "r", encoding="utf-8") as f:
            self.track_ids = json.load(f)

        # Annoy index 파일을 직접 읽어 dimension 자동 결정
        self.ann = AnnoyIndex(VECTOR_DIM, "euclidean")
        self.ann.load(ANNOY_PATH)
        self.vector_dim = VECTOR_DIM
        

        # Annoy 객체 재생성
        self.ann = AnnoyIndex(VECTOR_DIM, "euclidean")
        self.ann.load(ANNOY_PATH)

        print(f"Annoy Index Loaded (Dimension: {VECTOR_DIM})")
        self.vector_dim = VECTOR_DIM

        print("Annoy index path =", ANNOY_PATH)
        print("recommend_engine.py loaded from:", os.path.abspath(__file__))

    # ----------------------------
    # 노래 추천 로직
    # ----------------------------
    def recommend_top_k(self, user_vectors, k=10, per_track_k=20):

        # 입력 벡터 차원이 일치하는지 검증
        for v in user_vectors:
            if len(v) != self.vector_dim:
                raise ValueError(
                    f"벡터 차원 불일치: expected={self.vector_dim}, got={len(v)}"
                )

        # 후보 수집
        candidate_scores = {}  # 최소 거리
        candidate_counts = {}  # 등장 횟수

        for vec in user_vectors:
            idxs, distances = self.ann.get_nns_by_vector(
                vec, per_track_k, include_distances=True
            )

            for idx, dist in zip(idxs, distances):
                key = str(idx)
                if key not in self.track_ids:
                    continue

                track_id = self.track_ids[key]

                # 등장 횟수
                candidate_counts[track_id] = candidate_counts.get(track_id, 0) + 1

                # 최소 거리
                if track_id not in candidate_scores:
                    candidate_scores[track_id] = dist
                else:
                    candidate_scores[track_id] = min(candidate_scores[track_id], dist)

        if not candidate_scores:
            print("No recommendation candidates found.")
            return []

        # 후보 정렬 
        sorted_tracks = sorted(
            candidate_scores.keys(),
            key=lambda tid: candidate_scores[tid]
        )

        return sorted_tracks[:k]


    

