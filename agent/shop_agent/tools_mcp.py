"""Branchement du serveur MCP sur l'agent — exercice 4.

Un `McpToolset` n'est pas un tool mais un *catalogue* de tools. ADK ouvre une
session vers le serveur MCP, lui demande la liste de ce qu'il sait faire, et
expose chaque entrée au LLM comme s'il s'agissait d'un tool natif. Rien n'est à
déclarer manuellement : ce que le serveur publie, l'agent le voit.
"""

from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from .config import MCP_SERVER_URL

shop_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
    # Filet de sécurité : même si le serveur publiait d'autres tools un jour,
    # l'agent ne verra que ceux-ci.
    tool_filter=["check_stock", "top_rated_products"],
)
