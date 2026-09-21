"""API du shop — FOURNIE, à ne pas modifier pendant le TP.

C'est le système existant auquel l'agent doit se connecter. Elle se comporte
comme une vraie API interne : clé d'API, pagination, prix en centimes, codes
d'erreur métier. Le travail consiste à écrire le connecteur qui va avec.

Documentation interactive : http://localhost:8080/docs
"""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header

from .db import pool
from .errors import ShopError, shop_error_handler
from .routers import customers, orders, products

API_KEY = os.environ.get("SHOP_API_KEY", "tp-adk-2026")


def require_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    """Toutes les routes métier exigent l'en-tête X-API-Key."""
    if x_api_key != API_KEY:
        raise ShopError(401, "unauthorized", "En-tête X-API-Key manquant ou invalide.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    pool.open()
    pool.wait(timeout=30)
    yield
    pool.close()


app = FastAPI(
    title="Shop API — TP ADK",
    version="1.0.0",
    description=__doc__,
    lifespan=lifespan,
)
app.add_exception_handler(ShopError, shop_error_handler)


@app.get("/health", tags=["meta"], summary="Sonde de santé (sans clé d'API)")
def health():
    return {"status": "ok"}


for router in (products.router, customers.router, orders.router):
    app.include_router(router, dependencies=[Depends(require_api_key)])
