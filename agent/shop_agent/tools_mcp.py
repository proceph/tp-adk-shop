"""Branchement du serveur MCP sur l'agent — EXERCICE 4 (bonus).

Ce fichier est fourni complet aux élèves : le travail de l'exercice 4 se situe
dans `mcp_server/server.py`.

Les tools de l'exercice 2 ne sont utilisables que depuis cet agent ADK. Un
serveur MCP, lui, est un service autonome que tout client compatible peut
consommer : un agent ADK, un IDE, Claude Code, ou l'agent d'un tiers écrit dans
un autre framework. C'est la différence entre écrire une fonction et publier
une API.

Un `McpToolset` n'est pas un tool mais un CATALOGUE de tools : ADK ouvre une
session vers le serveur, lui demande la liste de ce qu'il sait faire, et expose
chaque entrée au LLM comme s'il s'agissait d'un tool natif. Rien n'est à
déclarer manuellement — ce que le serveur publie, l'agent le voit.

Attention : ces chemins d'import ne sont PAS ceux de la documentation
officielle, qui est en retard d'une version.
"""

from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from .config import MCP_SERVER_URL

shop_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
    # Filet de sécurité : seuls ces tools seront exposés au LLM, même si le
    # serveur venait à en publier d'autres.
    tool_filter=["check_stock", "top_rated_products"],
)
