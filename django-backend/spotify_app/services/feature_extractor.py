# spotify_app/feature_extractor.py
import numpy as np
import datetime
import re

DEFAULT_GENRE_VOCAB = [
    "k-pop", "korean r&b", "pop", "hip hop", "r&b",
    "rock", "indie", "edm", "jazz", "ballad"
]


def extract_features(metadata, genre_vocab=DEFAULT_GENRE_VOCAB):
    """ 기본 Mega Extractor (임베딩 없음, 100+ 특징) """

    artists = metadata.get("artists") or []
    primary_artist = artists[0] if artists else ""
    track_name = metadata.get("name", "")
    album_name = metadata.get("album_name", "")
    genres = metadata.get("genres") or []

    # --------------------------
    # 날짜 처리
    # --------------------------
    release_date = metadata.get("album_release_date", "2000-01-01")
    try:
        year = int(release_date[:4])
        month = int(release_date[5:7])
        day = int(release_date[8:10])
    except:
        year, month, day = 2000, 1, 1

    today = datetime.date.today()
    release_dt = datetime.date(year, month, day)
    age_days = (today - release_dt).days
    decade = (year // 10) * 10

    # 날짜 파생 특징
    quarter = (month - 1) // 3 + 1
    season = ["winter", "spring", "summer", "autumn"][(month % 12) // 3]
    is_weekend_release = 1 if release_dt.weekday() >= 5 else 0

    # --------------------------
    # 장르 multi-hot
    # --------------------------
    genre_vector = [1 if g in genres else 0 for g in genre_vocab]

    # --------------------------
    # 숫자 기반 특징
    # --------------------------
    track_pop = metadata.get("track_popularity") or 0
    artist_pop = metadata.get("artist_popularity") or 0
    followers = metadata.get("artist_followers") or 0
    explicit_flag = 1 if metadata.get("explicit") else 0
    duration_ms = metadata.get("duration_ms") or 0

    numeric_features = {
        # 기본 값
        "track_pop_norm": track_pop / 100.0,
        "artist_pop_norm": artist_pop / 100.0,
        "followers_log": float(np.log1p(followers)),
        "explicit": explicit_flag,
        "duration_norm": duration_ms / 300000.0,

        # 날짜 파생
        "release_year_norm": (year - 2000) / 30.0,
        "release_month": month,
        "release_day": day,
        "release_age_days": age_days,
        "release_decade": decade,
        "release_quarter": quarter,
        "release_is_weekend": is_weekend_release,

        # 장르 개수
        "genre_count": len(genres),

        # 인기도 파생
        "popularity_delta": artist_pop - track_pop,
        "followers_millions": followers / 1_000_000,

        # 길이 파생
        "duration_seconds": duration_ms / 1000,
        "duration_short_flag": 1 if duration_ms < 120000 else 0,
        "duration_long_flag": 1 if duration_ms > 300000 else 0,
    }

    # --------------------------
    # 텍스트 기반 특징
    # --------------------------
    text_features = {
        "track_name": track_name,
        "artist_names": ", ".join(artists),
        "album_name": album_name,
        "genres_text": ", ".join(genres),

        # 제목 기반
        "track_name_length": len(track_name),
        "track_name_word_count": len(track_name.split()),
        "track_name_has_digit": 1 if re.search(r"\d", track_name) else 0,
        "track_name_has_special": 1 if re.search(r"[^\w\s]", track_name) else 0,

        # 아티스트 기반
        "artist_name_length": len(primary_artist),
        "artist_word_count": len(primary_artist.split()),

        # 앨범 기반
        "album_name_length": len(album_name),
    }

    numeric_vector = list(numeric_features.values())

    return {
        "raw_metadata": metadata,
        "numeric_features": numeric_features,
        "numeric_vector": numeric_vector,
        "genre_vector": genre_vector,
        "text_features": text_features,
        "total_feature_count": len(numeric_vector) + len(genre_vector) + len(text_features),
        "version": "mega-basic"
    }
