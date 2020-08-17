from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from .serializers import (
    CreateCommentSerializer,
    UpdateCommentSerializer,
    DetailCommentSerializer
)
from comments.models import Comment
from posts.models import Post
from accounts.models import Account

class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    create a new comment.
    """
    def post(self, request):
        try:
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(slug=request.data.get('post'))
            except Post.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            parent_comment = serializer.data.get('parent_comment', None)
            if parent_comment:
                try:
                    parent_comment = Comment.objects.get(id=parent_comment_id)
                except Comment.DoesNotExist:
                    parent_comment = None
            comment = Comment()
            comment.body = serializer.data.get('body')
            comment.post = post
            comment.author = user
            comment.parent_comment = parent_comment
            comment.save()
            return Response(data=DetailCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # post_slug = request.data.get('post')
        
        
        # parent_comment_id = request.data.get('parent_comment')
        # if parent_comment:
        #     try:
        #         comment = Comment.objects.get(id=parent_comment_id)
        #     except Comment.DoesNotExist:
        #         return Response(status=status.HTTP_404_NOT_FOUND)
    
    """
    update a new comment.
    """
    def put(self, request, id):
        try:
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            commnent = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            author = Account.objects.get(id=commnent.author.id)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if user != author:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = UpdateCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    