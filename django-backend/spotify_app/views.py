from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from spotify_app.services.recommendation_service import run_recommendation
from spotify_app.services.url_parser import extract_track_id_from_url
from spotify_app.services.spotify_client import get_track_metadata, get_client_credentials_token


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
        "3AJwUDP919kvQ9QcozQPxg",
        "7D0RhFcb3CrfPuTJ0obrod",
        "1mea3bSkSGXuIRvnydlB5b",
    ]
    
    '''
    default_track_ids = [
    "0VjIjW4GlUZAMYd2vXMi3b",  # Blinding Lights - The Weeknd
    "463CkQjx2Zk1yXoT7XHjEa",  # Levitating - Dua Lipa
    "6b8Be6ljOzmkOmFslEb23P"   # 24K Magic - Bruno Mars
    ]
    '''
    def get(self, request):
        """GET 요청을 받으면 바로 추천 실행"""
        return self.process_with_token()

    def process_with_token(self):
        _, _, final_playlist = run_recommendation(self.default_track_ids)

        return Response({
            "success": True,
            "message": f"총 {len(final_playlist)}곡 추천 완료",
            "playlist": final_playlist 
        }, status=status.HTTP_200_OK)




# ============================================================
# A 모드: Flutter POST 수신 → 추천 실행
# ============================================================
class UrlProcessView(APIView):
    """
    Flutter에서 여러 URL → track_id 추출 → 추천 실행 → 상세 정보(제목/이미지) 반환
    """
    def get(self, request):
        return Response({"msg": "GET received. 서버 정상 작동 중 ✅"})

    def post(self, request):
        # A 모드 체크
        if SPOTIFY_MODE != "A":
            return Response({"error": "현재 모드는 A가 아닙니다."}, status=400)

        # 1. 데이터 받기
        input_urls = request.data.get("urls", [])

        if not input_urls:
            return Response({"error": "URL 리스트가 비어있습니다."}, status=400)

        # ---------------------------------------------------------
        # 2. track_id 추출
        # ---------------------------------------------------------
        track_ids = []
        for url in input_urls:
            tid = extract_track_id_from_url(url)
            if tid: track_ids.append(tid)

        track_ids = track_ids[:3] # 최대 3개

        if not track_ids:
            return Response({"error": "유효한 Spotify ID를 찾지 못했습니다."}, status=400)
        
        # ---------------------------------------------------------
        # 3. 추천 실행 (ID 리스트 획득)
        # ---------------------------------------------------------
        # (앞의 메타데이터 변수는 안 쓰므로 _ 로 처리)
        _, _, final_playlist = run_recommendation(track_ids)

        # ---------------------------------------------------------
        # 4. 결과 반환 (Flutter가 기다리는 'playlist' 키에 담기)
        # ---------------------------------------------------------
        return Response({
            "success": True,
            "message": f"총 {len(final_playlist)}곡 추천 완료",
            "playlist": final_playlist 
        }, status=status.HTTP_200_OK)
        



# ============================================================
# PingView (기본 연결 확인용)
# ============================================================
class PingView(APIView):
    def get(self, request):
        return Response({
            "message": "pong",
            "mode": SPOTIFY_MODE  # 현재 모드 알려주기
        })

