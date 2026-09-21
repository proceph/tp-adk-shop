"""Tools qui interrogent l'API du shop — EXERCICES 1 et 3.

Conventions à respecter dans tous les tools du TP :

  1. Le NOM de la fonction et sa DOCSTRING constituent ce que le LLM lit pour
     décider d'appeler le tool, et avec quels arguments. Ce ne sont pas des
     commentaires : c'est la spécification vue par le modèle. Une docstring
     imprécise produit un agent qui appelle le mauvais tool.
  2. Annotations de type obligatoires, et simples : str, int, float, bool.
  3. Retourner un dict contenant une clé `status` ("success" ou "error").
  4. Erreur MÉTIER attendue (produit inconnu, rupture de stock) -> retourner
     {"status": "error", "message": ...}, que le LLM saura expliquer à
     l'utilisateur. Erreur TECHNIQUE (API injoignable) -> laisser l'exception
     remonter : ADK dispose d'un mécanisme de reprise qu'un `except Exception:`
     générique désactiverait.
  5. Borner le volume retourné. Le LLM n'a pas besoin de 180 produits complets.

Documentation de l'API : http://localhost:8080/docs
"""

from .config import euros, shop_api

DESCRIPTION_MAX = 160


# ──────────────────────────────────────────────────────────────────────────────
# EXERCICE 1 — interroger le catalogue
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
    # ↑ Cette docstring sert de MODÈLE : c'est le niveau de précision attendu
    #   pour tous les autres tools. La lire avant de rédiger les suivantes.
    #
    # TODO EXERCICE 1 — implémenter le corps.
    #   1. Appeler GET /products avec le client fourni :
    #          with shop_api() as client:
    #              response = client.get("/products", params=...)
    #   2. Attention : l'API attend `max_price_cents`, pas des euros.
    #   3. Attention : la réponse contient `items` ET `total`, qui ne sont pas la
    #      même chose. Observer la réponse réelle sur http://localhost:8080/docs
    #      avant de coder.
    #   4. Retourner les prix en euros — le helper `euros()` est prévu pour cela.
    raise NotImplementedError("Exercice 1 : implémenter search_products dans tools_api.py")


def get_product(sku: str) -> dict:
    """TODO EXERCICE 1 — rédiger la docstring de ce tool.

    Prendre modèle sur search_products ci-dessus. Elle doit préciser :
      - ce que fait le tool, en une phrase ;
      - QUAND le LLM doit l'utiliser ;
      - ce qu'est `sku` et la forme qu'il prend (avec un exemple : "AUD-0174") ;
      - le contenu du dict retourné, y compris dans le cas d'erreur.
    """
    # TODO EXERCICE 1 — implémenter le corps.
    #   - Appeler GET /products/{sku}.
    #   - Un SKU inconnu renvoie un 404 : erreur MÉTIER attendue, donc un dict
    #     {"status": "error", ...}, et surtout pas une exception.
    #   - Retourner la description tronquée à DESCRIPTION_MAX caractères.
    raise NotImplementedError("Exercice 1 : implémenter get_product dans tools_api.py")


# ──────────────────────────────────────────────────────────────────────────────
# EXERCICE 3 — historique client et passage de commande
# ──────────────────────────────────────────────────────────────────────────────


def get_customer_orders(email: str) -> dict:
    """TODO EXERCICE 3 — rédiger la docstring.

    Ce tool liste les commandes d'un client, de la plus récente à la plus ancienne.
    """
    # TODO EXERCICE 3 — implémenter.
    #   - GET /customers/{email}/orders
    #   - Email inconnu (404) -> erreur métier.
    #   - Montants en euros, et limitation aux 10 commandes les plus récentes.
    raise NotImplementedError("Exercice 3 : implémenter get_customer_orders dans tools_api.py")


def create_order(customer_email: str, sku: str, quantity: int) -> dict:
    """TODO EXERCICE 3 — rédiger la docstring. Celle-ci mérite un soin particulier.

    C'est le seul tool qui MODIFIE l'état du système. La docstring doit indiquer
    explicitement au LLM qu'il s'agit d'une action irréversible, à n'appeler
    qu'après confirmation de l'utilisateur.
    """
    # TODO EXERCICE 3 — implémenter.
    #   POST /orders avec le corps :
    #       {"customer_email": ..., "items": [{"sku": ..., "quantity": ...}]}
    #
    #   Trois erreurs métier à traiter, toutes en valeur de retour :
    #     - 409 out_of_stock       -> indiquer au LLM combien d'exemplaires
    #                                 restent (error.details.available), afin
    #                                 qu'il puisse proposer une quantité réduite ;
    #     - 404 unknown_sku / unknown_customer ;
    #     - 422                    -> la boutique refuse les quantités hors bornes
    #                                 (1 à 100). Le LLM peut se corriger seul.
    raise NotImplementedError("Exercice 3 : implémenter create_order dans tools_api.py")
