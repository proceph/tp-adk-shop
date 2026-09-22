"""Tools qui parlent à l'API du shop (paliers 1 et 3).

Rappel des conventions du TP :
  1. Le NOM de la fonction et sa DOCSTRING sont ce que le LLM lit pour décider
     s'il appelle le tool. C'est de la documentation exécutable, pas du commentaire.
  2. Type hints obligatoires et simples (str, int, float, bool).
  3. On renvoie un dict contenant une clé `status`.
  4. Erreur MÉTIER attendue (rupture de stock, client inconnu) -> valeur de retour
     `{"status": "error", ...}` que le LLM saura expliquer à l'utilisateur.
     Erreur TECHNIQUE (API injoignable) -> on laisse l'exception remonter, pour
     qu'ADK applique son mécanisme de retry. Pas de `except Exception:` fourre-tout.
  5. On borne ce qu'on renvoie : un LLM n'a pas besoin de 180 produits complets.
"""

from .config import euros, shop_api

# On ne renvoie jamais les descriptions complètes au LLM : elles sont longues,
# et 180 descriptions feraient exploser la fenêtre de contexte pour rien.
DESCRIPTION_MAX = 160


def _format_product(raw: dict, with_description: bool = False) -> dict:
    formatted = {
        "sku": raw["sku"],
        "name": raw["name"],
        "brand": raw["brand"],
        "category": raw["category"],
        "price_eur": euros(raw["price_cents"]),
    }
    if with_description:
        description = raw["description"]
        if len(description) > DESCRIPTION_MAX:
            description = description[:DESCRIPTION_MAX].rstrip() + "…"
        formatted["description"] = description
    return formatted


def search_products(query: str = "", category: str = "", max_price_eur: float = 0.0) -> dict:
    """Recherche des produits dans le catalogue de la boutique.

    Utilise ce tool dès que l'utilisateur cherche un article, demande ce qui
    existe dans une gamme, ou pose une question sur les prix du catalogue.

    Args:
        query: Mots-clés cherchés dans le nom et la marque, par exemple
            "casque", "Aurora" ou "casque Orion". Chaque mot doit apparaître,
            dans n'importe quel ordre. Employer des mots-clés et jamais une
            phrase entière : "je cherche un casque pas cher" ne renvoie rien.
            Laisser vide pour ne pas filtrer sur le texte.
        category: Catégorie exacte parmi : audio, informatique, photo,
            maison-connectee, sport, gaming, telephonie, accessoires.
            Laisser vide pour toutes les catégories.
        max_price_eur: Prix maximum EN EUROS. Mettre 0 pour ne pas filtrer.

    Returns:
        Un dict avec `status`, `count` (nombre de produits renvoyés),
        `total_matching` (nombre total de produits correspondants, qui peut être
        plus grand que `count`) et `products` : une liste de produits avec leur
        sku, nom, marque, catégorie et prix en euros.
    """
    params: dict = {"limit": 20}
    if query:
        params["q"] = query
    if category:
        params["category"] = category
    if max_price_eur > 0:
        params["max_price_cents"] = int(round(max_price_eur * 100))

    with shop_api() as client:
        response = client.get("/products", params=params)
        response.raise_for_status()  # panne technique -> exception -> retry ADK
        payload = response.json()

    return {
        "status": "success",
        "count": len(payload["items"]),
        "total_matching": payload["total"],
        "products": [_format_product(item) for item in payload["items"]],
    }


def get_product(sku: str) -> dict:
    """Donne la fiche détaillée d'un produit à partir de sa référence (SKU).

    Utilise ce tool quand l'utilisateur veut des détails sur un produit précis
    dont tu connais déjà le SKU, par exemple après une recherche.

    Args:
        sku: Référence du produit, au format "AUD-0174".

    Returns:
        Un dict avec `status` et `product` (sku, nom, marque, catégorie, prix en
        euros, description). Si le SKU n'existe pas, `status` vaut "error" et
        `message` explique le problème.
    """
    with shop_api() as client:
        response = client.get(f"/products/{sku}")

    if response.status_code == 404:
        return {"status": "error", "message": f"Aucun produit ne porte la référence {sku}."}
    response.raise_for_status()

    return {"status": "success", "product": _format_product(response.json(), with_description=True)}


def get_customer_orders(email: str) -> dict:
    """Liste les commandes passées par un client, de la plus récente à la plus ancienne.

    Utilise ce tool quand l'utilisateur demande l'historique, le suivi ou le
    statut de ses commandes.

    Args:
        email: Adresse email du client, par exemple "alice@example.com".

    Returns:
        Un dict avec `status` et `orders` : pour chaque commande son numéro, son
        statut, son montant en euros et la liste des articles. Si l'email est
        inconnu, `status` vaut "error".
    """
    with shop_api() as client:
        response = client.get(f"/customers/{email}/orders")

    if response.status_code == 404:
        return {"status": "error", "message": f"Aucun client ne correspond à l'email {email}."}
    response.raise_for_status()

    payload = response.json()
    orders = [
        {
            "order_id": order["order_id"],
            "status": order["status"],
            "total_eur": euros(order["total_cents"]),
            "created_at": order["created_at"][:10],
            "items": [
                {"sku": i["sku"], "name": i["name"], "quantity": i["quantity"]}
                for i in order["items"]
            ],
        }
        for order in payload["orders"][:10]
    ]
    return {"status": "success", "count": len(orders), "orders": orders}


def create_order(customer_email: str, sku: str, quantity: int) -> dict:
    """Passe une commande pour un client. ACTION IRRÉVERSIBLE.

    N'appelle JAMAIS ce tool sans que l'utilisateur ait explicitement confirmé
    le produit, la quantité et son email. En cas de doute, pose la question.

    Args:
        customer_email: Email du client qui commande, par exemple "alice@example.com".
        sku: Référence du produit à commander, au format "AUD-0174".
        quantity: Nombre d'exemplaires, au minimum 1.

    Returns:
        Un dict avec `status`. En cas de succès : `order_id`, `total_eur` et le
        détail de la commande. En cas d'échec (stock insuffisant, client ou
        produit inconnu) : `status` vaut "error" et `message` explique pourquoi,
        avec le stock réellement disponible s'il s'agit d'une rupture.
    """
    with shop_api() as client:
        response = client.post(
            "/orders",
            json={"customer_email": customer_email, "items": [{"sku": sku, "quantity": quantity}]},
        )

    # L'API refuse les quantités hors bornes avec un 422 (format FastAPI, pas le
    # nôtre). C'est une erreur que le LLM peut corriger lui-même : on la lui dit.
    if response.status_code == 422:
        return {
            "status": "error",
            "code": "invalid_quantity",
            "message": f"La quantité {quantity} est refusée par la boutique. "
                       "Elle doit être comprise entre 1 et 100.",
        }

    # Erreurs métier attendues : on les transforme en réponse, pas en exception.
    if response.status_code in (404, 409):
        error = response.json()["error"]
        result = {"status": "error", "code": error["code"], "message": error["message"]}
        if error["code"] == "out_of_stock":
            result["available_quantity"] = error["details"]["available"]
        return result

    response.raise_for_status()
    payload = response.json()
    return {
        "status": "success",
        "order_id": payload["order_id"],
        "order_status": payload["status"],
        "total_eur": euros(payload["total_cents"]),
        "items": [
            {"sku": i["sku"], "name": i["name"], "quantity": i["quantity"]}
            for i in payload["items"]
        ],
    }
