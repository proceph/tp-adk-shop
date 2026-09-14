"""Branchement du serveur MCP sur l'agent — PALIER 4 (bonus).

Tes tools du palier 2 ne vivent que dans ton agent ADK. Un serveur MCP, lui, est
un service autonome que n'importe quel client compatible peut consommer : ton
agent ADK, mais aussi Claude Code, un IDE, l'agent d'un collègue écrit dans un
autre framework. C'est la différence entre écrire une fonction et publier une API.

Commence par le serveur : mcp_server/server.py. Reviens ici ensuite.
"""

# TODO PALIER 4 — branche le serveur MCP.
#
#   1. Les imports (attention, ce ne sont PAS ceux de la doc officielle, qui est
#      en retard d'une version) :
#
#          from google.adk.tools import McpToolset
#          from google.adk.tools.mcp_tool.mcp_session_manager import (
#              StreamableHTTPConnectionParams,
#          )
#          from .config import MCP_SERVER_URL
#
#   2. Crée un `shop_mcp_toolset = McpToolset(connection_params=...)` en lui
#      passant l'URL du serveur.
#
#   3. Un McpToolset n'est pas un tool : c'est un CATALOGUE de tools. ADK ouvre
#      une session vers le serveur, lui demande ce qu'il sait faire, et expose
#      chaque entrée au LLM. Tu ne déclares rien à la main.
#
#   4. Dans agent.py, remplace tes deux function tools du palier 2 par ce
#      toolset. L'agent doit se comporter exactement pareil : même capacités,
#      autre emballage.
#
#   5. N'oublie pas de démarrer le serveur : make mcp
