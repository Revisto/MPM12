from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikeViewSet, CommentViewSet, ViewViewSet

router = DefaultRouter()
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'views', ViewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('comments/podcast/<int:podcast_id>/', CommentViewSet.as_view({'get': 'list_by_podcast'}), name='comments-by-podcast'),
]