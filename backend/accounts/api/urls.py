from django.urls import path, include

from .views import (
    register_apiview,
    account_result,
    change_password_apiview,
    detail_user_profile_apiview,
    update_user_profile_apiview,
    update_user_avatar_apiview,
    get_followers_apiview,
    get_following_apiview,
    follow_apiview,
    unfollow_apiview,
    report_apiview
)

app_name = 'accounts'

urlpatterns = [
    path('register', register_apiview, name='register'),
    path('result', account_result, name='result'),
    path('change-password', change_password_apiview, name='change-password'),
    path('detail-profile/<str:slug>', detail_user_profile_apiview, name='detail-profile'),
    path('update-profile', update_user_profile_apiview, name='update-profile'),
    path('update-avatar', update_user_avatar_apiview, name='update-avatar'),
    path('get-followers/<str:slug>', get_followers_apiview, name='get-followers'),
    path('get-following/<str:slug>', get_following_apiview, name='get-following'),
    path('follow/<str:slug>', follow_apiview, name='follow'),
    path('unfollow/<str:slug>', unfollow_apiview, name='unfollow'),
    path('report/<str:slug>/<int:description>', report_apiview, name='report'),
]