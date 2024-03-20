from django.contrib import admin
from .models import Author, CoverImage, Category, Blog, ContentImage

admin.site.register(Author)
admin.site.register(CoverImage)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(ContentImage)
