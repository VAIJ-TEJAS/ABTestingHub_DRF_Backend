import os
from django.contrib import admin
from django.conf import settings
from django.http import FileResponse
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response

from analytics.views import AnswerViewSet, QuestionViewSet
from user import views as user_views
from blog.views import ArticleCardViewSet, ArticleViewSet, CategoryViewSet
from tool.views import TestViewSet
from feedback.views import FeedbackViewSet

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
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'articles-card', ArticleCardViewSet, basename='articles-card')
router.register(r'categories', CategoryViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = [
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("auth/", user_views.Signin.as_view()),
    path('google-complete/', user_views.google_complete, name='google-complete'),
    path('admin/', admin.site.urls),
    path(".well-known/pki-validation/39C4705D1E334590C29611D2B6F46839.txt/",
        FileView.as_view(),
        name="file-view",
    ),
    path("", include(router.urls)),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
