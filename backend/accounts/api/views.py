from django.urls import reverse
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    renderer_classes, 
    parser_classes
)
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated 
)
from PIL import Image

from myblog.utils import get_md5
from accounts.models import (
    Account,
    Relationship,
    RELATIONSHIP_FOLLOWING,
    RELATIONSHIP_REPORT,
)
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    DetailAccountSerializer,
    ListAccountSerializer,
    AccountUpdateSerializer,
    AccountUpdateAvatarSerializer
)

from posts.api.serializers import PostListSerializer
from posts.models import Post


@api_view(['POST'])
@permission_classes([AllowAny])
def register_apiview(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['title'] = _('success')
            data['message'] = _('Congratulations on your successful registration. A verification email has been sent to your email. Please verify your email and log in to this site.')
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer,TemplateHTMLRenderer])
def account_result(request):
    if request.method == 'GET':
        type = request.GET.get('type')
        id = request.GET.get('id')
        User = get_user_model()
        data = {}
        try:
            user = User.objects.get(pk=id)
        except Snippet.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user.is_confirmed_email:
            data['title'] = 'success'
            data['message'] = _('The email has been previously confirmed, you can now use your account to log in to this site.')
            return Response(data, template_name='accounts/result.html', status=status.HTTP_200_OK)

        if type == 'validation':
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.email) + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                data['title'] = 'error'
                data['message'] = _('Access is forbidden!')
                return Response(data, template_name='accounts/result.html', status=status.HTTP_403_FORBIDDEN)
            user.is_confirmed_email = True
            user.save()

            data['title'] = 'success'
            data['message'] = _('Congratulations, you have successfully completed the email verification, you can now use your account to log in to this site.')
            return Response(data, template_name='accounts/result.html', status=status.HTTP_200_OK)
        
        data['title'] = 'error'
        data['message'] = _('Not support type')
        return Response(data, template_name='accounts/result.html', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def change_password_apiview(request):
    if request.method in ['PUT', 'POST']:
        data = {}
        Account = get_user_model()
        try: 
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user.get_user_social():
            data['message'] = _("Don't change the password of the account create network social")
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")
            confirm_new_password = serializer.data.get("confirm_new_password")
            print(old_password)

            if not check_password(old_password, user.password):
                data['message'] = _("Old password doesn't match!")
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            data['message'] = _('successfully changed password')
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def detail_user_profile_apiview(request, slug):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(slug=slug)
    except UserModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    context = {'request': request}
    
    if request.method == 'GET':
        serializer = DetailAccountSerializer(user, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile_apiview(request):
    try:
        user = request.user
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = AccountUpdateSerializer(user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = _('Account update success')
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def update_user_avatar_apiview(request):
    try:
        user = request.user
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        # f = request.data.get('avatar').file
        # image_file = Image.open(f)
        # print(type(image_file))
        serializer = AccountUpdateAvatarSerializer(user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = _('Account update avatar success')
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user_apiview(request, slug):
    try:
        user = Account.objects.get(slug=slug)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    try:
        me = request.user
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        if me == user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        me.add_relationship(person=user, status=RELATIONSHIP_FOLLOWING)
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user_apiview(request, slug):
    try:
        user = Account.objects.get(slug=slug)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    try:
        me = request.user
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        if me == user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        me.add_relationship(person=user, status=RELATIONSHIP_FOLLOWING)
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_apiview(request, slug, description):
    try:
        user = Account.objects.get(slug=slug)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    try:
        me = request.user
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if me == user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Relationship.objects.filter(from_person=me, to_person=user, status=RELATIONSHIP_FOLLOWING).delete()
        return Response(status=status.HTTP_200_OK)

class GetFollowers(generics.ListAPIView):
    serializer_class = ListAccountSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):
        """
        This view should return a list of all the followers of
        the account as determined by the slug portion of the URL.
        """
        slug = self.kwargs['slug']
        try:
            user = Account.objects.get(slug=slug)
        except Account.DoesNotExist:
            return []
        return user.get_followers()


class GetFollowing(generics.ListAPIView):
    serializer_class = ListAccountSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):

        slug = self.kwargs['slug']
        try:
            user = Account.objects.get(slug=slug)
        except Account.DoesNotExist:
            return []
        return user.get_following()


class GetPosts(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):

        slug = self.kwargs['slug']
        try:
            user = Account.objects.get(slug=slug)
        except Account.DoesNotExist:
            return []
        return user.get_posts()
