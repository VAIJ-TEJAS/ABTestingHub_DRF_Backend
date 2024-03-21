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


class PreviousNextArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title"]


class ArticleCardSerializer(serializers.ModelSerializer):
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
            "popular_article",
            "featured_article",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    cover_image = CoverImageSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    content_images = ContentImageSerializer(many=True, read_only=True)
    related_articles = ArticleCardSerializer(many=True, read_only=True)
    previous_article = PreviousNextArticleSerializer(read_only=True)
    next_article = PreviousNextArticleSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "author",
            "cover_image",
            "category",
            "title",
            "short_description",
            "content",
            "published_date",
            "related_articles",
            "popular_article",
            "featured_article",
            "content_images",
            "previous_article",
            "next_article",
        ]
