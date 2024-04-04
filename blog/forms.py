from django import forms
from .models import Article, Topic

class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ArticleAdminForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['topic'].queryset = Topic.objects.filter(assigned_to=user)

