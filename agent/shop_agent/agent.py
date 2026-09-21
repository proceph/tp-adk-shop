"""L'agent du shop — c'est ici que tout se branche.

`adk web` recherche une variable nommée exactement `root_agent` dans ce fichier.
La renommer fait disparaître l'agent de l'interface.
"""

from google.adk.agents import LlmAgent

from .tools_api import create_order, get_customer_orders, get_product, search_products
from .tools_db import check_stock, top_rated_products

# TODO EXERCICE 0 — lire cette instruction, puis revenir l'enrichir à l'exercice 3.
#
# L'instruction est le « contrat de travail » de l'agent. Tout ce qui n'y figure
# pas sera décidé par le modèle, sans contrôle.
INSTRUCTION = """
Tu es l'assistant de vente d'une boutique en ligne d'électronique. Tu réponds en
français, de façon brève et concrète.

Règles de travail :
- Tu ne connais RIEN du catalogue de toi-même. Toute information sur un produit,
  un prix, un stock ou une commande doit venir d'un appel de tool. N'invente
  jamais une référence, un prix ou une disponibilité.
- Cite toujours la référence (SKU) du produit dont tu parles.

TODO EXERCICE 3 — ajouter ici les garde-fous de la commande.
Un tool qui écrit dans le monde réel sans garde-fou est un accident en attente.
Décrire précisément ce que l'agent doit faire AVANT d'appeler create_order :
vérifier le stock ? récapituler ? attendre une confirmation explicite de
l'utilisateur ? Ces règles doivent être écrites noir sur blanc — le modèle ne
devinera pas ce qui n'est pas formulé.
"""

root_agent = LlmAgent(
    # Modèle figé volontairement : la valeur par défaut d'ADK change selon les versions.
    model="gemini-2.5-flash",
    name="shop_agent",
    description="Assistant de vente : catalogue, stock, avis clients et commandes.",
    instruction=INSTRUCTION,
    # TODO EXERCICE 1 — ajouter les tools au fur et à mesure de leur écriture.
    # Commencer par une liste VIDE : converser d'abord avec l'agent sans aucun
    # tool, et observer ce qu'il invente lorsqu'on lui demande un prix. C'est le
    # point de départ du TP.
    tools=[],
)
