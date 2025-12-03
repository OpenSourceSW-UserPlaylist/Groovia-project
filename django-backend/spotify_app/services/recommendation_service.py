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
    recommended_ids = rec.recommend_top_k(vectors, k=50)   # 50개 받아옴

    # 👉 최종적으로 메타데이터는 10개만 조회
    top10_ids = recommended_ids[:10]

    recommended_details = []

    for tid in top10_ids:
        meta = get_track_metadata(tid, token)   # ★ 호출 10번만!
        if not meta:
            continue

        # artist 리스트 정리
        artists = meta.get("artists", [])
        if isinstance(artists, list):
            artist_name = ", ".join(str(a) for a in artists)
        else:
            artist_name = str(artists)

        recommended_details.append({
            "id": tid,
            "title": meta.get("name", "Unknown Title"),
            "artist": artist_name
        })

    # 중복 제거 (title + artist)
    unique = []
    seen = set()

    for item in recommended_details:
        key = (item["title"].lower(), item["artist"].lower())
        if key not in seen:
            unique.append(item)
            seen.add(key)

    # 최종 반환
    return metadata_list, features_list, unique[:10]

