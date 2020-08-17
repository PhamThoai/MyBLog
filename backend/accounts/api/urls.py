from django.urls import path, include

from .views import (
    register_apiview,
    account_result,
    change_password_apiview,
    detail_user_profile_apiview,
    update_user_profile_apiview,
    update_user_avatar_apiview,
    GetFollowers,
    GetFollowing,
    GetPosts,
    follow_user_apiview,
    unfollow_user_apiview,
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
    path('get-followers/<str:slug>', GetFollowers.as_view(), name='get-followers'),
    path('get-following/<str:slug>', GetFollowing.as_view(), name='get-following'),
    path('get-posts/<str:slug>', GetPosts.as_view(), name='get-post'),
    path('follow/<str:slug>', follow_user_apiview, name='follow'),
    path('unfollow/<str:slug>', unfollow_user_apiview, name='unfollow'),
    path('report/<str:slug>/<int:description>', report_apiview, name='report'),
]