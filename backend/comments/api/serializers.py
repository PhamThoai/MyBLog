from rest_framework import serializers
from comments.models import Comment
from accounts.api.serializers import CommentAccountSerializer

class CreateCommentSerializer(serializers.ModelSerializer):
    post = serializers.SlugField(required=True)
    class Meta:
        model = Comment
        fields = ['body', 'post', 'parent_comment']
        extra_kwargs = {
            'parent_comment': {'required': False}
        }
    
class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body']

class DetailCommentSerializer(serializers.ModelSerializer):
    have_replied = serializers.SerializerMethodField('get_have_replied')
    post = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'body', 'post', 'parent_comment', 'author', 'created_at', 'have_replied']

    def get_have_replied(self, obj):
        return Comment.objects.filter(parent_comment=obj).exists()

    def get_post(self, obj):
        return obj.post.slug
    
    def get_author(self, obj):
        return CommentAccountSerializer(obj.author).data
