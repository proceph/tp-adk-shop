"""Tools qui lisent directement la base Postgres — EXERCICE 2.

Pourquoi descendre en base alors qu'une API existe ?

Parce qu'une API expose ce que ses concepteurs ont prévu d'exposer. Dès qu'un
agrégat manque — « les produits les mieux notés » — deux options se présentent :
demander une évolution de l'API (des semaines), ou lire la base (des minutes).
En pratique, un connecteur combine souvent les deux approches.

La connexion utilise le rôle `student`, restreint au SELECT. Quand un LLM est
branché sur une base de données, le moindre privilège n'est pas une précaution
théorique : c'est la configuration par défaut. Un DELETE permet de le constater.

Pour explorer le schéma et mettre au point les requêtes :
    http://localhost:8081   (système=PostgreSQL, serveur=db, utilisateur=student,
                             mot de passe=student, base=shop)
"""

from .config import db_connection, euros


def check_stock(sku: str) -> dict:
    """TODO EXERCICE 2 — rédiger la docstring.

    Ce tool donne le stock disponible d'un produit, entrepôt par entrepôt.
    Préciser au LLM qu'il doit l'utiliser AVANT toute commande.
    """
    # TODO EXERCICE 2 — implémenter.
    #   Table `inventory`, jointure sur `products` pour retrouver le SKU.
    #
    #   PIÈGE : `quantity_available` inclut les articles déjà réservés par
    #   d'autres commandes. Le stock réellement commandable vaut
    #   quantity_available - quantity_reserved.
    #
    #   Usage de la connexion :
    #       with db_connection() as conn:
    #           rows = conn.execute("SELECT ...", (sku,)).fetchall()
    #   Les lignes sont des dictionnaires. Passer TOUJOURS les paramètres par le
    #   second argument : ne jamais construire le SQL par concaténation.
    raise NotImplementedError("Exercice 2 : implémenter check_stock dans tools_db.py")


def top_rated_products(category: str = "", limit: int = 5) -> dict:
    """TODO EXERCICE 2 — rédiger la docstring.

    Ce tool classe les produits les mieux notés à partir des avis clients.
    Préciser au LLM que cette information n'existe nulle part ailleurs : c'est
    précisément ce qui justifie de descendre en base.
    """
    # TODO EXERCICE 2 — implémenter.
    #   Jointure products × categories × product_reviews, avec avg(rating).
    #
    #   PIÈGE : un produit noté 5/5 par UNE seule personne n'est pas « le mieux
    #   noté ». Filtrer sur un minimum d'avis, rôle du HAVING :
    #       GROUP BY ... HAVING count(r.id) >= 3 ORDER BY avg(r.rating) DESC
    #
    #   Retourner également `review_count` : une note sans son nombre d'avis n'a
    #   pas de sens, et le LLM doit pouvoir le mentionner.
    raise NotImplementedError("Exercice 2 : implémenter top_rated_products dans tools_db.py")
