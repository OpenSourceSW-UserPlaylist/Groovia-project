
from django.urls import path
from .views import SpotifyLoginView, SpotifyCallbackView, SpotifySearchView, PingSpotifyView, FeatureExtractView, FeatureExtractEmbeddingView
from .views import PingSpotifyView
from .views import UrlProcessView

urlpatterns = [
    path('login', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('search', SpotifySearchView.as_view(), name='spotify_search'),
    path('ping-spotify', PingSpotifyView.as_view(), name='ping_spotify'),
    path('ping/', PingView.as_view(), name='spotify-ping'),
    path('features', FeatureExtractView.as_view(), name='spotify_features'),
    path("features-embedding", FeatureExtractEmbeddingView.as_view(), name="features_embedding"),
    path('process-urls/', UrlProcessView.as_view(), name='process_urls'),
]