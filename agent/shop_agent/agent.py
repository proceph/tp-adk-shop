"""L'agent du shop — c'est ici que tout se branche.

`adk web` recherche une variable nommée exactement `root_agent` dans ce fichier.
La renommer fait disparaître l'agent de l'interface.

AU DÉMARRAGE DU TP, LA LISTE `tools` EST VIDE : l'agent ne dispose d'aucun
moyen d'accéder au catalogue. C'est volontaire — l'exercice 0 consiste à
constater ce qu'il répond dans cet état.

Chaque tool s'active ensuite en décommentant UNE ligne dans `tools=[...]`, dans
l'ordre des exercices. Deux d'entre eux sont déjà écrits et fonctionnels : il
suffit de les décommenter. Les autres sont à implémenter avant d'être activés.
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
    tools=[
        # ┌──────────────────────────────────────────────────────────────────┐
        # │ Décommenter les lignes UNE PAR UNE, dans l'ordre des exercices,  │
        # │ et reparler à l'agent après chaque activation.                   │
        # │                                                                  │
        # │ Activer un tool encore marqué « à écrire » fera échouer l'agent  │
        # │ en pleine conversation.                                          │
        # └──────────────────────────────────────────────────────────────────┘

        # Exercice 1 — première activation. Ce tool est DÉJÀ ÉCRIT et
        # fonctionnel : le décommenter suffit à voir l'agent changer de
        # comportement. C'est le point de bascule du TP.
        search_products,

        # Exercice 1 — à écrire dans tools_api.py, puis activer ici.
        # get_product,

        # Exercice 2 — également DÉJÀ ÉCRIT : accès direct à la base.
        # check_stock,

        # Exercice 2 — à écrire dans tools_db.py, puis activer ici.
        # top_rated_products,

        # Exercice 3 — à écrire dans tools_api.py, puis activer ici.
        # get_customer_orders,
        # create_order,
    ],
)

# ── EXERCICE 4 (bonus) — passer par le serveur MCP ────────────────────────────
#
# Une fois `mcp_server/server.py` complété et le serveur démarré (`make mcp`),
# décommenter le bloc ci-dessous. Il retire les deux tools d'accès direct à la
# base et les remplace par leurs équivalents servis en MCP.
#
# Le comportement de l'agent doit rester strictement identique : seul le mode
# d'accès aux données change.
#
# from .tools_mcp import shop_mcp_toolset
#
# root_agent.tools = [
#     search_products,
#     get_customer_orders,
#     create_order,
#     shop_mcp_toolset,      # remplace check_stock et top_rated_products
# ]
