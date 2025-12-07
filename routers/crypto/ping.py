# 📍 routers/crypto/ping.py
import logging
from fastapi import APIRouter

ping_router = APIRouter()
logger = logging.getLogger(__name__)


@ping_router.get(
    "/ping",
    summary="Ping API",
    description="Check if the Crypto API service is online and reachable.",
)
async def ping():
    """
    Check the status of the Crypto API service.

    Returns:
    - **status**: "ok" if API is active
    - **message**: Informational message confirming the API is running
    """
    return {"status": "ok", "message": "Crypto API is active"}
