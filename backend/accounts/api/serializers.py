from rest_framework import serializers
from django.conf import settings
from accounts.models import (
    Account, 
    Relationship,
    RELATIONSHIP_FOLLOWING,
    RELATIONSHIP_REPORT,

)
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from uuid import uuid4

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'confirm_password', 'display_name', 'introduction', 'first_name', 'last_name')
        write_only_fields = ['password' 'confirm_password']

    def validate(self, data):
        # Check for the existence of the username
        try:
            username_exists = Account.objects.get(username=data.get('username'))
        except Account.DoesNotExist:
            username_exists = False
        if username_exists:
            raise serializers.ValidationError(_('Username already exists'))
        
        # Check for the existence of the email
        try:
            email_exists = Account.objects.filter(email=data.get('email'))
        except Account.DoesNotExist:
            email_exists = False
        if email_exists:
            raise serializers.ValidationError(_('Umail already exists'))
        
        # Check for confirm password
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError(_('Empty Password'))

        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(_('Password mismatch'))
        else:
            pass
        
        # Check the length of the password
        if len(data.get('password')) < 8:
            raise serializers.ValidationError(_('Password must be longer than 8 characters'))
        
        return data

    def create(self, validated_data):
        """
        Create and return a new `Account` instance, given the validated data.
        """
        validated_data.pop('confirm_password')
        return Account.objects.create_user(**validated_data)


class DetailAccountSerializer(serializers.ModelSerializer):
    """Detail User Info """
    followed = serializers.SerializerMethodField('get_followed')
    followers = serializers.SerializerMethodField('get_followers')
    following = serializers.SerializerMethodField('get_following')
    # posts = serializers.SerializerMethodField('get_posts_num')
    # total_view = serializers.SerializerMethodField('get_total_view')
    
    class Meta:
        model = Account
        fields = ('slug', 'avatar', 'email', 'display_name', 'introduction', 'followers', 'following', 'followed') # posts, total_view


    def get_followed(self, obj):
        me =  self.context['me']
        if me:
            followed = Relationship.objects.filter(
                from_person=me.id, 
                to_person=obj.id, 
                status=RELATIONSHIP_FOLLOWING
            ).exists()
            return followed
        return False

    def get_followers(self, obj):
        return obj.get_followers().count()
    
    def get_following(self, obj):
        return obj.get_following().count()

    # def get_posts(self, obj):
    #     return obj.posts.all().count()

    # def get_total_view(self, obj):
    #     return obj.posts.all().count('views')


class ListAccountSerializer(serializers.ModelSerializer):
    """Detail User Info """
    followed = serializers.SerializerMethodField('get_followed')   
    followers = serializers.SerializerMethodField('get_followers')
    # total_view = serializers.SerializerMethodField('get_total_view')
    # posts = serializers.SerializerMethodField('get_posts_num')
    
    class Meta:
        model = Account
        fields = ('slug', 'thumbnail_small', 'display_name', 'followers', 'followed') # posts, total_view


    def get_followed(self, obj):
        me =  self.context['me']
        if me:
            followed = Relationship.objects.filter(
                from_person=me.id, 
                to_person=obj.id, 
                status=RELATIONSHIP_FOLLOWING
            ).exists()
            return followed
        return False

    def get_followers(self, obj):
        return obj.get_followers().count()
    
    # def get_total_view(self, obj):
    #     return obj.posts.all().count('views')

    # def get_posts(self, obj):
    #     return obj.posts.all().count()


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'display_name', 'introduction', 'first_name', 'last_name')


class AccountUpdateAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('avatar',)
    
    def update(self, instance, validated_data):
        f = validated_data.get('avatar').file
        uuid_image_name = uuid4().hex
        image = Image.open(f)

        image.thumbnail(settings.THUMBNAIL_SIZE_MEDIUM, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        instance.avatar.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        image.thumbnail(settings.THUMBNAIL_SIZE_SMALL, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        instance.thumbnail_small.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        image.thumbnail(settings.THUMBNAIL_SIZE_TINY, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        instance.thumbnail_tiny.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if not data.get('old_password') or not data.get('new_password') or not data.get('confirm_new_password'):
            raise serializers.ValidationError(_('Empty Password'))
        else:
            if len(data.get('new_password')) < 8 or len(data.get('confirm_new_password')) < 8:
                raise serializers.ValidationError(_('Password must be longer than 8 characters'))
        if data.get('new_password') != data.get('confirm_new_password'):
            raise serializers.ValidationError(_('Mismatch'))
        return data
