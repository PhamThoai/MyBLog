from django.urls import path, include

from .views import (
    CreatePost,
    ListPost,
    DetailPost,
    ListPostNeedPublish,
    ListCommentsOfPost,
    publish_post

    
)

app_name = 'posts'

urlpatterns = [
    path('', CreatePost.as_view(), name='create'),
    path('get-posts', ListPost.as_view(), name='list'),
    path('get-need-publish', ListPostNeedPublish.as_view(), name='need-publish'),
    path('publish-posts', publish_post, name='publish'),
    path('get-comments/<str:slug>', ListCommentsOfPost.as_view(), name='list-comments'),
    # Note <str:slug> will match all strings
    # so it must be put at the very end
    path('<str:slug>', DetailPost.as_view(), name='detail'), 
    
]