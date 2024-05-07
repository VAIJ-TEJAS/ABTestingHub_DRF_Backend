from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _

class Topic(models.Model):
    class TopicStatus(models.TextChoices):
        NONE = 'None', _('None')
        WORKING_OUT = 'Working Out', _('Working Out')
        SENT_FOR_REVIEW = 'Sent for Review', _('Sent for Review')
        CHANGES_REQUIRED = 'Changes Required', _('Changes Required')
        POSTED = 'Posted', _('Posted')

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,choices=TopicStatus.choices,default=TopicStatus.NONE)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True},
        related_name='assigned_topics'
    )

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="author_pictures/")

    def __str__(self):
        return self.name


class CoverImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="cover_images/")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_cover_images')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):

    class ArticleStatus(models.TextChoices):
        DRAFT = "DR", _("Draft")
        PUBLISHED = "PB", _("Published")
        ARCHIVED = "AR", _("Archived")

    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,null=True,blank=True,related_name='articles')
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image = models.ForeignKey(CoverImage, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255)
    content = RichTextField()
    published_date = models.DateTimeField(auto_now_add=True)
    related_articles = models.ManyToManyField("self", blank=True)
    popular_article = models.BooleanField(default=False)
    featured_article = models.BooleanField(default=False)
    previous_article = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name='article_previous'
    )
    next_article = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name='article_next'
    )
    status = models.CharField(
        max_length=2, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT
    )
    team_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class ContentImage(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="content_images/")

    def __str__(self):
        return f"Content Image {self.name} for Blog {self.article.id}"
