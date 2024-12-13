from rest_framework import serializers
from .models import Podcast, Episode

class PodcastSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Podcast
        fields = '__all__'

class EpisodeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    view_count = serializers.IntegerField(read_only=True)
    podcast_name = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return request.build_absolute_uri(obj.podcast.image.url) if obj.podcast.image else None

    def get_podcast_name(self, obj):
        return obj.podcast.title

class EpisodeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['podcast', 'title', 'description', 'audio_file', 'transcript', 'ai_summary', 'image']