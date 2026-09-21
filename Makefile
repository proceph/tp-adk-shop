# TP ADK — raccourcis. Tape `make` pour voir la liste.

COMPOSE := docker compose

.DEFAULT_GOAL := help

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

preflight: ## Vérifie la clé d'API et télécharge les images (à faire avant le TP)
	@test -f .env || (echo "❌ Fichier .env absent. Le créer avec : cp .env.example .env"; exit 1)
	@grep -q '^GOOGLE_API_KEY=.\+' .env \
		|| (echo "❌ GOOGLE_API_KEY est vide dans .env."; \
		    echo "   Créer une clé sur https://aistudio.google.com/apikey puis la renseigner."; exit 1)
	@echo "✅ .env renseigné"
	@$(COMPOSE) --profile mcp build
	@$(COMPOSE) pull --quiet db adminer
	@echo "✅ Images prêtes. Démarrage : make up"

up: ## Démarre la boutique (db, api, adminer, agent)
	@$(COMPOSE) up -d --build
	@echo ""
	@echo "  Agent (adk web) ... http://localhost:8000"
	@echo "  API (Swagger) ..... http://localhost:8080/docs"
	@echo "  Base (Adminer) .... http://localhost:8081   serveur=db  user=student  pass=student  base=shop"

mcp: ## Démarre en plus le serveur MCP (exercice 4)
	@$(COMPOSE) --profile mcp up -d --build mcp
	@echo "  Serveur MCP ....... http://localhost:9090/mcp"

down: ## Arrête tout (la base est conservée)
	@$(COMPOSE) --profile mcp down

logs: ## Suit les logs de l'agent
	@$(COMPOSE) logs -f agent

logs-all: ## Suit les logs de tous les services
	@$(COMPOSE) --profile mcp logs -f

restart: ## Redémarre l'agent
	@$(COMPOSE) restart agent

reset: ## Remet la base à zéro (annule les commandes créées pendant les essais)
	@$(COMPOSE) --profile mcp down -v
	@$(COMPOSE) up -d
	@echo "✅ Base réinitialisée."

shell: ## Ouvre un shell dans le conteneur agent
	@$(COMPOSE) exec agent bash

# --- Branche solution uniquement : filet de régression du corrigé. ---
# Les élèves n'ont ni ces cibles ni le dossier tests/ : la vérification du TP
# se fait en conversant avec l'agent. Ces tests servent à confirmer que le
# corrigé fonctionne toujours, après une mise à jour d'ADK par exemple.
# Le dossier tests/ est monté à la volée, le compose reste identique à main.
RUNTESTS := $(COMPOSE) run --rm --no-deps -v ./tests:/app/tests agent pytest /app/tests -q --no-header

check: ## [solution] Rejoue tous les tests du corrigé
	@$(RUNTESTS)
check1: ## [solution] Tests de l'exercice 1
	@$(RUNTESTS) -m palier1
check2: ## [solution] Tests de l'exercice 2
	@$(RUNTESTS) -m palier2
check3: ## [solution] Tests de l'exercice 3
	@$(RUNTESTS) -m palier3
check4: ## [solution] Tests de l'exercice 4
	@$(RUNTESTS) -m palier4

.PHONY: help preflight up mcp down logs logs-all restart reset shell check check1 check2 check3 check4
