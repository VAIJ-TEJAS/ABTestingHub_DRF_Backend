from django.db import models
from ckeditor.fields import RichTextField


class Author(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="author_pictures/")

    def __str__(self):
        return self.name


class CoverImage(models.Model):
    image = models.ImageField(upload_to="cover_images/")

    def __str__(self):
        return f"Cover Image {self.id}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Blog(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover_image = models.ForeignKey(CoverImage, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255)
    content = RichTextField()
    published_date = models.DateTimeField(auto_now_add=True)
    similar_blogs = models.ManyToManyField('self', blank=True, related_name='related_similar_blogs')

    def __str__(self):
        return self.title


class ContentImage(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="content_images/")

    def __str__(self):
        return f"Content Image {self.id} for Blog {self.blog.id}"
