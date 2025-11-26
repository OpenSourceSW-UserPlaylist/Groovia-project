from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from spotify_app.services.recommendation_service import run_recommendation
from spotify_app.services.url_parser import extract_track_id_from_url

from dotenv import load_dotenv
from django.conf import settings

load_dotenv()

# ============================================================
# 모드 스위치: settings.py 에서 SPOTIFY_MODE="A" or "B"
# ============================================================
SPOTIFY_MODE = getattr(settings, "SPOTIFY_MODE", "A")   # 기본 A(Flutter POST 모드) / # B(PingSpotifyView 모드)



# ============================================================
# B 모드: runserver 실행 시 자동 추천 실행
# ============================================================
class PingSpotifyView(APIView):
    """
    3개 기본 Track으로 추천을 실행하는 테스트 View.
    """

    default_track_ids = [
        "3n3Ppam7vgaVa1iaRUc9Lp",
        "4VqPOruhp5EdPBeR92t6lQ",
        "7ouMYWpwJ422jRcDASZB7P",
    ]

    def get(self, request):
        """GET 요청을 받으면 바로 추천 실행"""
        return self.process_with_token()

    def process_with_token(self):

        metadata_list, features_list, recommended_ids = run_recommendation(
            self.default_track_ids
        )

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


# ============================================================
# A 모드: Flutter POST 수신 → 추천 실행
# ============================================================
class UrlProcessView(APIView):
    """
    Flutter에서 여러 URL → track_id 추출 → 추천 실행
    """
    def get(self, request):
        return Response({"msg": "GET received"})

    def post(self, request):

        # A 모드에서만 실행
        if SPOTIFY_MODE != "A":
            return Response(
                {"error": "현재 모드는 A(Flutter POST 모드)가 아닙니다."},
                status=400
            )

        input_urls = request.data.get("urls", [])

        if not input_urls:
            return Response(
                {"error": "URL 리스트가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------------------------
        # track_id 추출 단계
        # ---------------------------------------------------
        track_ids = []
        print(input_urls)
        for url in input_urls:
            tid = extract_track_id_from_url(url)
            if tid:  
                track_ids.append(tid)

        track_ids = track_ids[:3]
        print(track_ids)

        if not track_ids:
            return Response(
                {"error": "유효한 Spotify track_id를 추출하지 못했습니다."},
                status=400
            )
        
        # -------------------------
        # 추천 실행
        # -------------------------
        metadata_list, features_list, recommended_ids = run_recommendation(track_ids)

        print(recommended_ids)

        return Response({
            "message": f"추천 알고리즘 성공! 총 {len(recommended_ids)}곡 추천 완료.",
            "result": recommended_ids
        })
        '''
        # flutter로 리턴
        return Response({
            "success": True,
            "received_urls": input_urls,
            "parsed_track_ids": track_ids,
            "input_track_count": len(track_ids),
            "recommended_track_ids": recommended_ids
        })
        '''

        '''
        # flutter로 리턴
        return Response({
            # Flutter가 'results' 키를 기대하므로 리스트로 감싸서 반환
            "results": [
                {
                        "success": True,
                        "input_track_count": len(track_ids),
                        "recommended_track_ids": recommended_ids
                }
            ],
            # 추가적인 최상위 정보 (선택 사항)
            "status_code": status.HTTP_200_OK,
            "input_urls_processed": input_urls,
        })
        '''



# ============================================================
# PingView (기본 연결 확인용)
# ============================================================
class PingView(APIView):
    def get(self, request):
        return Response({
            "message": "pong",
            "mode": SPOTIFY_MODE  # 현재 모드 알려주기
        })


# ========================================================= #















# ========================================================= #
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
