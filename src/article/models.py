from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    )

    # Méta-données de l'article (Le conteneur)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True)

    # L'intro est importante pour le SEO et les cartes sur l'accueil
    excerpt = models.TextField(max_length=500, help_text="Un résumé accrocheur affiché sur la page d'accueil.")
    cover = models.ImageField(upload_to='articles/covers/%Y/%m/', blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_trending = models.BooleanField(default=False)

    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def read_time(self):
        # Calcul du temps de lecture basé sur toutes les sections
        total_words = 0
        for section in self.sections.all():
            total_words += len(section.content.split())
        minutes = total_words // 200
        return minutes if minutes > 0 else 1

    @property
    def comments_count(self):
        """Nombre de commentaires principaux (sans les réponses)"""
        return self.comments.filter(is_approved=True, parent__isnull=True).count()

    @property
    def all_comments_count(self):
        """Nombre total de commentaires (avec réponses)"""
        return self.comments.filter(is_approved=True).count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(id=user.id).exists()
        return False

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ArticleSection(models.Model):
    """
    Une section modulaire de l'article.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sections')

    # Position pour ordonner les sections (1, 2, 3...)
    position = models.PositiveIntegerField(default=0)

    title = models.CharField(max_length=200, blank=True, null=True, help_text="Titre optionnel de la section (h2)")
    content = models.TextField(help_text="Le contenu textuel de cette section.")
    image = models.ImageField(upload_to='articles/sections/%Y/%m/', blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True, null=True, help_text="Légende de l'image")

    class Meta:
        ordering = ['position']  # Trie automatiquement par position
        verbose_name = "Section d'article"
        verbose_name_plural = "Sections d'article"

    def __str__(self):
        return f"Section {self.position} - {self.article.title}"


class Comment(models.Model):
    """
    Modèle pour les commentaires d'articles avec support des réponses
    """
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies',
        help_text="Pour les réponses aux commentaires"
    )
    
    content = models.TextField(
        max_length=1000,
        help_text="Contenu du commentaire"
    )
    
    # Modération
    is_approved = models.BooleanField(
        default=True,
        help_text="Commentaire approuvé par un modérateur"
    )
    is_edited = models.BooleanField(
        default=False,
        help_text="Commentaire modifié"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Likes sur les commentaires (optionnel)
    likes = models.ManyToManyField(
        User, 
        related_name='liked_comments', 
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['article', '-created_at']),
        ]
    
    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.article.title}"
    
    @property
    def likes_count(self):
        """Nombre de likes sur le commentaire"""
        return self.likes.count()
    
    @property
    def replies_count(self):
        """Nombre de réponses à ce commentaire"""
        return self.replies.filter(is_approved=True).count()
    
    def is_reply(self):
        """Vérifie si c'est une réponse à un autre commentaire"""
        return self.parent is not None
    
    def get_replies(self):
        """Retourne les réponses approuvées à ce commentaire"""
        return self.replies.filter(is_approved=True).select_related('author')
# from django.db import models
# from django.contrib.auth import get_user_model
# from django.utils.text import slugify

# User = get_user_model()

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)
#     class Meta:
#         verbose_name_plural = "Categories"
#     def __str__(self):
#         return self.name
        

# class Tag(models.Model):
#     name = models.CharField(max_length=50)
#     slug = models.SlugField(unique=True)
#     def __str__(self):
#         return self.name

# class Article(models.Model):
#     STATUS_CHOICES = (
#         ('draft', 'Brouillon'),
#         ('published', 'Publié'),
#     )

#     # Méta-données de l'article (Le conteneur)
#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True, max_length=255)
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
#     tags = models.ManyToManyField(Tag, blank=True)

#     # L'intro est importante pour le SEO et les cartes sur l'accueil
#     excerpt = models.TextField(max_length=500, help_text="Un résumé accrocheur affiché sur la page d'accueil.")
#     cover = models.ImageField(upload_to='articles/covers/%Y/%m/', blank=True, null=True)

#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
#     is_trending = models.BooleanField(default=False)

#     likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     published_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         ordering = ['-published_at']

#     def __str__(self):
#         return self.title

#     @property
#     def likes_count(self):
#         return self.likes.count()

#     @property
#     def read_time(self):
#         # Calcul du temps de lecture basé sur toutes les sections
#         total_words = 0
#         for section in self.sections.all():
#             total_words += len(section.content.split())
#         minutes = total_words // 200
#         return minutes if minutes > 0 else 1

#     def is_liked_by(self, user):
#         if user.is_authenticated:
#             return self.likes.filter(id=user.id).exists()
#         return False

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         super().save(*args, **kwargs)


# class ArticleSection(models.Model):
#     """
#     Une section modulaire de l'article.
#     """
#     article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sections')

#     # Position pour ordonner les sections (1, 2, 3...)
#     position = models.PositiveIntegerField(default=0)

#     title = models.CharField(max_length=200, blank=True, null=True, help_text="Titre optionnel de la section (h2)")
#     content = models.TextField(help_text="Le contenu textuel de cette section.")
#     image = models.ImageField(upload_to='articles/sections/%Y/%m/', blank=True, null=True)
#     image_caption = models.CharField(max_length=200, blank=True, null=True, help_text="Légende de l'image")

#     class Meta:
#         ordering = ['position'] # Trie automatiquement par position
#         verbose_name = "Section d'article"
#         verbose_name_plural = "Sections d'article"

#     def __str__(self):
#         return f"Section {self.position} - {self.article.title}"
