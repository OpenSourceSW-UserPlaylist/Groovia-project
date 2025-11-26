import os
import json
import base64
import requests
import csv

from django.core.management.base import BaseCommand

from spotify_app.spotify_client import get_track_metadata
from spotify_app.feature_extractor import extract_features
from spotify_app.recommend_engine import AnnoyRecommender


# -----------------------------------------
# 1) 실험용 가중치 세트 
# -----------------------------------------
WEIGHT_CASES = [
    (0.1, 1.9),
    (0.5, 1.5),
    (0.8, 1.2),
    (1.2, 0.8),
    (1.5, 0.5),
]


# -----------------------------------------
# 2) 실험용 Track ID 리스트
# -----------------------------------------
TEST_TRACK_IDS = [
    "3n3Ppam7vgaVa1iaRUc9Lp",
    "4VqPOruhp5EdPBeR92t6lQ",
    "7ouMYWpwJ422jRcDASZB7P",
]


# -----------------------------------------
# 3) Spotify Client Credentials 토큰 자동 발급
# -----------------------------------------
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_client_credentials_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
        ).decode()
    }
    data = {"grant_type": "client_credentials"}

    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()
    return res.json()["access_token"]


# -----------------------------------------
# 4) 단일 실험 실행
# -----------------------------------------
def run_experiment(track_ids, numeric_weight, genre_weight, token):
    metadata_list = [get_track_metadata(tid, token) for tid in track_ids]
    features_list = [extract_features(meta) for meta in metadata_list]

    user_vectors = []
    for f in features_list:
        num = [x * numeric_weight for x in f["numeric_vector"]]
        gen = [g * genre_weight for g in f["genre_vector"]]
        user_vectors.append(num + gen)

    rec = AnnoyRecommender()
    recommended = rec.recommend_top_k(user_vectors, k=10)

    return {
        "track_ids": track_ids,
        "numeric_weight": numeric_weight,
        "genre_weight": genre_weight,
        "recommended": recommended,
    }


# -----------------------------------------
# 5) Management Command
# -----------------------------------------
class Command(BaseCommand):
    help = "Run automated recommendation experiments (weights × track count)"

    def handle(self, *args, **options):

        # 자동 Access Token
        access_token = get_client_credentials_token()
        self.stdout.write(self.style.SUCCESS("✓ Spotify Token 발급 완료"))

        all_results = []

        # Track Count = 1, 2, 3
        for track_count in [1, 2, 3]:
            tid_slice = TEST_TRACK_IDS[:track_count]
            self.stdout.write(f"\n=== Track Count = {track_count} ===")

            for idx, (nw, gw) in enumerate(WEIGHT_CASES, start=1):
                result = run_experiment(
                    tid_slice,
                    numeric_weight=nw,
                    genre_weight=gw,
                    token=access_token
                )

                all_results.append([
                    f"{track_count}tracks_case{idx}",
                    track_count,
                    ",".join(result["track_ids"]),
                    result["numeric_weight"],
                    result["genre_weight"],
                    ",".join(result["recommended"])
                ])

                self.stdout.write(f" → Completed case {idx}")

        self.stdout.write(self.style.SUCCESS("\n✓ 모든 실험 완료! (CSV만 생성)"))

        # ----------------------------
        # CSV 저장
        # ----------------------------
        output_csv = "experiment_results_export.csv"

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_name", "track_count",
                "track_ids", "numeric_weight",
                "genre_weight", "recommended_tracks"
            ])
            writer.writerows(all_results)

        self.stdout.write(self.style.SUCCESS(f"✓ CSV 생성 완료 → {output_csv}"))


        # ====================================================
        # 6) 입력 트랙 vs 추천 결과 유사도 검사 (콘솔 출력만)
        # ====================================================

        cases = {}

        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                case_name = row["case_name"]
                tcount = int(row["track_count"])
                rec_list = row["recommended_tracks"].split(",")

                cases[case_name] = {
                    "tcount": tcount,
                    "tracks": rec_list
                }

        # Jaccard 정의
        def jaccard(a, b):
            a = set(a)
            b = set(b)
            return len(a & b) / len(a | b) if len(a | b) else 0

        # 각 case별로 유사도 계산해서 콘솔에 표시
        self.stdout.write("\n=== 입력 트랙 vs 추천 결과 유사도 ===")

        for cname, info in cases.items():
            tcount = info["tcount"]
            input_tracks = TEST_TRACK_IDS[:tcount]
            sim = jaccard(input_tracks, info["tracks"])

            self.stdout.write(
                f"{cname}  (입력 {tcount}트랙)  →  유사도: {sim:.4f}"
            )

        self.stdout.write(self.style.SUCCESS("\n✓ 전체 실험 종료 (CSV + 유사도 계산만)"))
