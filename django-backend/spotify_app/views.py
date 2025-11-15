import os, requests
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .spotify_client import get_track_metadata
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

class SpotifyLoginView(APIView): #Spotify 로그인 화면으로 이동시키는 API
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


class SpotifyCallbackView(APIView): #Spotify 인증 완료 후 Access Token을 발급받는 API
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        r = requests.post(token_url, data=data)
        r.raise_for_status()
        tokens = r.json()

        # access_token과 refresh_token 반환
        return Response(tokens)


class SpotifySearchView(APIView): #Spotify 곡 검색 결과를 Django REST API로 전달하는 엔드포인트
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


class PingSpotifyView(APIView):
    def get(self, request):
        try:
            track_id = request.GET.get("track_id", "3n3Ppam7vgaVa1iaRUc9Lp")  # default: Uptown Funk
            user_token = request.GET.get("token")

            if not user_token:
                return Response(
                    {"error": "Missing access token (token query parameter)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            metadata = get_track_metadata(track_id, user_token)

            return Response({
                "message": "Spotify API reachable ✅",
                "track_id": metadata.get("id"),
                "track_name": metadata.get("name"),
                "artists": metadata.get("artists"),
                "album_name": metadata.get("album_name"),
                "album_release_date": metadata.get("album_release_date"),
                "duration_ms": metadata.get("duration_ms"),
                "explicit": metadata.get("explicit"),
                "track_popularity": metadata.get("track_popularity"),
                "genres": metadata.get("genres"),
                "artist_popularity": metadata.get("artist_popularity"),
                "artist_followers": metadata.get("artist_followers"),
                "spotify_url": metadata.get("spotify_url"),
                "album_image_url": metadata.get("album_image_url"),
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


