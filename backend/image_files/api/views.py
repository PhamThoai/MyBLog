from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UploadImageSerializer,
    DetailImageSerializer,
)
from image_files.models import ImageForPost

class ImageList(APIView):
    """
    List all images, or create a new image.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get(self, request, format=None):
        images = ImageForPost.objects.filter(owner=request.user.id)
        serializer = DetailImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            me = request.user
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        context = {'me': me}
        serializer = UploadImageSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageDetail(APIView):
    """
    Retrieve, update or delete a image
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_object(self, image_id):
        try:
            return ImageForPost.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, image_id, format=None):
        image = self.get_object(image_id)
        serializer = DetailImageSerializer(image)
        return Response(serializer.data)

    def delete(self, request, image_id, format=None):
        try:
            me = request.user
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        image = self.get_object(image_id)

        if me != image.owner
            return Response(status=status.HTTP_403_FORBIDDEN)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)