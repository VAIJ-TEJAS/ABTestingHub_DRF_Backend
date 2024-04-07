from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=100)

    def __str__(self):
        return self.choice_text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)  
    text_answer = models.TextField("Text Answer", blank=True, null=True)  

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        if self.choice:
            return f"{username} - {self.choice.choice_text}"
        return f"{username} - {self.text_answer}"