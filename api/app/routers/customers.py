from fastapi import APIRouter

from ..db import query, query_one
from ..errors import ShopError

router = APIRouter(tags=["customers"])


def _customer_or_404(email: str) -> dict:
    customer = query_one(
        "SELECT id, email, full_name, city, loyalty_tier FROM customers WHERE lower(email) = lower(%s)",
        (email,),
    )
    if not customer:
        raise ShopError(404, "unknown_customer", f"Aucun client avec l'email {email}.", {"email": email})
    return customer


@router.get("/customers/{email}", summary="Fiche client")
def get_customer(email: str):
    customer = _customer_or_404(email)
    customer.pop("id")
    return customer


@router.get("/customers/{email}/orders", summary="Commandes d'un client")
def get_customer_orders(email: str):
    customer = _customer_or_404(email)
    orders = query(
        """SELECT o.id AS order_id, o.status, o.total_cents, o.created_at
           FROM orders o WHERE o.customer_id = %s ORDER BY o.created_at DESC""",
        (customer["id"],),
    )
    for order in orders:
        order["items"] = query(
            """SELECT p.sku, p.name, oi.quantity, oi.unit_price_cents
               FROM order_items oi JOIN products p ON p.id = oi.product_id
               WHERE oi.order_id = %s""",
            (order["order_id"],),
        )
    return {"customer_email": customer["email"], "orders": orders, "total": len(orders)}
