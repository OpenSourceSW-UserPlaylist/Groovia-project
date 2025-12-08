import os
import pandas as pd
import numpy as np
import json
import re
from tqdm import tqdm


# ---------------------------------
# 0) 기본 설정
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
CSV_PATH = os.path.join(DATA_DIR, "kaggle_spotify.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------
# 1) 장르 vocab 통일 (10D)
# ---------------------------------
GENRE_VOCAB = [
    "k-pop", "korean r&b", "pop", "hip hop", "r&b",
    "rock", "indie", "edm", "jazz", "ballad"
]

def genre_to_vec(genre):
    genre = str(genre).lower()
    return [1 if g in genre else 0 for g in GENRE_VOCAB]


# ---------------------------------
# 2) Kaggle CSV 로드
# ---------------------------------
print(f"\nLoading Kaggle Dataset from:\n{CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} tracks.\n")


vectors = []
track_ids = {}

print("Generating 31-dimensional unified feature vectors...\n")


# ---------------------------------
# 3) Feature Extractor (Kaggle 버전)
# ---------------------------------
for idx, row in tqdm(df.iterrows(), total=len(df)):

    # ---------- 기본 metadata ----------
    track_name = str(row.get("track_name", "")) if "track_name" in df else ""
    if track_name == "" and "track_name" in df:
        track_name = str(row.get("track_name", ""))

    artist_name = str(row.get("artists", "")) if "artists" in df else str(row.get("artist_name", ""))
    album_name = str(row.get("album_name", "")) if "album_name" in df else ""

    duration_ms = row.get("duration_ms", 0)
    explicit = int(row.get("explicit", 0))
    popularity = int(row.get("popularity", 0))
    genre_text = str(row.get("track_genre", ""))

    # ---------- numeric features ----------
    duration_seconds = duration_ms / 1000
    duration_norm = duration_ms / 300000.0

    track_pop_norm = popularity / 100.0

    # Kaggle에는 release_date 없음 → 2000년 기준으로 통일
    release_year_norm = 0
    release_month = 0
    release_day = 0
    release_quarter = 0
    release_decade = 0
    release_age_days = 0

    # Kaggle에는 artist_popularity / followers 없음
    artist_pop = 0
    artist_followers = 0
    popularity_delta = 0
    followers_log = 0

    duration_short_flag = 1 if duration_ms < 120000 else 0
    duration_long_flag = 1 if duration_ms > 300000 else 0

    numeric_vector = [
        duration_seconds,
        duration_norm,
        explicit,
        track_pop_norm,
        release_year_norm,
        release_month,
        release_day,
        release_quarter,
        release_decade,
        release_age_days,
        popularity_delta,
        followers_log,
        duration_short_flag,
        duration_long_flag,
    ]


    # ---------- genre multi-hot ----------
    genre_vector = genre_to_vec(genre_text)   # 10D


    # ---------- text pattern ----------
    track_name_length = len(track_name) / 50
    track_name_word_count = len(track_name.split()) / 10
    has_digit = 1 if re.search(r"\d", track_name) else 0
    has_special = 1 if re.search(r"[^\w\s]", track_name) else 0

    artist_name_length = len(artist_name) / 30
    artist_word_count = len(artist_name.split()) / 10

    album_name_length = len(album_name) / 50

    text_vector = [
        track_name_length,
        track_name_word_count,
        has_digit,
        has_special,
        artist_name_length,
        artist_word_count,
        album_name_length,
    ]

    # ---------- 최종 벡터 ----------
    full_vector = numeric_vector + genre_vector + text_vector  # 총 31차원

    vectors.append(full_vector)
    track_ids[idx] = row["track_id"]


# ---------------------------------
# 4) 저장
# ---------------------------------
vectors = np.array(vectors)

np.save(os.path.join(OUTPUT_DIR, "kaggle_vectors.npy"), vectors)

with open(os.path.join(OUTPUT_DIR, "kaggle_track_ids.json"), "w", encoding="utf-8") as f:
    json.dump(track_ids, f, ensure_ascii=False, indent=2)

print(f"\nSaved {vectors.shape[0]} vectors ({vectors.shape[1]}-dim) successfully!\n")


