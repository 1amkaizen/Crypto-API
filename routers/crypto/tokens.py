# 📍 routers/crypto/tokens.py
import logging
from fastapi import APIRouter  # import yang diperlukan

tokens_router = APIRouter()  # router khusus untuk tokens
logger = logging.getLogger(__name__)


@tokens_router.get(
    "/tokens",
    summary="Get Supported Tokens",
    description=(
        "Retrieve a list of tokens and blockchains supported by this API. "
        "Clients can use this list to know which tokens are available for "
        "features like token swaps, sending native tokens, or other crypto operations."
    ),
)
async def get_supported_tokens():
    """
    Return the list of tokens and blockchains supported by the API.

    This helps clients to determine which tokens can be used with
    various crypto functionalities such as swap, send native, and more.
    """
    # List of supported tokens
    tokens = ["BASE", "SOL", "ETH", "BNB", "TRX"]

    # Logging
    logger.info("📌 Request for supported tokens list")

    return {"status": "success", "tokens": tokens}
