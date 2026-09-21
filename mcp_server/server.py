"""Serveur MCP du shop — exercice 4.

Mêmes capacités que les tools de l'exercice 2, autre emballage.

Un function tool ADK ne vit que dans l'agent qui le déclare. Un serveur MCP est
un service autonome que tout client compatible peut consommer : cet agent ADK,
mais aussi Claude Code, un IDE, ou l'agent d'un tiers écrit dans un autre
framework. C'est la différence entre écrire une fonction et publier une API.

Ce serveur parle le transport `streamable-http` et écoute sur http://mcp:9000/mcp.
"""

import os

import psycopg
from mcp.server.fastmcp import FastMCP
from psycopg.rows import dict_row

SHOP_DB_URL = os.environ.get("SHOP_DB_URL", "postgresql://student:student@db:5432/shop")

mcp = FastMCP(
    name="shop-inventory",
    instructions="Stock et avis clients de la boutique, lus directement en base.",
    host="0.0.0.0",
    port=9000,
)


def _connect() -> psycopg.Connection:
    return psycopg.connect(SHOP_DB_URL, row_factory=dict_row)


@mcp.tool()
def check_stock(sku: str) -> dict:
    """Donne le stock disponible d'un produit, entrepôt par entrepôt.

    Args:
        sku: Référence du produit, au format "AUD-0174".
    """
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT i.warehouse,
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
        "warehouses": rows,
    }


@mcp.tool()
def top_rated_products(category: str = "", limit: int = 5) -> dict:
    """Classe les produits les mieux notés par les clients.

    Args:
        category: Catégorie exacte (audio, informatique, photo, maison-connectee,
            sport, gaming, telephonie, accessoires). Vide = toutes catégories.
        limit: Nombre de produits à renvoyer, entre 1 et 20.
    """
    limit = max(1, min(limit, 20))
    sql = """
        SELECT p.sku, p.name, p.price_cents, c.slug AS category,
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
        sql, params = sql.format(where="WHERE c.slug = %s"), (category, limit)
    else:
        sql, params = sql.format(where=""), (limit,)

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()

    if not rows:
        return {"status": "error", "message": f"Aucun produit noté dans '{category}'."}

    return {
        "status": "success",
        "count": len(rows),
        "products": [
            {
                "sku": r["sku"],
                "name": r["name"],
                "category": r["category"],
                "price_eur": round(r["price_cents"] / 100, 2),
                "average_rating": float(r["average_rating"]),
                "review_count": r["review_count"],
            }
            for r in rows
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
