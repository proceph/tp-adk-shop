"""Tools qui parlent à l'API du shop — PALIERS 1 et 3.

C'est ici que tu travailles. Les conventions du TP, à respecter partout :

  1. Le NOM de la fonction et sa DOCSTRING sont ce que le LLM lit pour décider
     s'il appelle ton tool, et avec quels arguments. Ce n'est pas du commentaire :
     c'est la spécification que voit le modèle. Une docstring vague = un agent qui
     appelle le mauvais tool.
  2. Type hints obligatoires, et simples : str, int, float, bool.
  3. Renvoie un dict contenant une clé `status` ("success" ou "error").
  4. Erreur MÉTIER attendue (produit inconnu, rupture de stock) -> renvoie
     {"status": "error", "message": ...}. Le LLM saura l'expliquer à l'utilisateur.
     Erreur TECHNIQUE (API injoignable) -> laisse l'exception remonter : ADK a un
     mécanisme de retry qu'un `except Exception:` fourre-tout désactiverait.
  5. Borne ce que tu renvoies. Le LLM n'a pas besoin de 180 produits complets.

Documentation de l'API : http://localhost:8080/docs
"""

from .config import euros, shop_api

DESCRIPTION_MAX = 160


# ──────────────────────────────────────────────────────────────────────────────
# PALIER 1 — interroger le catalogue
# ──────────────────────────────────────────────────────────────────────────────


def search_products(query: str = "", category: str = "", max_price_eur: float = 0.0) -> dict:
    """Recherche des produits dans le catalogue de la boutique.

    Utilise ce tool dès que l'utilisateur cherche un article, demande ce qui
    existe dans une gamme, ou pose une question sur les prix du catalogue.

    Args:
        query: Texte libre cherché dans le nom et la marque, par exemple "casque"
            ou "Aurora". Laisser vide pour ne pas filtrer sur le texte.
        category: Catégorie exacte parmi : audio, informatique, photo,
            maison-connectee, sport, gaming, telephonie, accessoires.
            Laisser vide pour toutes les catégories.
        max_price_eur: Prix maximum EN EUROS. Mettre 0 pour ne pas filtrer.

    Returns:
        Un dict avec `status`, `count` (nombre de produits renvoyés),
        `total_matching` (nombre total de produits correspondants, qui peut être
        plus grand que `count`) et `products` : une liste de produits avec leur
        sku, nom, marque, catégorie et prix en euros.
    """
    # ↑ Cette docstring est ton MODÈLE : c'est le niveau de précision attendu
    #   pour tous les autres tools. Lis-la avant d'écrire les tiennes.
    #
    # TODO PALIER 1 — implémente le corps.
    #   1. Appelle GET /products avec le client fourni :
    #          with shop_api() as client:
    #              response = client.get("/products", params=...)
    #   2. Attention : l'API attend `max_price_cents`, pas des euros.
    #   3. Attention : la réponse contient `items` ET `total`. Ce n'est pas la
    #      même chose. Regarde ce que renvoie l'API sur http://localhost:8080/docs
    #      avant de coder.
    #   4. Renvoie les prix en euros — le helper `euros()` est là pour ça.
    raise NotImplementedError("Palier 1 : implémente search_products dans tools_api.py")


def get_product(sku: str) -> dict:
    """TODO PALIER 1 — écris la docstring de ce tool.

    Prends modèle sur search_products ci-dessus. Elle doit dire :
      - ce que fait le tool, en une phrase ;
      - QUAND le LLM doit l'utiliser ;
      - ce qu'est `sku` et à quoi il ressemble (donne un exemple : "AUD-0174") ;
      - ce que contient le dict renvoyé, y compris le cas d'erreur.
    """
    # TODO PALIER 1 — implémente le corps.
    #   - Appelle GET /products/{sku}.
    #   - Un SKU inconnu renvoie un 404 : c'est une erreur MÉTIER attendue, donc
    #     un dict {"status": "error", ...}, surtout pas une exception.
    #   - Renvoie la description, mais tronquée à DESCRIPTION_MAX caractères.
    raise NotImplementedError("Palier 1 : implémente get_product dans tools_api.py")


# ──────────────────────────────────────────────────────────────────────────────
# PALIER 3 — historique client et passage de commande
# ──────────────────────────────────────────────────────────────────────────────


def get_customer_orders(email: str) -> dict:
    """TODO PALIER 3 — écris la docstring.

    Ce tool liste les commandes d'un client, de la plus récente à la plus ancienne.
    """
    # TODO PALIER 3 — implémente.
    #   - GET /customers/{email}/orders
    #   - Email inconnu (404) -> erreur métier.
    #   - Montants en euros, et limite-toi aux 10 commandes les plus récentes.
    raise NotImplementedError("Palier 3 : implémente get_customer_orders dans tools_api.py")


def create_order(customer_email: str, sku: str, quantity: int) -> dict:
    """TODO PALIER 3 — écris la docstring. Celle-ci mérite un soin particulier.

    C'est le seul tool qui MODIFIE quelque chose dans le monde réel. Ta docstring
    doit dire explicitement au LLM qu'il s'agit d'une action irréversible et qu'il
    ne doit pas l'appeler sans confirmation de l'utilisateur.
    """
    # TODO PALIER 3 — implémente.
    #   POST /orders avec le corps :
    #       {"customer_email": ..., "items": [{"sku": ..., "quantity": ...}]}
    #
    #   Trois erreurs métier à traiter, toutes en valeur de retour :
    #     - 409 out_of_stock       -> dis au LLM combien d'exemplaires restent
    #                                 (c'est dans error.details.available), il
    #                                 pourra proposer d'en commander moins ;
    #     - 404 unknown_sku / unknown_customer ;
    #     - 422                    -> la boutique refuse les quantités hors bornes
    #                                 (1 à 100). Le LLM peut corriger lui-même.
    raise NotImplementedError("Palier 3 : implémente create_order dans tools_api.py")
