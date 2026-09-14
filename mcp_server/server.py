"""Serveur MCP du shop — PALIER 4 (bonus).

Objectif : reprendre tes deux tools du palier 2 (check_stock, top_rated_products)
et les publier comme un service MCP autonome, que ton agent consommera ensuite
via un McpToolset.

Démarre-le avec : make mcp        (logs : docker compose logs -f mcp)
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


# TODO PALIER 4 — publie tes deux tools.
#
#   Le décorateur @mcp.tool() suffit : FastMCP lit la signature et la docstring
#   de ta fonction pour construire le schéma MCP. C'est exactement la même idée
#   que les function tools ADK — la docstring est la spécification.
#
#       @mcp.tool()
#       def check_stock(sku: str) -> dict:
#           """Donne le stock disponible d'un produit, entrepôt par entrepôt.
#
#           Args:
#               sku: Référence du produit, au format "AUD-0174".
#           """
#           ...
#
#   Tu peux copier-coller le corps de tes fonctions de tools_db.py : c'est le
#   même code métier. Seul l'emballage change. C'est tout l'intérêt de
#   l'exercice — et la raison pour laquelle le test du palier 4 vérifie que les
#   deux chemins renvoient bien la même chose.


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
