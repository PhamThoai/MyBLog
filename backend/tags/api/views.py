from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from myblog.permissions import IsAuthorOrReadOnly
from tags.models import Tag
from .serializers import (
    CreateTagSerializer,
    DetailTagSerializer,
    ListTagInPostSerializer
)
from posts.api.serializers import PostListSerializer
from posts.models import Post


class ListTags(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = DetailTagSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ('title',)


class CreateTag(APIView):
    """
    Create a new tag.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            author = request.user
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CreateTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagDetail(APIView):
    """
    Retrieve, update or delete a tag instance.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, slug):
        try:
            return Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, slug, format=None):
        tag = self.get_object(slug)
        serializer = DetailTagSerializer(tag)
        return Response(serializer.data)

    # def put(self, request, slug, format=None):
    #     tag = self.get_object(slug)
    #     serializer = CreateTagSerializer(tag, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPostOfTags(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [AllowAny,]
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'author__display_name')

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            tag = Tag.objects.get(slug=slug)
        except:
            return []
        return tag.post_set.all().filter(is_publish=True).order_by('-publish_at')





