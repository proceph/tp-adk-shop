"""Configuration des tests — BRANCHE SOLUTION UNIQUEMENT.

Ces tests ne font pas partie du TP : les élèves vérifient leur travail en
conversant avec l'agent. Ils servent de filet de régression au corrigé,
typiquement après une montée de version d'ADK.

Ils appellent directement les fonctions du corrigé, sans passer par le LLM, et
sont donc entièrement déterministes.

Exécution : `make check`, ou `make check1` … `make check4` par exercice.
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
    # ADK émet de nombreux avertissements sur ses features expérimentales.
    # On les masque, pour que seules les erreurs réelles restent visibles.
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
