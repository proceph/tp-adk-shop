"""Palier 1 — les tools qui interrogent le catalogue via l'API REST."""

import pytest

from conftest import CASQUE_NAME, CASQUE_PRICE_EUR, CASQUE_SKU, NB_PRODUITS_TOTAL, SKU_INCONNU

pytestmark = pytest.mark.palier1


def test_search_products_trouve_des_casques(api_joignable):
    from shop_agent.tools_api import search_products

    result = search_products(query="casque")

    assert result["status"] == "success", "Le tool doit renvoyer status='success'."
    assert result["products"], "La recherche 'casque' doit remonter des produits."
    assert all("casque" in p["name"].lower() for p in result["products"])


def test_search_products_filtre_sur_le_prix_en_euros(api_joignable):
    from shop_agent.tools_api import search_products

    result = search_products(query="casque", max_price_eur=100)

    assert result["products"], "Il existe des casques à moins de 100 €."
    assert all(p["price_eur"] <= 100 for p in result["products"]), (
        "max_price_eur est en EUROS, mais l'API attend des CENTIMES : "
        "la conversion manque."
    )


def test_search_products_annonce_le_total(api_joignable):
    from shop_agent.tools_api import search_products

    result = search_products()

    assert result["total_matching"] == NB_PRODUITS_TOTAL, (
        f"Le catalogue contient {NB_PRODUITS_TOTAL} produits. Le tool doit renvoyer ce total "
        "(champ `total` de l'API), sinon l'agent croira qu'il n'y en a que 20."
    )
    assert result["count"] <= result["total_matching"]


def test_search_products_ne_renvoie_pas_les_descriptions(api_joignable):
    from shop_agent.tools_api import search_products

    result = search_products(query="casque")

    assert not any("description" in p for p in result["products"]), (
        "Une liste de résultats n'a pas besoin des descriptions complètes : "
        "c'est du contexte gaspillé pour le LLM."
    )


def test_get_product_renvoie_la_fiche(api_joignable):
    from shop_agent.tools_api import get_product

    result = get_product(CASQUE_SKU)

    assert result["status"] == "success"
    product = result["product"]
    assert product["sku"] == CASQUE_SKU
    assert product["name"] == CASQUE_NAME
    assert product["price_eur"] == CASQUE_PRICE_EUR, (
        f"Le prix doit être en euros ({CASQUE_PRICE_EUR}), pas en centimes."
    )


def test_get_product_sku_inconnu_renvoie_une_erreur_lisible(api_joignable):
    from shop_agent.tools_api import get_product

    result = get_product(SKU_INCONNU)

    assert result["status"] == "error", (
        "Un SKU inconnu est une erreur MÉTIER attendue : elle doit sortir en valeur de "
        "retour, pas en exception, pour que le LLM puisse l'expliquer à l'utilisateur."
    )
    assert "message" in result
