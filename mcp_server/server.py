"""Serveur MCP du shop — EXERCICE 4 (bonus).

Objectif : reprendre les deux tools de l'exercice 2 (check_stock,
top_rated_products) et les publier comme un service MCP autonome, que l'agent
consommera ensuite via un McpToolset.

Démarrage : make mcp        (logs : docker compose logs -f mcp)
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


# ══════════════════════════════════════════════════════════════════════════════
#  EXEMPLE FOURNI — le même check_stock que dans tools_db.py, publié en MCP.
#
#  Seul l'emballage change : @mcp.tool() suffit, FastMCP lit la signature et la
#  docstring pour construire le schéma MCP. Le code métier est identique.
# ══════════════════════════════════════════════════════════════════════════════

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


# TODO EXERCICE 4 — publier le second tool sur le même modèle.
#
#   Reprendre top_rated_products en suivant exactement le modèle de check_stock
#   ci-dessus. Le corps peut être copié depuis tools_db.py : c'est le même code
#   métier, seul l'emballage change. C'est précisément l'intérêt de l'exercice,
#   et la raison pour laquelle l'agent doit se comporter à l'identique une fois
#   le serveur branché.


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
