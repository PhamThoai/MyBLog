from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from myblog.permissions import IsAuthorOrReadOnly
from tags.models import Tag
from .serializers import (
    CreateTagSerializer,
    DetailTagSerializer,
    ListTagSerializer
)


class TagList(APIView):
    """
    List all tags, or create a new tag.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        tags = Tag.objects.all()
        serializer = ListTagSerializer(tags, many=True)
        return Response(serializer.data)

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




