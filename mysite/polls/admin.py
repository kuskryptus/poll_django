from django.contrib import admin
from .models import Choice, Question, Poll, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            "fields": ["question_text"]
        }),
        ("Date information", {
            "fields": ["pub_date"],
            "classes": ["collapse"]
        }),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ["choice"]


admin.site.register(Answer, AnswerAdmin)


class PollAdmin(admin.ModelAdmin):
    list_display = ["poll_name", "created_at"]
    inlines = [QuestionInline]


admin.site.register(Poll, PollAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["choice_text", "question"]
    inlines = [AnswerInline]


admin.site.register(Choice, ChoiceAdmin)
