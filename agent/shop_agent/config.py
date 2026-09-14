"""Configuration FOURNIE — tu n'as pas besoin de la modifier.

Elle lit les variables d'environnement injectées par docker-compose et expose
deux helpers que tes tools utiliseront : `shop_api()` et `db_connection()`.
"""

import os

import httpx
import psycopg
from psycopg.rows import dict_row

# http://api:8000 depuis le conteneur agent.
# Attention : depuis TON navigateur c'est http://localhost:8080. Ce n'est pas la
# même adresse, et c'est l'erreur numéro un de ce TP.
SHOP_API_URL = os.environ.get("SHOP_API_URL", "http://api:8000")
SHOP_API_KEY = os.environ.get("SHOP_API_KEY", "tp-adk-2026")
SHOP_DB_URL = os.environ.get("SHOP_DB_URL", "postgresql://student:student@db:5432/shop")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp:9000/mcp")


def shop_api() -> httpx.Client:
    """Client HTTP préconfiguré : bonne URL de base, clé d'API, timeout.

    À utiliser comme ceci :

        with shop_api() as client:
            response = client.get("/products", params={"q": "casque"})
    """
    return httpx.Client(
        base_url=SHOP_API_URL,
        headers={"X-API-Key": SHOP_API_KEY},
        timeout=10.0,
    )


def db_connection() -> psycopg.Connection:
    """Connexion Postgres en LECTURE SEULE (rôle `student`).

    Les lignes sont renvoyées sous forme de dictionnaires. À utiliser ainsi :

        with db_connection() as conn:
            rows = conn.execute("SELECT ...", (param,)).fetchall()
    """
    return psycopg.connect(SHOP_DB_URL, row_factory=dict_row)


def euros(cents: int) -> float:
    """Convertit des centimes en euros. L'API parle en centimes, pas les humains."""
    return round(cents / 100, 2)
