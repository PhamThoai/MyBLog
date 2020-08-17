from django.urls import path, include
from .views import (
    ImageList,
    ImageDetail
)

app_name = 'image_files'

urlpatterns = [
    path('', ImageList.as_view(), name='list-image'),
    path('<int:image_id>/', ImageDetail.as_view(), name='detail-image'),    
]