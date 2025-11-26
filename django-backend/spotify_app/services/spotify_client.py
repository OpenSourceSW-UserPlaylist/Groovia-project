import os, base64, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


# -------------------------------------
# Client Credentials Token 발급 함수
# -------------------------------------
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


def get_track_metadata(track_id, token):
    """
    Track/Artist 메타데이터를 가져오는 함수.
    - 허용된 /v1/tracks, /v1/artists 엔드포인트만 사용
    """
    if not token:
        raise ValueError("User access token is required.")

    headers = {"Authorization": f"Bearer {token.strip()}"}

    # 1) 트랙 기본 정보
    track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    track_res = requests.get(track_url, headers=headers)

    print("🎧 [Spotify Request - Track]", track_url)
    print("📡 [Response Status]", track_res.status_code)
    print("📃 [Response Body]", track_res.text[:200])
    track_res.raise_for_status()
    track = track_res.json()

    album = track.get("album") or {}
    artists = track.get("artists") or []
    primary_artist = artists[0] if artists else {}
    artist_id = primary_artist.get("id")

    genres = []
    artist_popularity = None
    artist_followers = None

    # 2) 아티스트 정보 (장르 등)
    if artist_id:
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_res = requests.get(artist_url, headers=headers)

        print("🎧 [Spotify Request - Artist]", artist_url)
        print("📡 [Artist Status]", artist_res.status_code)
        print("📃 [Artist Body]", artist_res.text[:200])
        if artist_res.ok:
            artist = artist_res.json()
            genres = artist.get("genres") or []
            artist_popularity = artist.get("popularity")
            followers = artist.get("followers") or {}
            artist_followers = followers.get("total")
    

    # 3) 정리된 메타데이터
    images = album.get("images") or []
    album_image_url = images[0]["url"] if images else None
    print("\n\n\n\n\nmetaData추출 성공\n\n\n\n\n")
    return {
        "id": track.get("id"),
        "name": track.get("name"),
        "artists": [a.get("name") for a in artists if a.get("name")],
        "album_name": album.get("name"),
        "album_release_date": album.get("release_date"),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit"),
        "track_popularity": track.get("popularity"),
        "spotify_url": track.get("external_urls", {}).get("spotify"),
        "album_image_url": album_image_url,
        "genres": genres,
        "artist_popularity": artist_popularity,
        "artist_followers": artist_followers,
    }


# 토큰 추출 함수
def exchange_code_for_token(code, redirect_uri, client_id, client_secret):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = requests.post(token_url, data=data)

    r.raise_for_status()
    return r.json()
