from rest_framework import serializers
from tags.models import Tag
from tags.api.serializers import ListTagInPostSerializer
from comments.models import Comment 
from posts.models import Post
from accounts.api.serializers import (
    ListAccountSerializer,
    PostListAccountSerializer
)


class TagsInPostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)


class PostCreateSerializer(serializers.ModelSerializer):
    tags = TagsInPostSerializer(many=True, required=False)
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "content",
            "is_draft",
            "enable_cmt",
            "tags"
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        author =  self.context['request'].user

        post = Post.objects.create(**validated_data, author=author)
        for tag in tags_data:
            obj, created = Tag.objects.get_or_create(
                title= tag.get('title'),
                defaults={'author': author},
            )
            post.tags.add(obj)
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    tags = TagsInPostSerializer(many=True, required=False)
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "content",
            "is_draft",
            "enable_cmt",
            "tags"
        ]
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'content': {'required': False},
            'is_draft': {'required': False},
            'enable_cmt': {'required': False},
            'tags': {'required': False},
        }


    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        request =  self.context['request']
        author = request.user

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.is_draft = validated_data.get('is_draft', instance.is_draft)
        instance.enable_cmt = validated_data.get('enable_cmt', instance.enable_cmt)
        instance.is_publish = False

        if tags_data:
            old_tags = instance.tags.all()
            not_update_tags = []
            for old_tag in old_tags:
                need_delete = True
                for tag in tags_data:
                    if tag.get('title') == old_tag.title:
                        not_update_tags.append(tag.get('title'))
                        need_delete = False
                if need_delete:
                    instance.tags.remove(old_tag)

            for tag in tags_data:
                obj, created = Tag.objects.get_or_create(
                    title= tag.get('title'),
                    defaults={'author': author},
                )
                instance.tags.add(obj)
            instance.save()
        return instance


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    html = serializers.SerializerMethodField()
    number_comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    def get_author(self, obj):
        return ListAccountSerializer(obj.author, context=self.context).data

    def get_html(self, obj):
        return obj.get_markdown()

    def get_number_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()
    
    def get_tags(self, obj):
        tags = obj.tags.all()
        tags = ListTagInPostSerializer(tags, many=True).data
        return tags

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "description",
            "html",
            "enable_cmt",
            "author",
            "publish_at",
            "tags",
            "views",
            "number_comments"
        ]
    
 
class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    number_comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "description",
            "author",
            "publish_at",
            "tags",
            "views",
            "number_comments"
        ]

    def get_number_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()
    
    def get_author(self, obj):
        return PostListAccountSerializer(obj.author).data

    def get_tags(self, obj):
        tags = obj.tags.all()
        tags = ListTagInPostSerializer(tags, many=True).data
        return tags
    
    
