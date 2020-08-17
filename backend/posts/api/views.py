from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.utils.timezone import now
from myblog.permissions import IsAuthorOrReadOnly, IsStaffOrIsSuperUser
from django.http import Http404

from .serializers import (
    PostCreateSerializer,
    PostUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer
)
from comments.api.serializers import DetailCommentSerializer
from comments.models import Comment

from posts.models import Post


class CreatePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context ={}
        context['request'] = request

        serializer = PostCreateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPost(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [AllowAny,]
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'description', 'author__display_name')

    def get_queryset(self):
        return Post.objects.filter(is_draft=False, is_publish=True).order_by('-publish_at')


class ListPostNeedPublish(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrIsSuperUser]
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('is_draft', 'title', 'description', 'author__display_name')

    def get_queryset(self):
        return Post.objects.filter(is_publish=False).order_by('update_at')


class DetailPost(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        try:
            user = request.user
        except:
            user = None
        context={'request': request}
        post = self.get_object(slug)
        if not post.is_publish:
            if user:
                if user.is_staff or user.is_superuser or post.author == user:
                    serializer = PostDetailSerializer(post, context=context)
                    return Response(serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        post.views = post.views + 1
        post.save()
        serializer = PostDetailSerializer(post, context=context)
        return Response(serializer.data)

    def put(self, request, slug, format=None):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        context={'request': request}
        serializer = PostUpdateSerializer(post, data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated ,IsStaffOrIsSuperUser])
def publish_post(request):
    messages = {}
    data = request.data
    try:
        user = request.user
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    publish_all = data.get('publish_all', False)
    if publish_all:
        messages['publish_all'] = True
        print("ngay khi vao sua doi")
        try:
            Post.objects.filter(is_draft=False, is_publish=False).update(is_publish=True, publish_by=user, publish_at=now())
        except:
            messages['result_success_all'] = False
            return Response(data=messages, status=status.HTTP_400_BAD_REQUEST)
        messages['result_success_all'] = True
        print('ngay truoc return')
        return Response(data=messages, status=status.HTTP_200_OK)
        
    slugs = data.get('slugs',[])
    results = []
    result_success_all = True
    for slug in slugs:
        message = {}
        slug_dict = dict(slug)
        slug_str = slug.get("slug", '')
        message['slug'] = slug_str
        try:
            post = Post.objects.get(slug=slug_str)
        except Post.DoesNotExist:
            result_success_all = False
            message['result'] = 'not_found'
            results.append(message)
            continue

        if post.is_draft:
            result_success_all = False
            message['result'] = 'post is draft'
            results.append(message)
            continue

        if post.is_publish:
            message['result'] = 'the post is in public'
            results.append(message)
            continue
        
        post.is_publish = True
        post.publish_by = user
        post.publish_at = now()
        post.save()

        message['result'] = 'published successfully'
        results.append(message)

    if result_success_all:
        messages['result_success_all'] = True
    else:
        messages['result_success_all'] = False
        messages['results'] = results
    
    return Response(data=messages, status=status.HTTP_200_OK)


class ListCommentsOfPost(ListAPIView):
    serializer_class = DetailCommentSerializer
    permission_classes = [AllowAny,]
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('body', 'author__display_name')

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            post = Post.objects.get(slug=slug)
        except:
            return []
        return Comment.objects.filter(post=post, parent_comment=None).order_by('-created_at')



