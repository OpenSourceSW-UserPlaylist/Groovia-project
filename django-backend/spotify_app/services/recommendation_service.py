from django.conf import settings
from spotify_app.services.spotify_client import get_client_credentials_token, get_track_metadata
from spotify_app.services.feature_extractor import extract_features
from spotify_app.recommend_engine import AnnoyRecommender
from annoy import AnnoyIndex


# ============================================================
# 추천 핵심 로직 
# ============================================================
def run_recommendation(track_ids):

    # 0) 서버 Client Credentials 토큰 발급
    token = get_client_credentials_token()

    # 1) 입력곡 메타데이터 조회 → 벡터 추출
    metadata_list = [get_track_metadata(tid, token) for tid in track_ids]
    
    features_list = []
    for meta in metadata_list:
        features_list.append(extract_features(meta)) # 벡터 추출

    # 2) 가중치 적용한 벡터 만들기
    NUMERIC_WEIGHT = getattr(settings, "SPOTIFY_NUMERIC_WEIGHT", 1.0)
    GENRE_WEIGHT = getattr(settings, "SPOTIFY_GENRE_WEIGHT", 1.0)
    TEXT_WEIGHT = getattr(settings, "SPOTIFY_TEXT_WEIGHT", 0.4)

    vectors = []
    for f in features_list:
        numeric = [x * NUMERIC_WEIGHT for x in f["numeric_features"].values()]  # 14D
        genre   = [g * GENRE_WEIGHT for g in f["genre_vector"]]  # 10D
        text = [t * TEXT_WEIGHT for t in f["text_features"].values()]  # 7D  

        full_vector = numeric + genre + text
        vectors.append(full_vector)

    # 3) Annoy 추천 50개 받아오기
    rec = AnnoyRecommender()
    recommended_ids = rec.recommend_top_k(vectors, k=50)


    # 4) 50개 전체 메타데이터 조회 
    raw_details = []

    for tid in recommended_ids:
        meta = get_track_metadata(tid, token)
        if not meta:
            continue

        # 아티스트 정리
        artists = meta.get("artists", []) or []
        if isinstance(artists, list) and len(artists) > 0:
            artist_name = str(artists[0])   # 첫 번째 아티스트만
        else:
            artist_name = "Unknown"

        raw_details.append({
            "track_id": tid,
            "title": meta.get("name", "Unknown Title"),
            "artist": artist_name,
            "album_image": meta.get("album_image_url", ""),
            "spotify_url": meta.get("spotify_url", "")
        })


    # 5) 중복 제거 (title + artist 기준)
    unique = []
    seen = set()

    for item in raw_details:
        key = (item["title"].lower(), item["artist"].lower())
        if key not in seen:
            unique.append(item)
            seen.add(key)


    # 6) 상위 10곡만 반환
    final_playlist = unique[:10]

    return metadata_list, [], final_playlist


