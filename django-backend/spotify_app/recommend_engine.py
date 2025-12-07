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
        # 파일을 로딩한 후 ann.get_item_vector(0)의 길이로 dim 추론 가능
        self.ann = AnnoyIndex(VECTOR_DIM, "euclidean")
        self.ann.load(ANNOY_PATH)
        self.vector_dim = VECTOR_DIM
        '''
        try:
            sample_vec = temp_ann.get_item_vector(0)
            VECTOR_DIM = len(sample_vec)
        except Exception:
            raise RuntimeError("❌ Annoy index를 로딩할 수 없습니다. index를 먼저 build해주세요.")
        '''

        # 실제 Annoy 객체 재생성
        self.ann = AnnoyIndex(VECTOR_DIM, "euclidean")
        self.ann.load(ANNOY_PATH)

        print(f"🔧 Annoy Index Loaded (Dimension: {VECTOR_DIM})")
        self.vector_dim = VECTOR_DIM

        print("📁 Annoy index path =", ANNOY_PATH)
        print("📌 recommend_engine.py loaded from:", os.path.abspath(__file__))


    def recommend_top_k(self, user_vectors, k=10, per_track_k=20):
        """
        입력: user_vectors → run_recommendation 에서 가중치 적용된 최종 벡터 리스트
        출력: 가장 유사한 track_id 리스트
        """

        # 입력 벡터 차원이 일치하는지 검증
        for v in user_vectors:
            if len(v) != self.vector_dim:
                raise ValueError(
                    f"❌ 벡터 차원 불일치: expected={self.vector_dim}, got={len(v)}"
                )

        # ----------------------------
        # 후보 수집
        # ----------------------------
        candidate_scores = {}  # track_id → 최소 거리
        candidate_counts = {}  # track_id → 등장 횟수

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

                # 거리 (min)
                if track_id not in candidate_scores:
                    candidate_scores[track_id] = dist
                else:
                    candidate_scores[track_id] = min(candidate_scores[track_id], dist)

        if not candidate_scores:
            print("⚠ No recommendation candidates found.")
            return []

        # ----------------------------
        # 후보 정렬 (등장횟수 → 거리)
        # ----------------------------
        sorted_tracks = sorted(
            candidate_scores.keys(),
            key=lambda tid: candidate_scores[tid]
        )

        return sorted_tracks[:k]

'''
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


    def recommend_top_k(self, user_vectors, k=10, per_track_k=20):

        # ==============================
        # 1) 입력곡 벡터 개별 추천 수집
        # ==============================
        candidate_scores = {}   # track_id → 최소거리(=유사도 점수)
        candidate_counts = {}   # track_id → 등장 횟수

        for vec in user_vectors:
            idxs, distances = self.ann.get_nns_by_vector(vec, per_track_k, include_distances=True)

            for idx, dist in zip(idxs, distances):
                key = str(idx)
                if key not in self.track_ids:
                    continue

                track_id = self.track_ids[key]

                # count 증가
                candidate_counts[track_id] = candidate_counts.get(track_id, 0) + 1

                # score(거리) 업데이트 (더 낮은 거리=더 유사)
                if track_id not in candidate_scores:
                    candidate_scores[track_id] = dist
                else:
                    candidate_scores[track_id] = min(candidate_scores[track_id], dist)

        # ==============================
        # 2) 후보를 점수/빈도 기반 정렬
        # ==============================
        # 정렬 기준:
        #   1) candidate_counts: 많이 등장한 곡 우선
        #   2) candidate_scores: 거리 낮은 곡 우선
        sorted_tracks = sorted(
            candidate_counts.keys(),
            key=lambda tid: (-candidate_counts[tid], candidate_scores[tid])
        )

        # ==============================
        # 3) 상위 k개 반환
        # ==============================
        return sorted_tracks[:k]
'''

    

