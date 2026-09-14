"""L'agent du shop — c'est ici que tout se branche.

`adk web` cherche une variable nommée exactement `root_agent` dans ce fichier.
Si tu la renommes, ton agent disparaît de l'interface.
"""

from google.adk.agents import LlmAgent

from .tools_api import create_order, get_customer_orders, get_product, search_products
from .tools_db import check_stock, top_rated_products

# TODO PALIER 0 — lis cette instruction, puis reviens l'enrichir au palier 3.
#
# L'instruction est le « contrat de travail » de ton agent. Tout ce que tu n'y
# écris pas, le modèle le décidera à ta place.
INSTRUCTION = """
Tu es l'assistant de vente d'une boutique en ligne d'électronique. Tu réponds en
français, de façon brève et concrète.

Règles de travail :
- Tu ne connais RIEN du catalogue de toi-même. Toute information sur un produit,
  un prix, un stock ou une commande doit venir d'un appel de tool. N'invente
  jamais une référence, un prix ou une disponibilité.
- Cite toujours la référence (SKU) du produit dont tu parles.

TODO PALIER 3 — ajoute ici les garde-fous de la commande.
Un tool qui écrit dans le monde réel sans garde-fou, c'est un accident qui
attend son heure. Décris précisément ce que l'agent doit faire AVANT d'appeler
create_order : vérifier le stock ? récapituler ? attendre une confirmation
explicite de l'utilisateur ? Écris-le noir sur blanc — le modèle ne le devinera pas.
"""

root_agent = LlmAgent(
    # Modèle figé volontairement : le défaut d'ADK change au fil des versions.
    model="gemini-2.5-flash",
    name="shop_agent",
    description="Assistant de vente : catalogue, stock, avis clients et commandes.",
    instruction=INSTRUCTION,
    # TODO PALIER 1 — ajoute tes tools au fur et à mesure que tu les écris.
    # Commence par une liste VIDE : parle d'abord à l'agent sans aucun tool, et
    # regarde ce qu'il invente quand tu lui demandes un prix. C'est le point de
    # départ du TP.
    tools=[],
)
