from django.contrib import admin
from article.models import Category, Tag, Article, ArticleSection

class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 1  # Affiche 1 section vide par défaut prêt à être remplie
    fields = ('position', 'title', 'content', 'image', 'image_caption')
    ordering = ('position',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at')
    inlines = [ArticleSectionInline]  # Ajoute l'éditeur de sections ici
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'excerpt')

admin.site.register(Category)
admin.site.register(Tag)
