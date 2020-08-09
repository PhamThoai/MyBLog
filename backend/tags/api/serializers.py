from rest_framework import serializers
from tags.models import Tag

class CreateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class DetailTagSerializer(serializers.ModelSerializer):
    # posts = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Tag
        fields = ['id', 'title', 'slug', 'create_at', 'author']

    # def get_posts(self, obj):
    #     return obj.post.all().count()

    def get_author(self, obj):
        return obj.author.display_name

class ListTagSerializer(serializers.ModelSerializer):
    # posts = serializers.SerializerMethodField()
    class Meta:
        model = Tag
        fields = ['id', 'title', 'slug']

    # def get_posts(self, obj):
    #     return obj.post.all().count()


