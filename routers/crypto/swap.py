# 📍 routers/crypto/swap.py
import logging
import httpx
from fastapi import APIRouter, HTTPException, Query

swap_router = APIRouter()
logger = logging.getLogger(__name__)

# Mapping token ke CoinGecko ID
COINGECKO_IDS = {
    "sol": "solana",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "usdt": "tether",
    "usdc": "usd-coin",
    "trx": "tron",
    "ton": "the-open-network",
}


async def get_token_price_usd(token: str) -> float:
    """Fetch the token price in USD from CoinGecko"""
    token_id = COINGECKO_IDS.get(token.lower())
    if not token_id:
        raise HTTPException(status_code=400, detail=f"Token {token} is not supported")

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        data = resp.json()
        price = data.get(token_id, {}).get("usd")

        if price is None:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch price for {token}"
            )

        return price


@swap_router.post(
    "/swap/simulasi",
    summary="Simulate Token Swap",
    description=(
        "Simulate swapping one token to another based on real-time CoinGecko prices. "
        "This is a simulation only and does not execute an actual transaction."
    ),
)
async def swap_tokens(
    from_token: str = Query(
        ..., description="Token symbol to swap from, e.g., SOL, ETH, USDT"
    ),
    to_token: str = Query(
        ..., description="Token symbol to swap to, e.g., ETH, USDC, SOL"
    ),
    amount: float = Query(..., description="Amount of the from_token to swap"),
):
    """
    Simulate swapping tokens from one type to another using real-time prices from CoinGecko.

    - **from_token**: Token symbol to swap from
    - **to_token**: Token symbol to swap to
    - **amount**: Amount of from_token to swap
    - **Note**: This is a simulation; no actual blockchain transaction is executed.
    """
    try:
        price_from = await get_token_price_usd(from_token)
        price_to = await get_token_price_usd(to_token)

        swapped_amount = (amount * price_from) / price_to
        swapped_amount = swapped_amount * 0.99  # apply 1% fee for simulation

        logger.info(
            f"Simulated Swap {amount} {from_token} → {swapped_amount:.6f} {to_token}"
        )

        return {
            "status": "success",
            "from_token": from_token,
            "to_token": to_token,
            "swapped_amount": round(swapped_amount, 6),
            "price_from_usd": price_from,
            "price_to_usd": price_to,
        }

    except Exception as e:
        logger.error(f"❌ Swap simulation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
