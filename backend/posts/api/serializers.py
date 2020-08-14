from rest_framework import serializers
from tags.models import Tag
from tags.api.serializers import PostCreateSerializer, ListTagSerializer
from comments.models import Comment 
from post.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        tags = PostCreateSerializer(many=True, required=False)
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
        author = validated_data.get('author')
        post = Post.objects.create(**validated_data)
        for tag in tags_data:
            tag = dict(tag)
            obj, created = Tag.objects.get_or_create(
                title= tag.get('title'),
                defaults={'author': author},
            )
            post.tags.add(obj)
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        author = validated_data.pop('author')

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.is_draft = validated_data.get('is_draft', instance.is_draft)
        instance.enable_cmt = validated_data.get('enable_cmt', instance.enable_cmt)
        instance.save()

        old_tags = instance.tags.all()
        not_update_tags = []
        for old_tag in old_tags:
            need_delete = True
            for tag in tags_data:
                if tag.title = old_tag.title:
                    not_update_tags.append(tag.title)
                    need_delete = False
            if need_delete:
                instance.tags.remove(old_tag)

        for tag in tags_data:
            obj, created = Tag.objects.get_or_create(
                title= tag.title,
                defaults={'author': author},
            )
            post.tags.add(obj)


class PostDetailSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='slug'
    )
    author = UserSumarySerializer(read_only=True)
    html = SerializerMethodField()
    number_comments = SerializerMethodField()
    tags = SerializerMethodField()

    def get_html(self, obj):
        return obj.get_markdown()

    def get_number_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()
    
    def get_tags(self, obj):
        tags = obj.tags.all()
        tags = ListTagSerializer(tags, many=True).data
        return tags

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "urls",
            "description",
            "html",
            "enable_cmt",
            "author",
            "publish_at",
            "tags",
            "views",
        ]
    

class PostListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='slug'
    )
    author = UserSumarySerializer(read_only=True)
    number_comments = SerializerMethodField()
    tags = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "url",
            "description",
            "author",
            "publish_at",
            "tags",
            "views",
        ]

    def get_number_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()
    
    def get_tags(self, obj):
        tags = obj.tags.all()
        tags = ListTagSerializer(tags, many=True).data
        return tags
    
    
