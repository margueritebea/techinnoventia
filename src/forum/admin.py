from django.contrib import admin

from .models import Category, Post, Topic


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'topics_count']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'is_solution', 'is_approved']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_pinned', 'is_locked', 'is_approved', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_locked', 'is_approved']
    search_fields = ['title', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostInline]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'topic', 'author', 'is_solution', 'is_approved', 'created_at']
    list_filter = ['is_solution', 'is_approved']
    search_fields = ['content', 'author__username']
