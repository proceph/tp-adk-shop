# TP ADK — raccourcis. Tape `make` pour voir la liste.

COMPOSE := docker compose
PYTEST  := $(COMPOSE) exec -T agent pytest /app/tests -q --no-header

.DEFAULT_GOAL := help

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

preflight: ## À FAIRE AVANT LE TP : vérifie ta clé et télécharge les images
	@test -f .env || (echo "❌ Pas de fichier .env. Fais : cp .env.example .env"; exit 1)
	@grep -q '^GOOGLE_API_KEY=.\+' .env \
		|| (echo "❌ GOOGLE_API_KEY est vide dans .env."; \
		    echo "   Crée une clé sur https://aistudio.google.com/apikey puis renseigne-la."; exit 1)
	@echo "✅ .env renseigné"
	@$(COMPOSE) --profile mcp build
	@$(COMPOSE) pull --quiet db adminer
	@echo "✅ Images prêtes. Tu peux faire : make up"

up: ## Démarre la boutique (db, api, adminer, agent)
	@$(COMPOSE) up -d --build
	@echo ""
	@echo "  Agent (adk web) ... http://localhost:8000"
	@echo "  API (Swagger) ..... http://localhost:8080/docs"
	@echo "  Base (Adminer) .... http://localhost:8081   serveur=db  user=student  pass=student  base=shop"

mcp: ## Démarre en plus le serveur MCP (palier 4)
	@$(COMPOSE) --profile mcp up -d --build mcp
	@echo "  Serveur MCP ....... http://localhost:9090/mcp"

down: ## Arrête tout (la base est conservée)
	@$(COMPOSE) --profile mcp down

logs: ## Suit les logs de l'agent
	@$(COMPOSE) logs -f agent

logs-all: ## Suit les logs de tous les services
	@$(COMPOSE) --profile mcp logs -f

restart: ## Redémarre l'agent (si adk web s'emmêle les pinceaux)
	@$(COMPOSE) restart agent

reset: ## Remet la base à zéro (annule toutes les commandes créées)
	@$(COMPOSE) --profile mcp down -v
	@$(COMPOSE) up -d
	@echo "✅ Base réinitialisée."

shell: ## Ouvre un shell dans le conteneur agent
	@$(COMPOSE) exec agent bash

check: ## Lance TOUS les tests
	@$(PYTEST)
check1: ## Teste le palier 1 (catalogue via l'API)
	@$(PYTEST) -m palier1
check2: ## Teste le palier 2 (stock et avis via SQL)
	@$(PYTEST) -m palier2
check3: ## Teste le palier 3 (commandes)
	@$(PYTEST) -m palier3
check4: ## Teste le palier 4 (serveur MCP)
	@$(PYTEST) -m palier4

.PHONY: help preflight up mcp down logs logs-all restart reset shell check check1 check2 check3 check4
