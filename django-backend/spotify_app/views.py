import os, requests, time
import numpy as np

from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .spotify_client import get_track_metadata, exchange_code_for_token
from .feature_extractor import extract_features
from .recommend_engine import AnnoyRecommender
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Spotify 로그인 화면으로 이동시키는 API 
# (spotify 인증 URL(auth_url)을 만들어 redirect)
class SpotifyLoginView(APIView): 
    def get(self, request):
        scope = "user-read-private user-read-email"
        auth_url = (
            "https://accounts.spotify.com/authorize"
            f"?client_id={CLIENT_ID}"
            "&response_type=code"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={scope}"
        )
        return redirect(auth_url)


# Spotify 인증 완료하면 redirect_uri로 코드 수령 -> Access Token을 요청하는 API
class SpotifyCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        tokens = exchange_code_for_token(
            code,
            REDIRECT_URI,
            CLIENT_ID,
            CLIENT_SECRET
        )

        access_token = tokens.get("access_token")

        view = PingSpotifyView()

        return view.process_with_token(access_token)

class PingSpotifyView(APIView):
    """
    1) 3개 음악 metadata → feature 추출
    2) Annoy로 10곡 추천
    3) 모든 결과를 한 번에 반환
    """

    # GET/POST에서 token을 request로 받지 않고,
    # callback에서 직접 process_with_token(token) 호출하는 방식 사용

    def process_with_token(self, token):
        # ----------------------------
        # 1) track_ids 선언
        # ----------------------------
        track_ids = [
            "3n3Ppam7vgaVa1iaRUc9Lp", 
            "4VqPOruhp5EdPBeR92t6lQ",
            "7ouMYWpwJ422jRcDASZB7P",
        ]

        # ----------------------------
        # 2) 트랙 metadata 가져오기
        # ----------------------------
        metadata_list = []
        for tid in track_ids:
            metadata = get_track_metadata(tid, token)
            metadata_list.append(metadata)

        # ----------------------------
        # 3) feature 추출
        # ----------------------------
        features_list = []
        for metadata in metadata_list:
            print("\n\n\n\nSLEEPING.....\n\n\n\n")
            time.sleep(0.8) # 0.8초 rest (spotify와는 무관하지만 일단 rest)
            features = extract_features(metadata)
            features_list.append(features)

        # ----------------------------
        # 4) Annoy 벡터 구성
        # ----------------------------
        user_vectors = []
        for f in features_list:
            numeric = f["numeric_vector"]
            genre = f["genre_vector"]
            vector = numeric + genre
            user_vectors.append(vector)

        # ----------------------------
        # 5) Annoy 추천 실행
        # ----------------------------
        rec = AnnoyRecommender()
        recommended_ids = rec.recommend_top_k(user_vectors, k=10)

        # ----------------------------
        # 6) 최종 응답 반환
        # ----------------------------
        return Response({
            "success": True,
            "input_track_count": len(features_list),
            "input_tracks": [
                {
                    "track_id": metadata_list[i]["id"],
                    "features": features_list[i]
                }
                for i in range(len(features_list))
            ],
            "recommended_track_ids": recommended_ids,
            "recommended_count": len(recommended_ids)
        })
    
class PingView(APIView):
    def get(self, request):
        return Response({"message": "pong"})
    
class UrlProcessView(APIView):
    """
    Flutter에서 보낸 URL 리스트를 받아 처리하는 API
    Method: POST
    """
    def post(self, request):
        # 1. Flutter에서 보낸 데이터 받기
        # 예: {"urls": ["https://open.spotify.com/track/...", "https://..."]}
        input_urls = request.data.get('urls', [])

        if not input_urls:
            return Response(
                {"error": "URL 리스트가 비어있습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        processed_results = []

        # 2. URL 처리 로직
        for url in input_urls:
            # 예시: 단순 수신 확인 (나중에 여기에 Spotify ID 추출 로직 등을 넣으면 됩니다)
            result_data = {
                "original_url": url,
                "status": "success",
                "message": "URL을 정상적으로 수신했습니다."
            }
            processed_results.append(result_data)

        # 3. 결과 반환
        return Response({"results": processed_results}, status=status.HTTP_200_OK)


# FeatureExtractView: 미사용
'''
class FeatureExtractView(APIView): #for test
    """ 기본 Mega Extractor """
    def get(self, request):
        token = request.GET.get("token")
        track_id = request.GET.get("track_id")

        metadata = get_track_metadata(track_id, token)
        features = extract_features(metadata)

        return Response({
            "success": True,
            "mode": "basic",
            "features": features
        })
'''

# RecommendView: 미사용
'''
class RecommendView(APIView): #for test
    """
    MultiTrackFeatureExtractView 결과(JSON)를 입력받아
    Annoy 기반 추천 10곡 반환
    """

    def post(self, request):
        tracks = request.data.get("tracks", [])

        if len(tracks) == 0:
            return Response({"error": "tracks missing"}, status=400)

        user_vectors = []

        try:
            for track in tracks:
                nf = track["features"]["numeric_vector"]
                gf = track["features"]["genre_vector"]
                vector = nf + gf
                user_vectors.append(vector)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # Annoy 추천 실행
        rec = AnnoyRecommender()
        recommended_ids = rec.recommend_top_k(user_vectors, k=10)

        return Response({
            "success": True,
            "mode": "embedding",
            "features": features
            "recommended_track_ids": recommended_ids,
            "count": len(recommended_ids)
        })
'''

# RecommendView: 미사용 (검색 결과 필요 시 사용)
'''
class SpotifySearchView(APIView): # Spotify 곡 검색 결과를 Django REST API로 전달하는 엔드포인트
    def get(self, request):
        access_token = request.GET.get("token")
        query = request.GET.get("q", "IU")
        if not access_token:
            return Response({"error": "Missing access token"}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=5"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return Response(r.json())
'''
