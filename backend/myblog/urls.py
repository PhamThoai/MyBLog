"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework_social_oauth2.urls')),

    path('api/users/', include("accounts.api.urls", namespace='accounts-api')),
    path('api/posts/', include("posts.api.urls", namespace='posts-api')),
    path('api/comments/', include("comments.api.urls", namespace='comments-api')),
    path('api/tags/', include("tags.api.urls", namespace='tags-api')),
    path('api/images/', include("image_files.api.urls", namespace='image_files-api')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
