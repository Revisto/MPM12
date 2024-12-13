from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Podcast, Episode, Category
from users.models import User
from interactions.models import View
from .serializers import PodcastSerializer, EpisodeSerializer, EpisodeUploadSerializer

class PodcastViewSet(viewsets.ModelViewSet):
    queryset = Podcast.objects.all().order_by('-created_at')
    serializer_class = PodcastSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user if request.user.is_authenticated else None
        # Record the view
        View.objects.create(user=user, podcast=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def episodes(self, request, pk=None):
        podcast = self.get_object()
        episodes = Episode.objects.filter(podcast=podcast).order_by('-created_at')
        serializer = EpisodeSerializer(episodes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def most_popular(self, request):
        podcasts = Podcast.objects.annotate(
            interaction_count=Count('views') + Count('episodes__views') + Count('episodes__like')
        ).order_by('-interaction_count')[:10]
        serializer = self.get_serializer(podcasts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def most_trending(self, request):
        time_threshold = timezone.now() - timedelta(days=7)
        podcasts = Podcast.objects.filter(
            Q(views__created_at__gte=time_threshold) |
            Q(episodes__views__created_at__gte=time_threshold) |
            Q(episodes__like__created_at__gte=time_threshold)
        ).annotate(
            interaction_count=Count('views') + Count('episodes__views') + Count('episodes__like')
        ).order_by('-interaction_count')[:10]
        serializer = self.get_serializer(podcasts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        podcasts = Podcast.objects.order_by('-created_at')[:10]
        serializer = self.get_serializer(podcasts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ai_generated(self, request):
        ai_podcasts = Podcast.objects.filter(
            Q(title__icontains='هوش مصنوعی') | Q(description__icontains='هوش مصنوعی')
        ).order_by('-created_at')
        serializer = self.get_serializer(ai_podcasts, many=True)
        return Response(serializer.data)

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all().order_by('-created_at')
    serializer_class = EpisodeSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user if request.user.is_authenticated else None
        # Record the view
        View.objects.create(user=user, episode=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def most_popular(self, request):
        episodes = Episode.objects.annotate(
            interaction_count=Count('views') + Count('like')
        ).order_by('-interaction_count')[:10]
        serializer = self.get_serializer(episodes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def most_trending(self, request):
        time_threshold = timezone.now() - timedelta(days=7)
        episodes = Episode.objects.filter(
            Q(views__created_at__gte=time_threshold) |
            Q(like__created_at__gte=time_threshold)
        ).annotate(
            interaction_count=Count('views') + Count('like')
        ).order_by('-interaction_count')[:10]
        serializer = self.get_serializer(episodes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        episodes = Episode.objects.order_by('-created_at')[:10]
        serializer = self.get_serializer(episodes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail": "User ID not provided."}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        # Get episodes of podcasts the user has viewed or liked
        viewed_podcasts = Podcast.objects.filter(views__user=user)
        liked_podcasts = Podcast.objects.filter(episodes__like__user=user)
        recommended_episodes = Episode.objects.filter(podcast__in=viewed_podcasts | liked_podcasts).exclude(views__user=user).distinct()[:10]

        serializer = self.get_serializer(recommended_episodes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        serializer = EpisodeUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
