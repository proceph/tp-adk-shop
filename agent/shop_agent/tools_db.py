"""Tools qui parlent directement à la base Postgres (palier 2).

Pourquoi descendre en base alors qu'une API existe ?
Parce que l'API expose ce que ses concepteurs ont prévu d'exposer. Dès qu'on a
besoin d'un agrégat qu'aucun endpoint ne fournit — « les mieux notés »,
« le stock consolidé par entrepôt » — soit on demande une évolution de l'API,
soit on lit la base. Un connecteur, dans la vraie vie, fait souvent les deux.

La connexion utilise le rôle `student`, qui n'a QUE le droit SELECT. Quand on
branche un LLM sur une base, le moindre privilège n'est pas une précaution
théorique : c'est la configuration par défaut.
"""

from .config import db_connection, euros


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
    """Classe les produits les mieux notés par les clients, note moyenne à l'appui.

    Utilise ce tool quand l'utilisateur demande un conseil, les meilleurs
    produits, les plus appréciés, ou ce que tu recommandes. Cette information
    n'existe nulle part ailleurs : elle est calculée à partir des avis clients.

    Args:
        category: Catégorie exacte parmi : audio, informatique, photo,
            maison-connectee, sport, gaming, telephonie, accessoires.
            Laisser vide pour toutes les catégories.
        limit: Nombre de produits à renvoyer, entre 1 et 20.

    Returns:
        Un dict avec `status` et `products` : pour chacun son sku, son nom, son
        prix en euros, sa note moyenne sur 5 et son nombre d'avis. Seuls les
        produits ayant au moins 3 avis sont classés, pour éviter qu'un unique
        avis à 5 étoiles ne fausse le classement.
    """
    limit = max(1, min(limit, 20))

    sql = """
        SELECT p.sku,
               p.name,
               p.price_cents,
               c.slug AS category,
               round(avg(r.rating)::numeric, 2) AS average_rating,
               count(r.id) AS review_count
        FROM products p
        JOIN categories c ON c.id = p.category_id
        JOIN product_reviews r ON r.product_id = p.id
        {where}
        GROUP BY p.sku, p.name, p.price_cents, c.slug
        HAVING count(r.id) >= 3
        ORDER BY avg(r.rating) DESC, count(r.id) DESC
        LIMIT %s
    """
    if category:
        sql = sql.format(where="WHERE c.slug = %s")
        params: tuple = (category, limit)
    else:
        sql = sql.format(where="")
        params = (limit,)

    with db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    if not rows:
        return {
            "status": "error",
            "message": f"Aucun produit noté dans la catégorie '{category}'.",
        }

    return {
        "status": "success",
        "count": len(rows),
        "products": [
            {
                "sku": row["sku"],
                "name": row["name"],
                "category": row["category"],
                "price_eur": euros(row["price_cents"]),
                "average_rating": float(row["average_rating"]),
                "review_count": row["review_count"],
            }
            for row in rows
        ],
    }
