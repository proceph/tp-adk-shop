"""Format d'erreur unique pour toute l'API.

Toutes les erreurs sortent sous la forme :
    {"error": {"code": "...", "message": "...", "details": {...}}}

C'est volontaire : un connecteur bien écrit s'appuie sur le `code` (stable,
machine) et non sur le `message` (humain, susceptible de changer).
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ShopError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


async def shop_error_handler(_request: Request, exc: ShopError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
