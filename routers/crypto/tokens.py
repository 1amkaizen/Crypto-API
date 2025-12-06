# 📍 routers/crypto/tokens.py
import logging
from fastapi import APIRouter  # import yang diperlukan

tokens_router = APIRouter()  # router khusus untuk tokens
logger = logging.getLogger(__name__)


@tokens_router.get("/tokens")
async def get_supported_tokens():
    """
    Endpoint untuk menampilkan daftar token/blockchain yang didukung API ini.
    Digunakan untuk memastikan client mengetahui token apa saja yang dapat
    digunakan pada fitur swap, kirim native, ataupun fungsi crypto lainnya.
    """
    # daftar token yang disupport
    tokens = ["BASE", "SOL", "ETH", "BNB", "TRX"]

    # logging
    logger.info("📌 Request daftar token yang didukung")

    return {"status": "success", "tokens": tokens}
