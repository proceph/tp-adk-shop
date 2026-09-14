# TP ADK — Construis ton connecteur

Une boutique en ligne existe déjà : une base de données, une API, des clients,
des commandes. Un agent ADK existe aussi, mais il est **aveugle** : il ne sait
rien de ce catalogue.

Ton travail est d'écrire ce qui manque entre les deux — le **connecteur**.

Tu ne modifieras ni la base, ni l'API. Comme dans la vraie vie : le système est
là, il ne bougera pas pour toi, et c'est à ton agent de savoir lui parler.

---

## 1. Démarrage

Prérequis : Docker Desktop, et une clé Google AI Studio (gratuite).

```bash
cp .env.example .env          # puis colle ta clé dans GOOGLE_API_KEY
make preflight                # vérifie ta clé et télécharge les images
make up                       # démarre la boutique
```

Ta clé se crée en trente secondes sur **https://aistudio.google.com/apikey**.

Quatre adresses à garder ouvertes :

| Adresse | Quoi |
|---|---|
| http://localhost:8000 | **Ton agent** (interface `adk web`) |
| http://localhost:8080/docs | L'API de la boutique, documentation interactive |
| http://localhost:8081 | La base de données (`db` / `student` / `student` / `shop`) |
| — | `make logs` pour voir ce que fait ton agent en direct |

> **Le piège numéro un de ce TP.** Depuis ton navigateur, l'API est sur
> `localhost:8080`. Depuis le conteneur de l'agent, elle est sur `api:8000`.
> Ce ne sont pas les mêmes adresses. Ton code tourne dans le conteneur : il
> utilise `api:8000`, et c'est déjà configuré dans `config.py`.

**Tu édites uniquement dans `agent/shop_agent/`** (et `mcp_server/server.py` au
palier 4). Ton IDE local, tes fichiers : le conteneur voit tes modifications
immédiatement, pas besoin de le redémarrer.

Pour vérifier ton travail à tout moment : `make check1`, `make check2`, … ou
`make check` pour tout. Ces tests appellent tes fonctions directement, sans
passer par le LLM : un test rouge est un vrai bug, jamais un caprice du modèle.

---

## 2. Les règles du jeu

Six conventions, valables pour chaque tool que tu écriras. Elles ne sont pas
décoratives : ce sont elles que les tests vérifient.

1. **Le nom et la docstring sont la spécification que lit le LLM.** Pas un
   commentaire : la seule chose sur laquelle le modèle s'appuie pour décider
   d'appeler ton tool, et avec quels arguments. Une docstring floue produit un
   agent qui appelle le mauvais tool au mauvais moment.
2. **Type hints obligatoires, et simples** : `str`, `int`, `float`, `bool`.
3. **Renvoie un `dict` avec une clé `status`** (`"success"` ou `"error"`).
4. **Erreur métier ≠ erreur technique.** Un produit inconnu, une rupture de
   stock : la boutique fonctionne normalement, elle te dit non. Ça se renvoie
   en valeur de retour, pour que l'agent l'explique à l'utilisateur. Une API
   injoignable, en revanche, est une panne : laisse l'exception remonter, ADK
   sait réessayer. **N'écris jamais un `except Exception:` fourre-tout** — en
   ADK 2.x il masque la panne au framework et désactive le retry automatique.
5. **Borne ce que tu renvoies.** Le catalogue fait 180 produits. Les envoyer
   tous, descriptions comprises, gaspille la fenêtre de contexte du modèle et
   dégrade ses réponses.
6. **Convertis pour les humains.** L'API parle en centimes. Personne ne dit
   « ce casque coûte 2980 ». Le helper `euros()` est fourni.

---

## Palier 0 — l'agent aveugle *(25 min)*

Ouvre http://localhost:8000, choisis `shop_agent`, et demande-lui :

> « Combien coûte le casque Orion Air ? »

Il va te répondre quelque chose. Regarde bien **quoi**. Il n'a aucun tool
(`tools=[]` dans `agent.py`) et aucun accès au catalogue : soit il refuse, soit
il invente. Retiens cette réponse, c'est le point de départ.

Va voir les briques auxquelles tu vas le connecter : l'API sur
http://localhost:8080/docs (essaie `GET /products` — la clé est `tp-adk-2026`),
et la base sur http://localhost:8081.

---

## Palier 1 — voir le catalogue *(35 min)*

**Fichier : `agent/shop_agent/tools_api.py`**

```python
def search_products(query: str = "", category: str = "", max_price_eur: float = 0.0) -> dict
def get_product(sku: str) -> dict
```

La docstring de `search_products` t'est donnée en entier : c'est ton **modèle**,
lis-la avant d'écrire celle de `get_product`. Les corps sont à écrire.

Branche-les ensuite dans `agent.py` (`tools=[search_products, get_product]`) et
repose ta question du palier 0. La différence est tout l'objet de ce TP.

Trois pièges t'attendent, tous visibles dans la conversation :
- `GET /products` renvoie `items` **et** `total`. Si tu ignores `total`, ton
  agent affirmera au client qu'il n'existe que 20 produits. Il y en a 180.
- L'API filtre sur `max_price_cents`, ton tool reçoit des euros.
- Renvoie les descriptions complètes de 20 produits et regarde la qualité des
  réponses se dégrader.

✅ `make check1`

---

## Palier 2 — descendre en base *(35 min)*

**Fichier : `agent/shop_agent/tools_db.py`**

```python
def check_stock(sku: str) -> dict
def top_rated_products(category: str = "", limit: int = 5) -> dict
```

L'API ne sait pas répondre à « quel est le casque le mieux noté ? ». Cette
information existe pourtant : elle est dans la table `product_reviews`. Soit tu
attends une évolution de l'API, soit tu lis la base. Un connecteur fait les deux.

Utilise Adminer (http://localhost:8081) pour explorer le schéma et mettre au
point tes requêtes avant de les coder.

Deux pièges :
- `quantity_available` compte aussi les articles **déjà réservés** par d'autres
  commandes. Le stock réellement vendable, c'est `available - reserved`.
- Un produit noté 5/5 par une seule personne n'est pas « le mieux noté ».
  `HAVING count(...) >= 3`.

Et un troisième, pour la culture : tente un `DELETE` depuis Adminer avec le
compte `student`. La base refusera. Quand on branche un LLM sur des données, le
moindre privilège n'est pas une option qu'on ajoute plus tard.

✅ `make check2`

---

## Palier 3 — agir sur le monde réel *(40 min)*

**Fichiers : `tools_api.py` et `agent.py`**

```python
def get_customer_orders(email: str) -> dict
def create_order(customer_email: str, sku: str, quantity: int) -> dict
```

`create_order` est le premier tool qui **modifie** quelque chose. Tout change.

Écris-le, branche-le, puis demande à ton agent de commander quelque chose. Et
observe : sans garde-fou, va-t-il vérifier le stock ? te demander confirmation ?
ou passer la commande directement parce que tu as prononcé le mot « commande » ?

C'est le vrai exercice du palier : **la moitié du travail est dans
`INSTRUCTION`**, pas dans le code. Écris noir sur blanc ce que l'agent doit
faire avant d'appeler `create_order`. Le modèle ne devinera pas ce que tu n'as
pas écrit.

Trois erreurs métier à traiter en valeur de retour — teste-les, elles arrivent
toutes en conversation réelle :
- stock insuffisant (**409**) : dis au LLM **combien** il en reste, il pourra
  proposer d'en commander moins ;
- client ou produit inconnu (**404**) ;
- quantité hors bornes (**422**) : le modèle peut se corriger tout seul.

Client de test : `alice@example.com`.

✅ `make check3`

---

## Palier 4 — publier ton connecteur *(40 min, bonus)*

**Fichiers : `mcp_server/server.py` puis `agent/shop_agent/tools_mcp.py`**

Tes tools du palier 2 ne vivent que dans ton agent ADK. Personne d'autre ne peut
les utiliser.

Reprends-les dans un **serveur MCP** : le même code métier, publié comme un
service autonome que n'importe quel client compatible peut consommer — ton agent,
Claude Code, un IDE, l'agent d'un collègue écrit dans un autre framework. C'est
la différence entre écrire une fonction et publier une API.

```bash
make mcp       # démarre le serveur
```

Puis branche-le dans `agent.py` via un `McpToolset`, en remplacement de tes deux
function tools. L'agent doit se comporter **exactement pareil** : le test du
palier 4 vérifie précisément que les deux chemins renvoient la même chose.

⚠️ Les chemins d'import de la documentation officielle sont en retard sur la
version installée. Ceux qui marchent sont dans `tools_mcp.py`.

✅ `make check4`

---

## En cas de pépin

| Symptôme | Cause la plus probable |
|---|---|
| `Connection refused` vers `localhost:8080` depuis un tool | Ton code tourne dans le conteneur : c'est `api:8000`. Utilise `shop_api()`. |
| L'agent invente des prix | Tu as oublié de l'ajouter à `tools=[...]` dans `agent.py`. |
| L'agent n'appelle jamais ton tool | Ta docstring ne dit pas *quand* l'utiliser. Relis celle de `search_products`. |
| `401 unauthorized` | Utilise `shop_api()`, qui pose la clé pour toi. |
| L'interface ne voit plus l'agent | Une erreur de syntaxe dans tes fichiers. `make logs`. |
| Les tests de stock échouent bizarrement | Tes essais ont réservé du stock. `make reset`. |
| Rien ne va plus | `make reset` remet la boutique à neuf. |

`make` seul liste toutes les commandes disponibles.
