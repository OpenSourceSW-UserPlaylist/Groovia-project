
from django.urls import path

from .views import PingSpotifyView, PingView, UrlProcessView

urlpatterns = [
    path('ping-spotify', PingSpotifyView.as_view(), name='ping_spotify'),
    path('ping/', PingView.as_view(), name='spotify_ping'),
    path('process-urls/', UrlProcessView.as_view(), name='process_urls'),
]

# path('search', SpotifySearchView.as_view(), name='spotify_search'),
# path('features', FeatureExtractView.as_view(), name='spotify_features'),
# path("api/recommend", RecommendView.as_view()),
# path('login', SpotifyLoginView.as_view(), name='spotify_login'),
# path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
