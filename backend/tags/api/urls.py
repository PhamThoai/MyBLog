from django.urls import path, include

from .views import (
    ListTags,
    CreateTag,
    TagDetail,
    ListPostOfTags
)

app_name = 'accounts'

urlpatterns = [
    path('', ListTags.as_view(), name='list-tags'),
    path('create', CreateTag, name='create-tag'),
    path('<str:slug>', TagDetail.as_view(), name='detail-tag'),
    path('posts/<str:slug>', ListPostOfTags.as_view(), name='list-post-of-tag'),
]