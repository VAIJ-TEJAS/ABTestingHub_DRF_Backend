from django.contrib import admin
from .models import Author, CoverImage, Category, Article, ContentImage

admin.site.register(Author)
admin.site.register(CoverImage)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(ContentImage)
