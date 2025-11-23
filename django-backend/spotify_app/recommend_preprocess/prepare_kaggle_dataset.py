import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # recommend_preprocess
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
CSV_PATH = os.path.join(DATA_DIR, "kaggle_spotify.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\n📥 Loading Kaggle Dataset from:\n{CSV_PATH}")

df = pd.read_csv(CSV_PATH)
print(f"✔ Loaded {len(df)} tracks.\n")


# -----------------------------
# GENRE VOCAB (10개)
# -----------------------------
GENRE_VOCAB = [
    "k-pop", "korean r&b", "pop", "hip hop", "r&b",
    "rock", "indie", "edm", "jazz", "ballad"
]

def genre_to_vec(genre):
    genre = str(genre).lower()
    vec = [1 if g in genre else 0 for g in GENRE_VOCAB]
    return vec


vectors = []
track_ids = {}

print("🎛 Generating 28-dimensional feature vectors...\n")

for idx, row in tqdm(df.iterrows(), total=len(df)):

    # ----------------------------
    # Numeric Features (18개)
    # ----------------------------
    track_pop_norm = row["popularity"] / 100
    explicit = int(row["explicit"])
    duration_norm = row["duration_ms"] / 600_000
    duration_seconds = row["duration_ms"] / 1000

    # Spotify API에서 얻는 정보들 요약값 사용(없으면 0)
    artist_pop_norm = 0
    followers_log = 0
    release_year_norm = 0
    release_month = 0
    release_day = 0
    release_age_days = 0
    release_decade = 0
    release_quarter = 0
    release_is_weekend = 0
    genre_count = 1
    popularity_delta = 0
    followers_millions = 0
    duration_short_flag = 0
    duration_long_flag = 0

    numeric_vector = [
        track_pop_norm,
        artist_pop_norm,
        followers_log,
        explicit,
        duration_norm,
        release_year_norm,
        release_month,
        release_day,
        release_age_days,
        release_decade,
        release_quarter,
        release_is_weekend,
        genre_count,
        popularity_delta,
        followers_millions,
        duration_seconds,
        duration_short_flag,
        duration_long_flag
    ]

    # ----------------------------
    # Genre (10개)
    # ----------------------------
    genre_vector = genre_to_vec(row["track_genre"])

    final_vector = numeric_vector + genre_vector  # 28 dim

    vectors.append(final_vector)
    track_ids[idx] = row["track_id"]


# ----------------------------
# 저장
# ----------------------------
np.save(os.path.join(OUTPUT_DIR, "kaggle_vectors.npy"), np.array(vectors))

with open(os.path.join(OUTPUT_DIR, "kaggle_track_ids.json"), "w", encoding="utf-8") as f:
    json.dump(track_ids, f, ensure_ascii=False, indent=2)

print("\n✅ Saved 28-dim vectors & IDs successfully!\n")
