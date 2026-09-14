"""Palier 2 — les tools qui lisent directement la base Postgres."""

import pytest

from conftest import CASQUE_SKU, SKU_INCONNU

pytestmark = pytest.mark.palier2


def test_check_stock_renvoie_un_stock_coherent(api_joignable):
    from shop_agent.tools_db import check_stock

    result = check_stock(CASQUE_SKU)

    assert result["status"] == "success"
    assert result["total_sellable"] >= 0
    assert result["warehouses"], "Ce produit est stocké dans au moins un entrepôt."
    assert result["total_sellable"] == sum(w["sellable"] for w in result["warehouses"]), (
        "total_sellable doit être la somme des entrepôts."
    )


def test_check_stock_tient_compte_des_reservations(api_joignable):
    """Le stock vendable, c'est disponible MOINS réservé — pas juste disponible."""
    import psycopg
    from psycopg.rows import dict_row

    from shop_agent.config import SHOP_DB_URL
    from shop_agent.tools_db import check_stock

    with psycopg.connect(SHOP_DB_URL, row_factory=dict_row) as conn:
        row = conn.execute(
            """SELECT sum(i.quantity_available) AS dispo,
                      sum(i.quantity_available - i.quantity_reserved) AS vendable
               FROM inventory i JOIN products p ON p.id = i.product_id
               WHERE p.sku = %s""",
            (CASQUE_SKU,),
        ).fetchone()

    assert check_stock(CASQUE_SKU)["total_sellable"] == row["vendable"], (
        "Attention : quantity_available compte aussi les articles déjà réservés "
        "par d'autres commandes. Le stock réellement vendable, c'est "
        "quantity_available - quantity_reserved."
    )


def test_check_stock_sku_inconnu(api_joignable):
    from shop_agent.tools_db import check_stock

    result = check_stock(SKU_INCONNU)

    assert result["status"] == "error"
    assert "message" in result


def test_top_rated_products_est_trie_par_note(api_joignable):
    from shop_agent.tools_db import top_rated_products

    result = top_rated_products(limit=5)

    assert result["status"] == "success"
    notes = [p["average_rating"] for p in result["products"]]
    assert notes == sorted(notes, reverse=True), "Les mieux notés d'abord."
    assert all(1 <= n <= 5 for n in notes)


def test_top_rated_products_ignore_les_produits_a_un_seul_avis(api_joignable):
    from shop_agent.tools_db import top_rated_products

    result = top_rated_products(limit=10)

    assert all(p["review_count"] >= 3 for p in result["products"]), (
        "Un produit noté 5/5 par une seule personne n'est pas 'le mieux noté'. "
        "Filtre sur un nombre minimum d'avis (HAVING count(...) >= 3)."
    )


def test_top_rated_products_filtre_par_categorie(api_joignable):
    from shop_agent.tools_db import top_rated_products

    result = top_rated_products(category="audio", limit=5)

    assert result["status"] == "success"
    assert all(p["category"] == "audio" for p in result["products"])


def test_le_role_student_est_bien_en_lecture_seule():
    """Garde-fou : si ce test passe au rouge, la config de la base a dérivé."""
    import psycopg

    from shop_agent.config import SHOP_DB_URL

    with psycopg.connect(SHOP_DB_URL) as conn, pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("DELETE FROM products WHERE sku = 'AUD-0174'")
