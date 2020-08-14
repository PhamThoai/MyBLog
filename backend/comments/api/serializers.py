from rest_framework import serializers
from comments.models import Comment


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body', 'post', 'parent_comment']
    
class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body']

class DetailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'body', 'post', 'parent_comment', 'author', 'created_at']
