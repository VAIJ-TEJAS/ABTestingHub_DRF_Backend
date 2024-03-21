"""abtesting_drf_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import os
from django.contrib import admin
from django.conf import settings
from django.http import FileResponse
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response

from user import views as user_views
from blog.views import BlogViewSet, CategoryViewSet
from tool.views import TestViewSet

class FileView(APIView):
    def get(self, request):
        file_path = "39C4705D1E334590C29611D2B6F46839.txt"
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if os.path.exists(file_path):
            file = open(file_path, "rb")
            response = FileResponse(file)
            return response
        else:
            return Response({"error": "File not found"}, status=404)


router = DefaultRouter()
router.register(r'signup', user_views.Signup)
router.register(r'articles', BlogViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tests', TestViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
    path("auth/", user_views.Signin.as_view()),
    path(
        ".well-known/pki-validation/39C4705D1E334590C29611D2B6F46839.txt/",
        FileView.as_view(),
        name="file-view",
    ),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
