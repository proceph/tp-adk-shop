# API de la boutique — aide-mémoire

Base : `http://api:8000` depuis le conteneur agent · `http://localhost:8080` depuis un navigateur
Documentation interactive : http://localhost:8080/docs

Toutes les routes sauf `/health` exigent l'en-tête `X-API-Key: tp-adk-2026`.
Le client fourni par `shop_api()` la transmet automatiquement.

## Routes

| Méthode | Route | Réponse |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` — sans clé |
| GET | `/products` | `{items, total, limit, offset}` |
| GET | `/products/{sku}` | la fiche produit |
| GET | `/products/{sku}/availability` | stock par entrepôt |
| GET | `/customers/{email}` | la fiche client |
| GET | `/customers/{email}/orders` | `{customer_email, orders, total}` |
| POST | `/orders` | la commande créée (**201**) |
| GET | `/orders/{id}` | le détail d'une commande |

### `GET /products`

| Paramètre | Type | Défaut | Note |
|---|---|---|---|
| `q` | texte | — | cherché dans le nom **et** la marque |
| `category` | slug | — | `audio`, `informatique`, `photo`, `maison-connectee`, `sport`, `gaming`, `telephonie`, `accessoires` |
| `max_price_cents` | entier | — | **en centimes** |
| `limit` | entier | **20** | maximum 100 |
| `offset` | entier | 0 | |

```json
{
  "items": [{"sku": "AUD-0174", "name": "Casque filaire Orion Air", "brand": "Orion",
             "category": "audio", "description": "…", "price_cents": 2980}],
  "total": 180, "limit": 20, "offset": 0
}
```

`total` est le nombre de produits **correspondants**, pas le nombre renvoyé.

### `POST /orders`

```json
{"customer_email": "alice@example.com", "items": [{"sku": "AUD-0174", "quantity": 2}]}
```

`quantity` doit être compris entre 1 et 100. La commande est créée avec le
statut `pending` et **réserve le stock** correspondant.

## Erreurs

Toutes les erreurs métier suivent la même forme :

```json
{"error": {"code": "out_of_stock",
           "message": "Stock insuffisant pour AUD-0174 : 99 demandé(s), 38 disponible(s).",
           "details": {"sku": "AUD-0174", "requested": 99, "available": 38}}}
```

S'appuyer sur `code` (stable, destiné aux machines), et non sur `message`
(humain, susceptible de changer).

| Statut | `code` | Quand |
|---|---|---|
| 401 | `unauthorized` | en-tête `X-API-Key` manquant ou faux |
| 404 | `unknown_sku` | le SKU n'existe pas |
| 404 | `unknown_customer` | l'email n'existe pas |
| 404 | `unknown_order` | la commande n'existe pas |
| 409 | `out_of_stock` | stock vendable insuffisant — `details.available` donne le stock réel |
| 422 | *(format FastAPI)* | quantité hors bornes, paramètre invalide |
