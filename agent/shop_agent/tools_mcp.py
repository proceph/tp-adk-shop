"""Branchement du serveur MCP sur l'agent — EXERCICE 4 (bonus).

Les tools de l'exercice 2 ne sont utilisables que depuis cet agent ADK. Un
serveur MCP, lui, est un service autonome que tout client compatible peut
consommer : un agent ADK, un IDE, Claude Code, ou l'agent d'un tiers écrit dans
un autre framework. C'est la différence entre écrire une fonction et publier une
API.

Commencer par le serveur : mcp_server/server.py. Revenir ici ensuite.
"""

# TODO EXERCICE 4 — brancher le serveur MCP.
#
#   1. Les imports (attention, ce ne sont PAS ceux de la documentation
#      officielle, en retard d'une version) :
#
#          from google.adk.tools import McpToolset
#          from google.adk.tools.mcp_tool.mcp_session_manager import (
#              StreamableHTTPConnectionParams,
#          )
#          from .config import MCP_SERVER_URL
#
#   2. Créer un `shop_mcp_toolset = McpToolset(connection_params=...)` en lui
#      passant l'URL du serveur.
#
#   3. Un McpToolset n'est pas un tool mais un CATALOGUE de tools : ADK ouvre une
#      session vers le serveur, lui demande la liste de ce qu'il sait faire, et
#      expose chaque entrée au LLM. Rien n'est à déclarer manuellement.
#
#   4. Dans agent.py, remplacer les deux function tools de l'exercice 2 par ce
#      toolset. Le comportement de l'agent doit rester identique : mêmes
#      capacités, autre mode d'accès.
#
#   5. Ne pas oublier de démarrer le serveur : make mcp
