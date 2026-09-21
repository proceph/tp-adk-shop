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


# ══════════════════════════════════════════════════════════════════════════════
#  EXEMPLE FOURNI — tool SQL complet et fonctionnel.
#
#  À noter dans le code ci-dessous :
#    · les paramètres passent par le second argument d'execute(), jamais par
#      concaténation de chaînes ;
#    · le stock vendable vaut quantity_available - quantity_reserved, car
#      `quantity_available` compte aussi les articles déjà réservés ;
#    · un SKU inconnu produit une liste vide, traitée en erreur métier et non
#      en exception ;
#    · le résultat est agrégé et borné : le LLM reçoit un total et un détail
#      court, pas un dump de la table.
# ══════════════════════════════════════════════════════════════════════════════


def check_stock(sku: str) -> dict:
    """Donne le stock disponible d'un produit, entrepôt par entrepôt.

    Utilise ce tool quand l'utilisateur demande si un article est disponible,
    en stock, ou livrable — et systématiquement avant de passer une commande.

    Args:
        sku: Référence du produit, au format "AUD-0174".

    Returns:
        Un dict avec `status`, `total_sellable` (quantité réellement commandable,
        tous entrepôts confondus) et `warehouses` (le détail par entrepôt).
        Si le SKU est inconnu, `status` vaut "error".
    """
    with db_connection() as conn:
        rows = conn.execute(
            """
            SELECT i.warehouse,
                   i.quantity_available,
                   i.quantity_reserved,
                   i.quantity_available - i.quantity_reserved AS sellable
            FROM inventory i
            JOIN products p ON p.id = i.product_id
            WHERE p.sku = %s
            ORDER BY sellable DESC
            """,
            (sku,),
        ).fetchall()

    if not rows:
        return {"status": "error", "message": f"Aucun produit ne porte la référence {sku}."}

    return {
        "status": "success",
        "sku": sku,
        "total_sellable": sum(row["sellable"] for row in rows),
        "warehouses": [
            {"warehouse": row["warehouse"], "sellable": row["sellable"]} for row in rows
        ],
    }

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
