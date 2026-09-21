"""Palier 4 (bonus) — les mêmes capacités, servies par un serveur MCP."""

import asyncio
import json

import pytest

from conftest import CASQUE_SKU

pytestmark = pytest.mark.palier4


def _tools():
    try:
        from shop_agent.tools_mcp import shop_mcp_toolset
    except ImportError:
        pytest.fail(
            "shop_agent/tools_mcp.py ne définit pas encore `shop_mcp_toolset`.\n"
            "Exercice 4 : créer le McpToolset pointant vers le serveur MCP."
        )

    async def run():
        try:
            return await shop_mcp_toolset.get_tools(), shop_mcp_toolset
        except Exception as exc:  # noqa: BLE001 — message d'aide plutôt qu'un retry
            pytest.fail(
                f"Le serveur MCP est injoignable ({exc}).\n"
                "Démarre-le avec : make mcp"
            )

    return asyncio.run(run())


def test_le_serveur_mcp_publie_les_deux_tools():
    tools, toolset = _tools()
    noms = {t.name for t in tools}

    assert {"check_stock", "top_rated_products"} <= noms, (
        f"Le serveur MCP ne publie que {sorted(noms)}. "
        "Les deux fonctions sont-elles bien décorées avec @mcp.tool() ?"
    )
    asyncio.run(toolset.close())


def test_check_stock_via_mcp_renvoie_les_memes_donnees_qu_en_direct():
    from shop_agent.tools_db import check_stock as check_stock_direct

    tools, toolset = _tools()
    tool = next(t for t in tools if t.name == "check_stock")

    brut = asyncio.run(tool.run_async(args={"sku": CASQUE_SKU}, tool_context=None))
    asyncio.run(toolset.close())

    # Un serveur MCP renvoie du contenu typé ; le JSON est dans le bloc texte.
    via_mcp = json.loads(brut["content"][0]["text"])

    assert via_mcp["status"] == "success"
    assert via_mcp["total_sellable"] == check_stock_direct(CASQUE_SKU)["total_sellable"], (
        "Passer par MCP ne change pas la réponse : c'est le même code métier, "
        "servi autrement."
    )
