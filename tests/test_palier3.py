"""Palier 3 — historique client et création de commande."""

import pytest

from conftest import CASQUE_SKU, CLIENT_EMAIL, EMAIL_INCONNU, SKU_INCONNU

pytestmark = pytest.mark.palier3


def test_get_customer_orders(api_joignable):
    from shop_agent.tools_api import get_customer_orders

    result = get_customer_orders(CLIENT_EMAIL)

    assert result["status"] == "success"
    assert result["orders"], f"{CLIENT_EMAIL} a des commandes dans le seed."
    order = result["orders"][0]
    assert {"order_id", "status", "total_eur"} <= set(order)
    assert isinstance(order["total_eur"], float)
    assert order["total_eur"] < 100_000, "Les montants doivent être en euros, pas en centimes."


def test_get_customer_orders_email_inconnu(api_joignable):
    from shop_agent.tools_api import get_customer_orders

    result = get_customer_orders(EMAIL_INCONNU)

    assert result["status"] == "error"
    assert "message" in result


def test_create_order_nominal(api_joignable):
    from shop_agent.tools_api import create_order
    from shop_agent.tools_db import check_stock

    avant = check_stock(CASQUE_SKU)["total_sellable"]
    result = create_order(CLIENT_EMAIL, CASQUE_SKU, 1)

    assert result["status"] == "success", f"La commande aurait dû passer : {result}"
    assert isinstance(result["order_id"], int)
    assert result["total_eur"] > 0

    apres = check_stock(CASQUE_SKU)["total_sellable"]
    assert apres == avant - 1, "Une commande doit réserver le stock correspondant."


def test_create_order_rupture_de_stock_est_une_erreur_metier(api_joignable):
    from shop_agent.tools_api import create_order

    result = create_order(CLIENT_EMAIL, CASQUE_SKU, 100)

    assert result["status"] == "error", (
        "Une rupture de stock n'est pas un crash : c'est une réponse normale de la "
        "boutique. Elle doit revenir en valeur de retour pour que l'agent propose "
        "une alternative à l'utilisateur."
    )
    assert "available_quantity" in result, (
        "Dis au LLM combien d'exemplaires sont réellement disponibles : il pourra "
        "proposer d'en commander moins."
    )


def test_create_order_sku_inconnu(api_joignable):
    from shop_agent.tools_api import create_order

    result = create_order(CLIENT_EMAIL, SKU_INCONNU, 1)

    assert result["status"] == "error"


def test_create_order_client_inconnu(api_joignable):
    from shop_agent.tools_api import create_order

    result = create_order(EMAIL_INCONNU, CASQUE_SKU, 1)

    assert result["status"] == "error"


def test_l_agent_expose_bien_ses_tools():
    from shop_agent.agent import root_agent

    noms = {getattr(t, "__name__", getattr(t, "name", "")) for t in root_agent.tools}
    attendus = {
        "search_products", "get_product", "check_stock",
        "top_rated_products", "get_customer_orders", "create_order",
    }
    manquants = attendus - noms
    assert not manquants, f"Tools non branchés sur root_agent : {sorted(manquants)}"


def test_l_instruction_protege_la_commande():
    """Un tool d'écriture sans garde-fou dans l'instruction, c'est un accident qui attend."""
    from shop_agent.agent import root_agent

    instruction = root_agent.instruction or ""

    assert "TODO" not in instruction, (
        "Il reste un TODO dans l'INSTRUCTION de ton agent. Le palier 3 ne se joue "
        "pas qu'en Python : remplace les consignes par les vraies règles que "
        "l'agent doit suivre avant de passer une commande."
    )
    minuscules = instruction.lower()
    assert any(mot in minuscules for mot in ("confirm", "valide")), (
        "L'instruction de l'agent doit lui imposer une confirmation explicite de "
        "l'utilisateur avant d'appeler create_order."
    )
    assert "check_stock" in minuscules, (
        "L'instruction doit aussi lui imposer de vérifier le stock AVANT de "
        "commander : le modèle ne le fera pas spontanément."
    )
