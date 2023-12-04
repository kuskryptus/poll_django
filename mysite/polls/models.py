from django.db import models
from django.utils import timezone
from django.contrib import admin

import datetime


class Poll(models.Model):
    poll_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    indexes = [
        models.Index(fields=["create_at","poll_name"]),
    ]

    def __str__(self):
        return self.poll_name


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.question_text

    indexes = [
        models.Index(fields=["pub_date","question_text"]),
    ]

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=250)
    selected = models.BooleanField(default=False)

    indexes = [
        models.Index(fields=["choice_text"]),
    ]

    def __str__(self):
        return self.choice_text

    def selected_true(self):
        self.selected = True
        self.save()
        return self

    def selected_false(self):
        self.selected = False
        self.save()
        return self


class Answer(models.Model):
    choice = models.ForeignKey("Choice", models.ForeignKey, related_name="answers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "created_at"

    indexes = [
        models.Index(fields=["created_at"]),
    ]

    def __str__(self):
        return f"{self.choice}"
