def extract_track_id_from_url(spotify_url: str | None) -> str | None:
    if not spotify_url:
        return None

    url = spotify_url.strip()

    # 기대하는 형식이 아닌 경우 빠르게 제외
    if "open.spotify.com/track/" not in url:
        return None

    # track/ 이후 ID 추출
    try:
        parts = url.split("track/")[1]  # track/ 이후 문자열
        track_id = parts.split("?")[0]  # ? 앞까지만 ID
    except IndexError:
        return None

    # Spotify track_id는 항상 길이 22
    return track_id if len(track_id) == 22 else None
