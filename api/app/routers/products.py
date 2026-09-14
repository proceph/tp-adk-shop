from fastapi import APIRouter, Query

from ..db import query, query_one
from ..errors import ShopError

router = APIRouter(tags=["products"])

PRODUCT_SELECT = """
    SELECT p.sku, p.name, p.description, p.brand, c.slug AS category,
           p.price_cents
    FROM products p
    JOIN categories c ON c.id = p.category_id
"""


@router.get("/products", summary="Rechercher des produits")
def search_products(
    q: str | None = Query(None, description="Texte libre cherché dans le nom et la marque"),
    category: str | None = Query(None, description="Slug de catégorie, ex. 'audio'"),
    max_price_cents: int | None = Query(None, gt=0, description="Prix maximum, EN CENTIMES"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats par page (20 par défaut)"),
    offset: int = Query(0, ge=0),
):
    """Renvoie une page de produits.

    La réponse contient `total` : le nombre de produits qui correspondent au
    filtre, qui peut être BIEN supérieur au nombre d'éléments renvoyés.
    """
    where, params = [], []
    if q:
        where.append("(p.name ILIKE %s OR p.brand ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    if category:
        where.append("c.slug = %s")
        params.append(category)
    if max_price_cents:
        where.append("p.price_cents <= %s")
        params.append(max_price_cents)

    clause = (" WHERE " + " AND ".join(where)) if where else ""

    total = query_one(
        "SELECT count(*) AS n FROM products p JOIN categories c ON c.id = p.category_id" + clause,
        tuple(params),
    )["n"]

    items = query(
        PRODUCT_SELECT + clause + " ORDER BY p.price_cents ASC LIMIT %s OFFSET %s",
        tuple(params) + (limit, offset),
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/products/{sku}", summary="Détail d'un produit")
def get_product(sku: str):
    product = query_one(PRODUCT_SELECT + " WHERE p.sku = %s", (sku,))
    if not product:
        raise ShopError(404, "unknown_sku", f"Aucun produit avec le SKU {sku}.", {"sku": sku})
    return product


@router.get("/products/{sku}/availability", summary="Stock d'un produit, par entrepôt")
def get_availability(sku: str):
    product = query_one("SELECT id, sku, name FROM products WHERE sku = %s", (sku,))
    if not product:
        raise ShopError(404, "unknown_sku", f"Aucun produit avec le SKU {sku}.", {"sku": sku})

    rows = query(
        """SELECT warehouse, quantity_available, quantity_reserved,
                  quantity_available - quantity_reserved AS quantity_sellable
           FROM inventory WHERE product_id = %s ORDER BY warehouse""",
        (product["id"],),
    )
    return {
        "sku": product["sku"],
        "name": product["name"],
        "warehouses": rows,
        "total_sellable": sum(r["quantity_sellable"] for r in rows),
    }
