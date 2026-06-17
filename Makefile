# Makefile pour le projet Django Tech Innoventia
# Variables
PYTHON_CMD = python3
VENV = .venv
MANAGE = $(VENV)/bin/python src/manage.py

# ============================================================================
# ENVIRONNEMENT DE DÉVELOPPEMENT
# ============================================================================

# Installation initiale du projet
setup:
	$(PYTHON_CMD) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

# Lancer le serveur de développement
run:
	$(MANAGE) runserver 8080 --settings=config.dev_settings 

# Appliquer les migrations (dev)
migrate:
	$(MANAGE) migrate --settings=config.dev_settings

# Créer les fichiers de migration (dev)
migrations:
	$(MANAGE) makemigrations --settings=config.dev_settings

# Créer un superutilisateur (dev)
createsuperuser:
	$(MANAGE) createsuperuser --settings=config.dev_settings

# Lancer les tests (dev)
test:
	$(VENV)/bin/python -m unittest discover tests --settings=config.dev_settings

# Ouvrir le shell Django (dev)
shell:
	$(MANAGE) shell --settings=config.dev_settings

# ============================================================================
# ENVIRONNEMENT DE PRODUCTION
# ============================================================================
migrate-prod:
	$(MANAGE) migrate --settings=config.settings

migrations-prod:
	$(MANAGE) makemigrations --settings=config.settings

# Collecter les fichiers statiques (production)
collectstatic:
	$(MANAGE) collectstatic --noinput --settings=config.settings

# Créer un superutilisateur (production)
createsuperuser-prod:
	$(MANAGE) createsuperuser --settings=config.settings

# Vérifier la configuration de production
check-prod:
	$(MANAGE) check --deploy --settings=config.settings

# Ouvrir le shell Django (production)
shell-prod:
	$(MANAGE) shell --settings=config.settings

# ============================================================================
# GESTION DES DÉPENDANCES
# ============================================================================

# Sauvegarder les dépendances
freeze:
	$(VENV)/bin/pip freeze > requirements.txt

# Installer/mettre à jour les dépendances
install:
	$(VENV)/bin/pip install -r requirements.txt

# Mettre à jour pip
update-pip:
	$(VENV)/bin/pip install --upgrade pip

# ============================================================================
# NETTOYAGE
# ============================================================================

# Nettoyer les fichiers Python compilés et cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Supprimer l'environnement virtuel
clean-venv:
	rm -rf $(VENV)

# Nettoyage complet (cache + venv)
clean-all: clean clean-venv

# ============================================================================
# DÉVELOPPEMENT
# ============================================================================
startapp:
	@read -p "Nom de la nouvelle app: " app_name; \
	$(MANAGE) startapp $$app_name --settings=config.dev_settings

# Créer un fichier .env à partir de .env.example
env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo " Fichier .env créé ! N'oubliez pas de le remplir avec vos valeurs."; \
	else \
		echo " Le fichier .env existe déjà."; \
	fi

# ============================================================================
# BASE DE DONNÉES
# ============================================================================
# Réinitialiser la base de données (dev) -  DANGER : supprime toutes les données !
reset-db:
	@echo " Cette commande va SUPPRIMER toutes les données !"
	@read -p "Voulez-vous continuer ? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f src/db.sqlite3; \
		$(MANAGE) migrate --settings=config.dev_settings; \
		echo " Base de données réinitialisée !"; \
	else \
		echo " Opération annulée."; \
	fi

# Créer une sauvegarde de la base de données
backup-db:
	@mkdir -p backups
	@cp src/db.sqlite3 backups/db_backup_$$(date +%Y%m%d_%H%M%S).sqlite3
	@echo " Sauvegarde créée dans backups/"

# ============================================================================
# QUALITÉ DU CODE
# ============================================================================

# Linter + formater le code avec ruff
lint:
	$(VENV)/bin/ruff check src/

format:
	$(VENV)/bin/ruff format src/

check: lint
	$(VENV)/bin/ruff check --fix src/

# ============================================================================
# AIDE
# ============================================================================

# Afficher l'aide
help:
	@echo "📚 Commandes disponibles:"
	@echo ""
	@echo "🔧 ENVIRONNEMENT DE DÉVELOPPEMENT"
	@echo "  make setup              - Créer l'environnement virtuel et installer les dépendances"
	@echo "  make run                - Lancer le serveur de développement"
	@echo "  make migrate            - Appliquer les migrations (dev)"
	@echo "  make migrations         - Créer les migrations (dev)"
	@echo "  make createsuperuser    - Créer un superutilisateur (dev)"
	@echo "  make shell              - Ouvrir le shell Django (dev)"
	@echo "  make test               - Lancer les tests"
	@echo ""
	@echo "🚀 ENVIRONNEMENT DE PRODUCTION"
	@echo "  make migrate-prod       - Appliquer les migrations (production)"
	@echo "  make migrations-prod    - Créer les migrations (production)"
	@echo "  make collectstatic      - Collecter les fichiers statiques"
	@echo "  make createsuperuser-prod - Créer un superutilisateur (production)"
	@echo "  make check-prod         - Vérifier la configuration de production"
	@echo "  make shell-prod         - Ouvrir le shell Django (production)"
	@echo ""
	@echo "📦 DÉPENDANCES"
	@echo "  make freeze             - Sauvegarder les dépendances"
	@echo "  make install            - Installer les dépendances"
	@echo "  make update-pip         - Mettre à jour pip"
	@echo ""
	@echo "🧹 NETTOYAGE"
	@echo "  make clean              - Nettoyer les fichiers cache"
	@echo "  make clean-venv         - Supprimer l'environnement virtuel"
	@echo "  make clean-all          - Nettoyage complet"
	@echo ""
	@echo "🗄️  BASE DE DONNÉES"
	@echo "  make reset-db           - Réinitialiser la DB ( supprime les données)"
	@echo "  make backup-db          - Créer une sauvegarde de la DB"
	@echo ""
	@echo " AUTRES"
	@echo "  make env                - Créer le fichier .env"
	@echo "  make format             - Formater le code avec black"
	@echo "  make lint               - Linter avec flake8"

# Par défaut, afficher l'aide
.DEFAULT_GOAL := help

# Déclarer les cibles phony (qui ne correspondent pas à des fichiers)
.PHONY: setup run migrate migrations createsuperuser test shell \
        migrate-prod migrations-prod collectstatic createsuperuser-prod check-prod shell-prod \
        freeze install update-pip clean clean-venv clean-all \
        reset-db backup-db format lint env help
