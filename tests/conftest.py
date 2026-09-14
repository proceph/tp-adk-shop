"""Configuration des tests — FOURNIE, ne pas modifier.

Ces tests appellent directement TES fonctions, sans jamais passer par le LLM.
Ils sont donc 100 % déterministes : un test rouge est un vrai bug dans ton
connecteur, jamais un caprice du modèle.

Lance-les avec `make check1`, `make check2`, … ou `make check` pour tout.
"""

import sys

import pytest

sys.path.insert(0, "/app")

# Données garanties présentes par le seed de la base.
CASQUE_SKU = "AUD-0174"          # Casque filaire Orion Air, 29,80 €
CASQUE_NAME = "Casque filaire Orion Air"
CASQUE_PRICE_EUR = 29.80
CLIENT_EMAIL = "alice@example.com"
SKU_INCONNU = "ZZZ-9999"
EMAIL_INCONNU = "personne@example.com"
NB_PRODUITS_TOTAL = 180


def pytest_configure(config):
    for palier in (1, 2, 3, 4):
        config.addinivalue_line("markers", f"palier{palier}: tests du palier {palier}")
    # ADK bavarde beaucoup sur ses features expérimentales. Ce n'est pas ton problème
    # pendant le TP : on masque, pour que seules TES erreurs restent visibles.
    for rule in (
        "ignore::DeprecationWarning",
        "ignore::UserWarning",
    ):
        config.addinivalue_line("filterwarnings", rule)


@pytest.fixture(scope="session")
def api_joignable():
    """Échoue tôt et clairement si les conteneurs ne tournent pas."""
    import httpx

    try:
        httpx.get("http://api:8000/health", timeout=5).raise_for_status()
    except Exception as exc:  # noqa: BLE001 — ici on VEUT un message d'aide, pas un retry
        pytest.fail(
            f"L'API du shop est injoignable ({exc}).\n"
            "Vérifie que les conteneurs tournent : make up"
        )
