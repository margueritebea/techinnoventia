# 🚀 Guide de démarrage rapide - TechInnoventia

## Installation en 5 minutes

### 1️⃣ Préparer l'environnement

```bash
# Vous êtes déjà dans le projet
cd ~/space_work/tech_innoventia

# Activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Installer les dépendances (avec TinyMCE)

```bash
pip install -r requirements.txt
```

### 3️⃣ Créer les dossiers nécessaires

```bash
mkdir -p src/templates/includes
mkdir -p src/templates/article/partials
mkdir -p src/article/management/commands
mkdir -p src/media/articles
touch src/article/management/__init__.py
touch src/article/management/commands/__init__.py
```

### 4️⃣ Appliquer vos models existants

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 6️⃣ Créer des données de démo

```bash
python manage.py create_sample_data
```

✅ Cela va créer :
- Catégories (Programmation, Technologies, Mathématiques, IA)
- Topics (Python, Django, React, ML, etc.)
- 3 Articles complets avec sections
- Commentaires et réactions
- Utilisateur demo : `demo_user` / `demo123` (staff)

### 7️⃣ Lancer le serveur

```bash
python manage.py runserver
```

### 8️⃣ Accéder au site

- **Site web** : http://localhost:8000
- **Admin Django** : http://localhost:8000/admin
- **Articles** : http://localhost:8000/articles/

---

## ✨ Créer votre premier article (via Admin)

1. Connectez-vous à l'admin avec votre superuser
2. **Articles** → **Ajouter un article**
3. Remplissez :
   - **Titre** : "Mon premier article"
   - **Topics** : Sélectionnez un ou plusieurs
   - **Introduction** : Utilisez TinyMCE pour formater
   - **Image** : Optionnel
   - **Est publié** : ✅ Coché
4. Scroll down vers **Article sections** (inline)
5. Ajoutez des sections :
   - **Order** : 1, 2, 3...
   - **Subtitle** : Titre de la section
   - **Content** : Contenu riche avec TinyMCE
   - **Status** : approved
6. **Enregistrer**

---

## 🎨 TinyMCE - Fonctionnalités

L'éditeur TinyMCE vous permet :
- ✅ Formatage riche (gras, italique, listes)
- ✅ Insertion de code avec coloration syntaxique
- ✅ Liens et images
- ✅ Tableaux
- ✅ Mode source (HTML)

Pour insérer du code :
1. Cliquez sur le bouton `</>` dans la toolbar
2. Sélectionnez le langage (Python, JavaScript, etc.)
3. Collez votre code

---

## 🧪 Tester les fonctionnalités

### Articles
- ✅ Liste avec filtres (Topics, Categories, Tri)
- ✅ Recherche en temps réel (HTMX)
- ✅ Pagination

### Détail d'article
- ✅ Sections numérotées
- ✅ Réactions (Like 👍 / Dislike 👎)
- ✅ Commentaires avec réponses (2 niveaux)
- ✅ Partage social

### Interactions
- Connectez-vous pour :
  - Réagir aux articles
  - Commenter
  - Répondre aux commentaires
  - Supprimer vos commentaires

---

## 📁 Structure de votre projet

```
src/
├── article/
│   ├── models.py          ✅ VOS models (Category, Topic, Article, etc.)
│   ├── views.py           ✅ Vues complètes
│   ├── urls.py            ✅ URLs
│   ├── admin.py           ✅ Admin avec TinyMCE
│   └── management/
│       └── commands/
│           └── create_sample_data.py
├── templates/
│   ├── base.html
│   ├── includes/
│   │   ├── header.html
│   │   └── footer.html
│   ├── home/
│   │   └── index.html
│   └── article/
│       ├── articles_list.html
│       ├── article_detail.html
│       ├── card.html
│       └── partials/
│           ├── article_grid.html
│           ├── reaction_buttons.html
│           └── comment_item.html
└── config/
    ├── settings.py        ✅ Config TinyMCE
    └── urls.py            ✅ URLs avec TinyMCE
```

---

## 🔧 Commandes utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Shell Django
python manage.py shell

# Collecter les fichiers statiques (production)
python manage.py collectstatic
```

---

## 🎯 Prochaines étapes

1. **Personnaliser le design**
   - Modifier les couleurs dans les templates
   - Ajouter votre logo

2. **Créer du contenu**
   - Ajouter des catégories personnalisées
   - Créer des topics spécifiques
   - Publier vos articles

3. **Configurer l'authentification**
   - Personnaliser les templates allauth
   - Ajouter l'authentification sociale (optionnel)

4. **Déploiement**
   - Configurer PostgreSQL
   - Setup Gunicorn + Nginx
   - Configurer les variables d'environnement

---

**Bon développement ! 🚀**

Questions ? Consultez le README.md ou la documentation Django. Des tags et commentaires

### 7️⃣ Lancer le serveur

```bash
python manage.py runserver
# ou depuis la racine : make run
```

### 8️⃣ Accéder au site

- **Site web** : http://localhost:8000
- **Admin Django** : http://localhost:8000/admin
- **Articles** : http://localhost:8000/articles/

---

## 📝 Configuration de base

### Créer votre fichier `.env`

Créez un fichier `.env` à la racine du projet :

```env
SECRET_KEY=django-insecure-votre-cle-secrete-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Structure des fichiers à copier

Assurez-vous d'avoir copié tous les templates dans les bons emplacements :

```
src/templates/
├── base.html
├── includes/
│   ├── header.html
│   └── footer.html
├── home/
│   └── index.html
└── article/
    ├── list.html
    ├── detail.html
    ├── card.html
    ├── comment.html
    └── partials/
        ├── article_grid.html
        ├── like_button.html
        └── comment_like_button.html
```

---

## ✨ Premiers pas

### 1. Créer votre premier article via l'admin

1. Connectez-vous à l'admin : http://localhost:8000/admin
2. Allez dans **Articles** → **Ajouter un article**
3. Remplissez :
   - **Titre** : "Mon premier article"
   - **Catégorie** : Choisissez une catégorie
   - **Contenu** : Votre contenu (HTML supporté)
   - **Est publié** : ✅ Coché
4. Cliquez sur **Enregistrer**

### 2. Tester les fonctionnalités

- ✅ **Recherche** : Utilisez la barre de recherche sur `/articles/`
- ✅ **Filtres** : Filtrez par catégorie et tri
- ✅ **Likes** : Connectez-vous et likez un article
- ✅ **Commentaires** : Ajoutez un commentaire sur un article
- ✅ **Responsive** : Testez sur mobile (F12 → mode responsive)

---

## 🛠️ Commandes utiles

```bash
# Depuis la racine du projet
make help              # Voir toutes les commandes
make run               # Lancer le serveur
make shell             # Ouvrir le shell Django
make test              # Exécuter les tests
make clean             # Nettoyer les fichiers temporaires

# Depuis src/
python manage.py makemigrations    # Créer des migrations
python manage.py migrate           # Appliquer les migrations
python manage.py createsuperuser   # Créer un admin
python manage.py collectstatic     # Collecter les fichiers statiques
```

---

## 🎨 Personnalisation

### Modifier les couleurs (Tailwind)

Dans `base.html`, ajoutez votre configuration Tailwind :

```html
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          primary: '#267ad4',
          secondary: '#6c63ff',
        }
      }
    }
  }
</script>
```

### Ajouter votre logo

1. Placez votre logo dans `src/static/images/logo.png`
2. Modifiez `includes/header.html` :

```html
<h1 class="text-xl sm:text-2xl font-bold">
  <a href="{% url 'home:index' %}" class="flex items-center gap-2">
    <img src="{% static 'images/logo.png' %}" alt="Logo" class="h-8">
    TechInnoventia
  </a>
</h1>
```

---

## 🐛 Dépannage

### Erreur "No module named 'article'"

```bash
# Vérifiez que vous êtes dans le bon dossier
cd src
python manage.py runserver
```

### Erreur "Table doesn't exist"

```bash
# Réappliquez les migrations
python manage.py migrate --run-syncdb
```

### Les fichiers statiques ne se chargent pas

```bash
# En développement, c'est normal si DEBUG=True
# Vérifiez dans settings.py :
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### HTMX ne fonctionne pas

Vérifiez que le script est bien chargé dans `base.html` :
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

---

## 📚 Ressources

- **Documentation Django** : https://docs.djangoproject.com/
- **Documentation HTMX** : https://htmx.org/docs/
- **Documentation Alpine.js** : https://alpinejs.dev/
- **Documentation Tailwind CSS** : https://tailwindcss.com/docs

---

## 🎯 Prochaines étapes

1. **Enrichir le profil utilisateur**
   - Ajouter une bio, avatar, réseaux sociaux
   
2. **Implémenter le forum**
   - Créer les modèles Topic et Reply
   - Ajouter les vues et templates

3. **Ajouter des notifications**
   - Notifier lors d'un nouveau commentaire
   - Notifier lors d'un like

4. **Améliorer l'éditeur**
   - Intégrer un éditeur Markdown (SimpleMDE)
   - Prévisualisation en temps réel

5. **SEO et performance**
   - Ajouter des meta tags
   - Optimiser les images
   - Mettre en cache

---

## 💡 Conseils

- **Git** : Committez régulièrement vos changements
- **Tests** : Écrivez des tests pour vos nouvelles fonctionnalités
- **Documentation** : Documentez votre code
- **Sécurité** : Ne commitez JAMAIS votre `.env` ou `SECRET_KEY`

---