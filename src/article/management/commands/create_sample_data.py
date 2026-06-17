"""
Commande Django pour créer des données de démonstration
Usage: python manage.py create_sample_data
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from article.models import Article, ArticleSection, Category, Comment, Tag

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer des données de démonstration pour TechInnoventia'

    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données de démonstration...')

        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@techinnoventia.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Utilisateur demo créé'))

        categories_data = [
            {'name': 'Programmation'},
            {'name': 'Technologie'},
            {'name': 'Intelligence Artificielle'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
            )
            categories[cat_data['name']] = cat
        self.stdout.write(self.style.SUCCESS(f'{len(categories)} catégories créées'))

        tags_data = ['Python', 'JavaScript', 'Django', 'React', 'Machine Learning', 'Web Dev']
        tags = {}
        for name in tags_data:
            tag, created = Tag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write(self.style.SUCCESS(f'{len(tags)} tags créés'))

        articles_data = [
            {
                'title': 'Introduction complète à Django et HTMX',
                'excerpt': 'Django et HTMX forment un duo puissant pour créer des applications web modernes et réactives sans écrire trop de JavaScript.',
                'category': categories['Programmation'],
                'tags': ['Django', 'Python', 'Web Dev'],
                'sections': [
                    {
                        'title': 'Qu\'est-ce que HTMX ?',
                        'content': 'HTMX est une bibliothèque JavaScript légère qui permet d\'accéder aux fonctionnalités AJAX, CSS Transitions, WebSockets et Server Sent Events directement en HTML. Avec HTMX, vous pouvez créer des interfaces utilisateur dynamiques sans écrire de JavaScript complexe.',
                        'position': 1,
                    },
                    {
                        'title': 'Pourquoi Django + HTMX ?',
                        'content': '- Développement plus rapide\n- Moins de code JavaScript\n- Meilleure maintenabilité\n- SEO-friendly',
                        'position': 2,
                    },
                    {
                        'title': 'Exemple pratique',
                        'content': '<button hx-post="/like" hx-swap="outerHTML">Like</button>\n\nCette simple ligne permet d\'envoyer une requête POST sans recharger la page !',
                        'position': 3,
                    },
                ],
            },
            {
                'title': 'Les fondamentaux du Machine Learning',
                'excerpt': 'Le Machine Learning est une branche de l\'intelligence artificielle qui permet aux ordinateurs d\'apprendre sans être explicitement programmés.',
                'category': categories['Intelligence Artificielle'],
                'tags': ['Machine Learning', 'Python'],
                'sections': [
                    {
                        'title': 'Types d\'apprentissage',
                        'content': '1. Supervisé : apprentissage avec des données étiquetées\n2. Non supervisé : découverte de patterns dans des données non étiquetées\n3. Par renforcement : apprentissage par essai-erreur',
                        'position': 1,
                    },
                    {
                        'title': 'Applications pratiques',
                        'content': 'Le ML est utilisé dans de nombreux domaines :\n- Reconnaissance d\'images\n- Traitement du langage naturel\n- Véhicules autonomes\n- Recommandations personnalisées',
                        'position': 2,
                    },
                ],
            },
            {
                'title': 'Maîtriser React en 2025',
                'excerpt': 'React reste la bibliothèque JavaScript la plus populaire pour créer des interfaces utilisateur modernes et performantes.',
                'category': categories['Technologie'],
                'tags': ['React', 'JavaScript', 'Web Dev'],
                'sections': [
                    {
                        'title': 'Les nouveautés de React',
                        'content': 'React Server Components, Suspense amélioré, et bien plus encore transforment la façon dont nous développons des applications web.',
                        'position': 1,
                    },
                    {
                        'title': 'Bonnes pratiques',
                        'content': '- Utiliser les hooks personnalisés\n- Optimiser les re-renders\n- Structurer correctement vos composants\n- Tester votre code',
                        'position': 2,
                    },
                ],
            },
        ]

        created_count = 0
        for article_data in articles_data:
            sections_data = article_data.pop('sections')
            tag_names = article_data.pop('tags')

            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    **article_data,
                    'author': user,
                    'status': 'published',
                    'published_at': timezone.now(),
                },
            )

            if created:
                for tag_name in tag_names:
                    article.tags.add(tags[tag_name])

                for section_data in sections_data:
                    ArticleSection.objects.create(
                        article=article,
                        **section_data,
                    )

                Comment.objects.create(
                    article=article,
                    author=user,
                    content=f"Excellent article sur {article.title} ! Très instructif et bien détaillé.",
                )

                article.likes.add(user)

                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_count} articles créés avec sections'))
        self.stdout.write(self.style.SUCCESS('Données de démonstration créées avec succès !'))
        self.stdout.write(self.style.WARNING('Utilisateur : demo_user | Mot de passe : demo123'))
