from rest_framework import serializers
from image_files.models import ImageForPost
from accounts.models import Account
from accounts.api.serializers import DetailAccountSerializer
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from io import BytesIO
from uuid import uuid4

class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageForPost
        fields = ['image']
    
    def create(self, validated_data):
        image_file = ImageForPost()
        image_file.owner = self.context['me']

        f = validated_data.get('image').file
        uuid_image_name = uuid4().hex
        image = Image.open(f)

        # image.thumbnail(settings.THUMBNAIL_MOBILE_API, Image.ANTIALIAS)
        # image_io_thumb = BytesIO()
        # image.save(image_io_thumb, format="JPEG")
        # image_file.thumbnail_mobile_api.save(uuid_image_name + '.jpg',
        #                         ContentFile(image_io_thumb.getvalue()))
        # image_io_thumb.close()

        image.thumbnail(settings.THUMBNAIL_BIG_SIZE, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        image_file.image.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()
        image_file.save()
        return image_file

class DetailImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')
    owner = serializers.SerializerMethodField('get_owner')
    class Meta:
        model = ImageForPost
        fields = ['id', 'image_url', 'add_on', 'owner']

    def get_image_url(self, obj):
        try:
            return obj.image.url
        except:
            return None
    
    def get_owner(self, obj):
        return obj.owner.display_name

