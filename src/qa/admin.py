from django.contrib import admin

from .models import Answer, QATag, Question


@admin.register(QATag)
class QATagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'is_accepted', 'is_approved']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_resolved', 'is_approved', 'vote_score', 'created_at']
    list_filter = ['is_resolved', 'is_approved', 'tags']
    search_fields = ['title', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'question', 'author', 'is_accepted', 'is_approved', 'created_at']
    list_filter = ['is_accepted', 'is_approved']
    search_fields = ['content', 'author__username']
