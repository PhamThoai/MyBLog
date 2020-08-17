from rest_framework import serializers
from tags.models import Tag
from posts.models import Post
from accounts.api.serializers import CommentAccountSerializer

class CreateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class DetailTagSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Tag
        fields = ['title', 'slug', 'create_at', 'author', 'posts']

    def get_posts(self, obj):
        return obj.post.all().count()

    def get_author(self, obj):
        return CommentAccountSerializer(obj.author).data

class ListTagInPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title', 'slug']


