# 📍 routers/crypto/price.py
import logging
from fastapi import APIRouter, HTTPException, Query
from lib.coingecko import get_current_price  # ✅ import yang diperlukan

price_router = APIRouter()  # 🔹 router khusus untuk price
logger = logging.getLogger(__name__)


@price_router.get(
    "/price",
    summary="Get Token Price",
    description="Get the real-time price of a token in IDR. The token symbol should be provided (e.g., BTC, ETH, SOL).",
)
async def get_token_price(
    token: str = Query(
        ...,
        description="Token symbol to fetch the current price for, e.g., BTC, ETH, SOL",
    )
):
    """
    Fetch the current real-time price of a token in Indonesian Rupiah (IDR).

    - **token**: The token symbol to get the price for (e.g., BTC, ETH, SOL)
    """
    try:
        price = await get_current_price(token)
        if price == 0:
            raise HTTPException(
                status_code=404, detail=f"Price for {token.upper()} is not available"
            )
        return {"status": "success", "token": token.upper(), "price_idr": price}
    except Exception as e:
        logger.error(f"❌ Failed to fetch token price: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
