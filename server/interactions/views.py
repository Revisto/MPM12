from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Like, Comment, View
from .serializers import LikeSerializer, CommentSerializer, ViewSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @action(detail=False, methods=['post'], url_path='like-episode')
    def like_episode(self, request):
        user_id = request.data.get('user_id')
        episode_id = request.data.get('episode_id')

        if not user_id or not episode_id:
            return Response({'error': 'user_id and episode_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        like, created = Like.objects.get_or_create(user_id=user_id, episode_id=episode_id)

        if created:
            return Response({'message': 'Episode liked successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Episode already liked'}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.all().order_by('-created_at')

    @action(detail=False, methods=['get'], url_path='podcast/(?P<podcast_id>[^/.]+)')
    def list_by_podcast(self, request, podcast_id=None):
        queryset = self.get_queryset().filter(podcast_id=podcast_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ViewViewSet(viewsets.ModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer