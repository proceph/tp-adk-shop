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


# TODO EXERCICE 4 — publier les deux tools.
#
#   Le décorateur @mcp.tool() suffit : FastMCP lit la signature et la docstring
#   de la fonction pour construire le schéma MCP. Le principe est exactement
#   celui des function tools ADK — la docstring est la spécification.
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
#   Le corps des fonctions de tools_db.py peut être repris tel quel : c'est le
#   même code métier, seul l'emballage change. C'est précisément l'intérêt de
#   l'exercice, et la raison pour laquelle l'agent doit se comporter à
#   l'identique une fois le serveur branché.


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
