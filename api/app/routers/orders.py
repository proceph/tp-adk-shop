from fastapi import APIRouter
from psycopg.rows import dict_row

from ..db import pool, query, query_one
from ..errors import ShopError
from ..models import OrderIn

router = APIRouter(tags=["orders"])


@router.post("/orders", status_code=201, summary="Créer une commande")
def create_order(payload: OrderIn):
    """Crée une commande pour un client.

    Codes d'erreur possibles :
      - 404 `unknown_customer` : l'email ne correspond à aucun client
      - 404 `unknown_sku`      : un des SKU n'existe pas
      - 409 `out_of_stock`     : stock vendable insuffisant pour un des articles
    """
    with pool.connection() as conn:
        conn.row_factory = dict_row
        with conn.transaction():
            customer = conn.execute(
                "SELECT id, email FROM customers WHERE lower(email) = lower(%s)",
                (payload.customer_email,),
            ).fetchone()
            if not customer:
                raise ShopError(
                    404, "unknown_customer",
                    f"Aucun client avec l'email {payload.customer_email}.",
                    {"email": payload.customer_email},
                )

            lines = []
            for item in payload.items:
                product = conn.execute(
                    "SELECT id, sku, name, price_cents FROM products WHERE sku = %s", (item.sku,)
                ).fetchone()
                if not product:
                    raise ShopError(
                        404, "unknown_sku", f"Aucun produit avec le SKU {item.sku}.", {"sku": item.sku}
                    )

                sellable = conn.execute(
                    """SELECT COALESCE(sum(quantity_available - quantity_reserved), 0) AS n
                       FROM inventory WHERE product_id = %s""",
                    (product["id"],),
                ).fetchone()["n"]

                if sellable < item.quantity:
                    raise ShopError(
                        409, "out_of_stock",
                        f"Stock insuffisant pour {product['sku']} : {item.quantity} demandé(s), "
                        f"{sellable} disponible(s).",
                        {"sku": product["sku"], "requested": item.quantity, "available": sellable},
                    )

                lines.append((product, item.quantity))

            total = sum(p["price_cents"] * qty for p, qty in lines)
            order = conn.execute(
                """INSERT INTO orders (customer_id, status, total_cents)
                   VALUES (%s, 'pending', %s) RETURNING id, status, total_cents, created_at""",
                (customer["id"], total),
            ).fetchone()

            for product, qty in lines:
                conn.execute(
                    """INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents)
                       VALUES (%s, %s, %s, %s)""",
                    (order["id"], product["id"], qty, product["price_cents"]),
                )
                # On réserve le stock sur les entrepôts, du plus fourni au moins fourni.
                remaining = qty
                rows = conn.execute(
                    """SELECT warehouse, quantity_available - quantity_reserved AS sellable
                       FROM inventory WHERE product_id = %s
                       ORDER BY quantity_available - quantity_reserved DESC""",
                    (product["id"],),
                ).fetchall()
                for row in rows:
                    if remaining <= 0:
                        break
                    take = min(remaining, row["sellable"])
                    if take <= 0:
                        continue
                    conn.execute(
                        """UPDATE inventory SET quantity_reserved = quantity_reserved + %s
                           WHERE product_id = %s AND warehouse = %s""",
                        (take, product["id"], row["warehouse"]),
                    )
                    remaining -= take

    return {
        "order_id": order["id"],
        "customer_email": customer["email"],
        "status": order["status"],
        "total_cents": order["total_cents"],
        "created_at": order["created_at"],
        "items": [
            {"sku": p["sku"], "name": p["name"], "quantity": q, "unit_price_cents": p["price_cents"]}
            for p, q in lines
        ],
    }


@router.get("/orders/{order_id}", summary="Détail d'une commande")
def get_order(order_id: int):
    order = query_one(
        """SELECT o.id AS order_id, c.email AS customer_email, o.status,
                  o.total_cents, o.created_at
           FROM orders o JOIN customers c ON c.id = o.customer_id
           WHERE o.id = %s""",
        (order_id,),
    )
    if not order:
        raise ShopError(404, "unknown_order", f"Aucune commande {order_id}.", {"order_id": order_id})

    order["items"] = query(
        """SELECT p.sku, p.name, oi.quantity, oi.unit_price_cents
           FROM order_items oi JOIN products p ON p.id = oi.product_id
           WHERE oi.order_id = %s""",
        (order_id,),
    )
    return order
