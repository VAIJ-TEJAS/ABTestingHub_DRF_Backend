from django.contrib import admin
from .forms import ArticleAdminForm
from .models import Topic, Author, CoverImage, Category, Article, ContentImage


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(topic__assigned_to=request.user)

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(ArticleAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            self.exclude = ["popular_article", "featured_article", "status"]
        else:
            self.exclude = []
        return AdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "topic":
            used_topics = Article.objects.exclude(topic__isnull=True).values_list(
                "topic", flat=True
            )
            kwargs["queryset"] = Topic.objects.exclude(id__in=used_topics)
        if db_field.name == "cover_image" and not request.user.is_superuser:
            kwargs["queryset"] = CoverImage.objects.filter(created_by=request.user)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CoverImageAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CoverImageAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields.pop("created_by", None)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)
admin.site.register(CoverImage, CoverImageAdmin)
admin.site.register(Topic)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(ContentImage)
