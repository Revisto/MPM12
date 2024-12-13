from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PodcastViewSet, EpisodeViewSet

router = DefaultRouter()
router.register(r'podcasts', PodcastViewSet)
router.register(r'episodes', EpisodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('podcasts/ai_generated/', PodcastViewSet.as_view({'get': 'ai_generated'}), name='ai-generated-podcasts'),
]