# TP — Connecter un agent ADK à un système existant

**Durée : 3 h 30 · 5 exercices · Python · Agent Development Kit (ADK) 2.9**

## Objectif

Apprendre à connecter un agent LLM à un système d'information existant, et
mesurer l'effet de chaque décision de conception sur le comportement de l'agent.

Plus précisément, être capable à l'issue du TP de :

- exposer une API REST et une base de données à un LLM sous forme de tools ADK ;
- rédiger une docstring de tool exploitable par un modèle ;
- distinguer erreur métier et erreur technique, et traiter chacune correctement ;
- encadrer un tool à effet de bord par une instruction d'agent ;
- republier un connecteur sous forme de serveur MCP.

## Sujet

Mise en situation : une boutique en ligne est déjà en service — base de données,
API REST, catalogue, clients, commandes. Un agent ADK est livré avec, mais il est
aveugle : il ignore tout de ce système.

Le travail consiste à écrire ce qui manque entre les deux, le **connecteur**.

Ni la base ni l'API ne peuvent être modifiées. Comme en situation réelle, le
système existant ne s'adapte pas à l'agent : c'est à l'agent de savoir lui parler.

## Ce qui est mis à disposition

L'environnement complet est fourni et démarre par une commande unique. Aucune
installation de Python, de PostgreSQL ou de dépendance n'est requise.

| Brique | Contenu | Statut |
|---|---|---|
| Base PostgreSQL | 180 produits · 8 catégories · 60 clients · 300 commandes · 700 avis · stocks répartis sur 3 entrepôts | fournie — accès en lecture seule |
| API REST | 8 routes : catalogue, clients, commandes. Clé d'API, pagination, codes d'erreur métier, documentation interactive | fournie — non modifiable |
| Agent ADK | agent opérationnel sous `adk web`, configuration et clients d'accès prêts à l'emploi | fourni — à compléter |
| Serveur MCP | squelette destiné à héberger les tools de l'exercice 4 | fourni — à compléter |
| Documentation | `docs/API.md` : routes et erreurs · `docs/SCHEMA.md` : schéma et requêtes types | fournie |

## Ce qui est à produire

Six tools, une instruction d'agent et un serveur MCP, répartis sur cinq fichiers :

| Fichier | Contenu attendu | Exercice |
|---|---|---|
| `agent/shop_agent/tools_api.py` | 4 tools interrogeant l'API REST | 1 et 3 |
| `agent/shop_agent/tools_db.py` | 2 tools interrogeant la base en SQL | 2 |
| `agent/shop_agent/agent.py` | déclaration des tools et instruction de l'agent | 1 et 3 |
| `mcp_server/server.py` | publication des tools en MCP | 4 (bonus) |
| `agent/shop_agent/tools_mcp.py` | branchement du serveur MCP sur l'agent | 4 (bonus) |

## Prérequis

- Docker Desktop installé et démarré ;
- une clé Google AI Studio (gratuite) : https://aistudio.google.com/apikey ;
- des notions de Python et de SQL.

---

## Mise en route

```bash
cp .env.example .env          # renseigner GOOGLE_API_KEY
make preflight                # vérification de la clé, téléchargement des images
make up                       # démarrage de la boutique
```

`make` sans argument liste toutes les commandes disponibles.

### Services

| Adresse | Service |
|---|---|
| http://localhost:8000 | Agent ADK — interface `adk web` |
| http://localhost:8080/docs | API de la boutique — documentation interactive |
| http://localhost:8081 | Adminer — interface web d'accès à la base |

`make logs` affiche l'activité de l'agent en direct.

Adminer ne demande aucune installation. Les quatre champs du formulaire :

| Champ Adminer | Valeur |
|---|---|
| Système | **PostgreSQL** — le menu propose MySQL par défaut |
| Serveur | `db` |
| Utilisateur / Mot de passe | `student` / `student` |
| Base de données | `shop` |

Adminer s'exécutant lui-même dans un conteneur, le serveur est `db`, nom du
service dans le réseau Docker. `localhost` y désignerait le conteneur Adminer
et serait refusé.

Pour un client SQL externe (DBeaver, DataGrip, psql), le serveur PostgreSQL
lui-même est exposé sur un **autre port** :

| Paramètre | Valeur |
|---|---|
| Hôte | `localhost` |
| Port | `5432` |
| Base | `shop` |
| Utilisateur / mot de passe | `student` / `student` (lecture seule) |

Trois confusions fréquentes :

- `8081` est le port de l'interface web d'Adminer, pas celui de PostgreSQL ;
- le nom du serveur dépend du point de départ : `db` depuis Adminer, qui tourne
  dans un conteneur, mais `localhost` depuis un client installé sur le poste ;
- Adminer propose **MySQL** par défaut dans le menu *Système* : sélectionner
  PostgreSQL, sinon la connexion échoue quels que soient les autres champs.

> **Avertissement — adressage réseau.** Depuis un navigateur, l'API répond sur
> `localhost:8080`. Depuis le conteneur de l'agent, elle répond sur `api:8000`.
> Le code des tools s'exécute dans le conteneur : il utilise donc `api:8000`.
> Ce point est déjà traité dans `config.py`, à condition de passer par le client
> fourni `shop_api()`.

### Périmètre de travail

Seuls deux emplacements sont à modifier :

- `agent/shop_agent/` — les tools et l'agent (exercices 1 à 3) ;
- `mcp_server/server.py` — le serveur MCP (exercice 4).

L'édition se fait dans l'IDE local. Les fichiers sont montés dans le conteneur,
qui prend en compte les modifications sans redémarrage.

### Vérifier son travail

La vérification se fait en conversant avec l'agent dans `adk web`. Chaque
exercice se termine par une question à lui poser et le comportement attendu en
réponse.

Deux commandes utiles pendant la mise au point :

| Commande | Usage |
|---|---|
| `make logs` | affiche les appels de tools et les erreurs Python en direct |
| `make reset` | remet la base à zéro, notamment le stock réservé par les essais |

---

## Exercice 0 — Constater les limites du modèle seul

**Durée : 25 min · aucun code**

Ouvrir http://localhost:8000, sélectionner `shop_agent` et poser la question :

> « Combien coûte le casque Orion Air ? »

Observer précisément la réponse. L'agent ne dispose d'aucun tool
(`tools=[]` dans `agent.py`) ni d'aucun accès au catalogue : il refuse ou il
invente. Cette réponse constitue le point de référence du TP.

Explorer ensuite les deux briques à connecter :

- l'API sur http://localhost:8080/docs — essayer `GET /products`, clé `tp-adk-2026` ;
- la base via Adminer sur http://localhost:8081.

---

## Exercice 1 — Interroger le catalogue

**Durée : 35 min · fichier `agent/shop_agent/tools_api.py`**

### À implémenter

```python
def search_products(query: str = "", category: str = "", max_price_eur: float = 0.0) -> dict
def get_product(sku: str) -> dict
```

La docstring de `search_products` est fournie intégralement : elle sert de
modèle de référence et doit être lue avant de rédiger celle de `get_product`.
Seuls les corps sont à écrire.

Brancher ensuite les deux tools dans `agent.py` (`tools=[...]`), puis reposer la
question de l'exercice 0 et comparer.

### Points d'attention

- `GET /products` renvoie `items` **et** `total`. Ignorer `total` conduit l'agent
  à affirmer que le catalogue compte 20 produits ; il en compte 180.
- Le filtre de l'API porte sur `max_price_cents`, le tool reçoit des euros.
- Renvoyer les descriptions complètes de 20 produits permet de mesurer l'effet
  d'une réponse trop volumineuse sur la qualité des réponses.

### Vérification

Dans `adk web` : « quels casques proposez-vous à moins de 100 € ? »

L'agent doit citer des références réelles du catalogue avec leur prix en euros.
Puis : « combien de produits compte le catalogue ? » — la réponse attendue est
180, et non 20.

---

## Exercice 2 — Accéder directement à la base

**Durée : 35 min · fichier `agent/shop_agent/tools_db.py`**

### Contexte

L'API ne permet pas de répondre à « quel est le casque le mieux noté ? ».
L'information existe pourtant, dans la table `product_reviews`. Deux options :
attendre une évolution de l'API, ou lire la base. Un connecteur combine
généralement les deux approches.

### À implémenter

```python
def check_stock(sku: str) -> dict
def top_rated_products(category: str = "", limit: int = 5) -> dict
```

Adminer (http://localhost:8081) permet d'explorer le schéma et de mettre au
point les requêtes avant de les coder. Le schéma est également décrit dans
`docs/SCHEMA.md`.

### Points d'attention

- `quantity_available` inclut les articles **déjà réservés** par d'autres
  commandes. Le stock réellement vendable vaut `available - reserved`.
- Un produit noté 5/5 par un seul client n'est pas « le mieux noté » :
  filtrer sur un nombre minimal d'avis (`HAVING count(...) >= 3`).
- Les paramètres SQL se passent toujours par le second argument de `execute()`,
  jamais par concaténation.

À titre d'illustration, tenter un `DELETE` depuis Adminer avec le compte
`student` : la base refuse. Le rôle utilisé par les tools est restreint à la
lecture seule — le moindre privilège est ici la configuration par défaut, non
une précaution ajoutée après coup.

### Vérification

Dans `adk web` : « le AUD-0174 est-il disponible ? », puis « quels sont les
produits audio les mieux notés ? »

L'agent doit annoncer un stock réparti par entrepôt, et un classement assorti
des notes moyennes et du nombre d'avis.

---

## Exercice 3 — Agir sur le système

**Durée : 40 min · fichiers `tools_api.py` et `agent.py`**

### À implémenter

```python
def get_customer_orders(email: str) -> dict
def create_order(customer_email: str, sku: str, quantity: int) -> dict
```

`create_order` est le premier tool qui **modifie** l'état du système.

Après l'avoir branché, demander à l'agent de passer une commande et observer son
comportement : vérifie-t-il le stock ? demande-t-il confirmation ? ou commande-t-il
dès que le mot « commande » apparaît dans la conversation ?

### Point central de l'exercice

La moitié du travail se situe dans `INSTRUCTION`, non dans le code Python. Les
règles à respecter avant tout appel à `create_order` doivent y être énoncées
explicitement : ce qui n'est pas écrit ne sera pas appliqué.

### Erreurs à traiter en valeur de retour

| Code | Cas | Traitement attendu |
|---|---|---|
| 409 | stock insuffisant | transmettre la quantité réellement disponible, pour permettre une contre-proposition |
| 404 | client ou produit inconnu | message explicite |
| 422 | quantité hors bornes (1 à 100) | message permettant au modèle de se corriger |

Client de test : `alice@example.com`.

### Vérification

Dans `adk web`, enchaîner :

1. « quelles sont les dernières commandes de alice@example.com ? » ;
2. « commande-lui un AUD-0174 » — l'agent doit vérifier le stock, récapituler et
   **attendre une confirmation** avant d'agir ;
3. « en fait, j'en veux 100 » — l'agent doit annoncer le stock réellement
   disponible et proposer une quantité réduite, sans message d'erreur technique.

L'étape 2 est le critère déterminant : un agent qui commande sans confirmation
signale une instruction insuffisante.

---

## Exercice 4 — Publier le connecteur en MCP

**Durée : 40 min · exercice bonus · fichiers `mcp_server/server.py` puis `agent/shop_agent/tools_mcp.py`**

### Contexte

Les tools de l'exercice 2 ne sont utilisables que depuis cet agent ADK. Un
serveur MCP expose le même code métier sous forme de service autonome,
consommable par tout client compatible : un agent ADK, un IDE, Claude Code, ou
l'agent d'un tiers écrit dans un autre framework. C'est la différence entre
écrire une fonction et publier une API.

### Marche à suivre

1. Reprendre `check_stock` et `top_rated_products` dans `mcp_server/server.py`,
   décorés par `@mcp.tool()`.
2. Démarrer le serveur : `make mcp`.
3. Déclarer un `McpToolset` dans `tools_mcp.py`, puis le substituer aux deux
   function tools dans `agent.py`.

Le comportement de l'agent doit rester strictement identique : seul le mode
d'accès aux données change, pas les données elles-mêmes.

> Les chemins d'import indiqués par la documentation officielle ne correspondent
> pas à la version installée. Les chemins valides figurent dans `tools_mcp.py`.

### Vérification

Reposer les deux questions de l'exercice 2. Les réponses doivent être
identiques : seul le chemin d'accès a changé. `make logs` confirme que les
appels transitent désormais par le serveur MCP.

---

## Annexe — Dépannage

| Symptôme | Cause la plus probable |
|---|---|
| `Connection refused` vers `localhost:8080` depuis un tool | Le code s'exécute dans le conteneur : utiliser `shop_api()` (`api:8000`). |
| L'agent invente des prix | Tool absent de `tools=[...]` dans `agent.py`. |
| L'agent n'appelle jamais un tool | La docstring n'indique pas *quand* l'utiliser. Relire celle de `search_products`. |
| `401 unauthorized` | Passer par `shop_api()`, qui transmet la clé d'API. |
| L'agent disparaît de l'interface | Erreur de syntaxe dans un fichier. Consulter `make logs`. |
| Stock qui diminue sans raison | Les essais de commande réservent du stock. Lancer `make reset`. |
| Client SQL connecté mais aucune table | Champ *Database* laissé à `postgres` : la connexion réussit sur une base vide. Saisir `shop`. |
| Client SQL : connexion refusée | Port `8081` (Adminer) au lieu de `5432`, ou hôte `db` au lieu de `localhost`. |
| Adminer refuse la connexion | Menu *Système* resté sur MySQL : sélectionner PostgreSQL. Le serveur est `db`, pas `localhost`. |
| Blocage général | `make reset` réinitialise la boutique. |

## Annexe — Documentation fournie

| Fichier | Contenu |
|---|---|
| `docs/API.md` | routes, paramètres, codes d'erreur de l'API |
| `docs/SCHEMA.md` | schéma de la base, pièges, requêtes types |
| http://localhost:8080/docs | documentation interactive de l'API |

---

## Pour aller plus loin

Ce TP s'arrête au développement local : l'agent, l'API et la base tournent dans
Docker, sur un poste. Les deux ressources suivantes, publiées par Google sur
[Google Skills](https://www.skills.google/), prolongent directement les
exercices 3 et 4 en abordant le déploiement.

| Ressource | Prolonge | Durée |
|---|---|---|
| [Build an AI Agent and Configure an MCP Server on Cloud Run](https://www.skills.google/focuses/132621) | exercice 4 | ~1 h 30 |
| [Deploy Your First Agent](https://www.skills.google/paths/3802/course_templates/1639) | exercices 3 et 4 | ~1 h 15 |

**Build an AI Agent and Configure an MCP Server on Cloud Run** — atelier pratique.
Construction d'un agent guide touristique pour un zoo fictif, interrogeant un
serveur MCP distant et Wikipédia, puis déploiement sur Cloud Run. Le schéma est
celui de l'exercice 4 — un agent ADK consommant un serveur MCP — mais avec un
serveur hébergé et non plus un conteneur local.

**Deploy Your First Agent** — cours de niveau avancé. Passage d'un agent ADK du
poste de développement à la production : déploiement sur Vertex AI Agent Engine
et sur Cloud Run, et introduction à Memory Bank pour la mémoire persistante
entre sessions. Cette dernière notion répond à une limite visible dès
l'exercice 3 : l'agent du TP ne conserve rien d'une conversation à l'autre.

Ces deux ressources nécessitent un compte Google Skills. Les ateliers pratiques
s'exécutent sur une infrastructure Google Cloud provisionnée pour la session.
