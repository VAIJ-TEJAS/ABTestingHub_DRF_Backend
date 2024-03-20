from rest_framework import serializers
from .models import Author, CoverImage, Category, Article, ContentImage


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "role", "picture"]


class CoverImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverImage
        fields = ["id", "image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = ["id", "blog", "image"]


class RelatedArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    cover_image = CoverImageSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "author",
            "cover_image",
            "category",
            "title",
            "short_description",
            "published_date",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    cover_image = CoverImageSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    content_images = ContentImageSerializer(
        many=True, read_only=True, source="contentimage_set"
    )
    related_articles = RelatedArticleSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "author",
            "cover_image",
            "category",
            "popular_article",
            "featured_article",
            "title",
            "short_description",
            "content",
            "published_date",
            "content_images",
            "related_articles",
        ]
