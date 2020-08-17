from django.urls import path, include

from .views import (
    CommentAPIView
)

app_name = 'comments'

urlpatterns = [
    path('', CommentAPIView.as_view(), name='detail'),
]