from rest_framework import serializers
from .models import Like, Comment, View

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    commenter_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_commenter_name(self, obj):
        return obj.user.username if obj.user else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('comments'):
            data['comments'] = []
        return data

class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = '__all__'