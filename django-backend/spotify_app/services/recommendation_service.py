import time
from django.conf import settings
from spotify_app.services.spotify_client import get_client_credentials_token, get_track_metadata
from spotify_app.services.feature_extractor import extract_features
from spotify_app.recommend_engine import AnnoyRecommender


# ============================================================
# 추천 핵심 로직 (두 모드가 공유하는 기능)
# ============================================================
def run_recommendation(track_ids):
    token = get_client_credentials_token()

    # 1) metadata
    metadata_list = [get_track_metadata(tid, token) for tid in track_ids]

    # 2) features
    features_list = []
    for meta in metadata_list:
        time.sleep(0.3)
        features_list.append(extract_features(meta))

    # 3) weighted vector
    NUMERIC_WEIGHT = getattr(settings, "SPOTIFY_NUMERIC_WEIGHT", 1.0)
    GENRE_WEIGHT = getattr(settings, "SPOTIFY_GENRE_WEIGHT", 1.0)

    vectors = []
    for f in features_list:
        num = [x * NUMERIC_WEIGHT for x in f["numeric_vector"]]
        gen = [g * GENRE_WEIGHT for g in f["genre_vector"]]
        vectors.append(num + gen)

    # 4) Annoy
    rec = AnnoyRecommender()
    recommended = rec.recommend_top_k(vectors, k=10)

    return metadata_list, features_list, recommended
