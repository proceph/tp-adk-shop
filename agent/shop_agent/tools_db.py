"""Tools qui lisent directement la base Postgres — PALIER 2.

Pourquoi descendre en base alors qu'une API existe ?

Parce qu'une API expose ce que ses concepteurs ont prévu d'exposer. Dès que tu as
besoin d'un agrégat qu'aucun endpoint ne fournit — « les produits les mieux notés »
— tu as deux choix : demander une évolution de l'API (des semaines), ou lire la
base (des minutes). Un connecteur, dans la vraie vie, fait souvent les deux.

La connexion utilise le rôle `student`, qui n'a QUE le droit SELECT. Quand on
branche un LLM sur une base de données, le moindre privilège n'est pas une
précaution théorique : c'est la configuration par défaut. Essaie un DELETE pour voir.

Pour explorer le schéma et mettre au point tes requêtes :
    http://localhost:8081   (serveur=db, utilisateur=student, mot de passe=student, base=shop)
"""

from .config import db_connection, euros


def check_stock(sku: str) -> dict:
    """TODO PALIER 2 — écris la docstring.

    Ce tool donne le stock disponible d'un produit, entrepôt par entrepôt.
    Pense à préciser au LLM qu'il doit l'utiliser AVANT toute commande.
    """
    # TODO PALIER 2 — implémente.
    #   Table `inventory`, jointure sur `products` pour retrouver le SKU.
    #
    #   PIÈGE : `quantity_available` inclut les articles déjà réservés par
    #   d'autres commandes. Le stock réellement commandable, c'est
    #   quantity_available - quantity_reserved.
    #
    #   Usage de la connexion :
    #       with db_connection() as conn:
    #           rows = conn.execute("SELECT ...", (sku,)).fetchall()
    #   Les lignes sont des dictionnaires. Passe TOUJOURS tes paramètres par le
    #   second argument : ne construis jamais ton SQL par concaténation.
    raise NotImplementedError("Palier 2 : implémente check_stock dans tools_db.py")


def top_rated_products(category: str = "", limit: int = 5) -> dict:
    """TODO PALIER 2 — écris la docstring.

    Ce tool classe les produits les mieux notés à partir des avis clients.
    Précise au LLM que cette information n'existe nulle part ailleurs : c'est
    exactement pour cela qu'on descend en base.
    """
    # TODO PALIER 2 — implémente.
    #   Jointure products × categories × product_reviews, avec avg(rating).
    #
    #   PIÈGE : un produit noté 5/5 par UNE seule personne n'est pas « le mieux
    #   noté ». Filtre sur un minimum d'avis — c'est le rôle de HAVING :
    #       GROUP BY ... HAVING count(r.id) >= 3 ORDER BY avg(r.rating) DESC
    #
    #   Renvoie aussi `review_count` : une note sans son nombre d'avis n'a pas
    #   de sens, et le LLM doit pouvoir le dire à l'utilisateur.
    raise NotImplementedError("Palier 2 : implémente top_rated_products dans tools_db.py")
