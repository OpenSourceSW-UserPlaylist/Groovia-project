
from django.urls import path
from .views import SpotifyLoginView, SpotifyCallbackView, SpotifySearchView, PingSpotifyView

urlpatterns = [
    path('login', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('search', SpotifySearchView.as_view(), name='spotify_search'),
    path('ping-spotify', PingSpotifyView.as_view(), name='ping_spotify'),
]