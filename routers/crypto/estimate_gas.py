# 📍 routers/crypto/estimate_gas.py
import logging
from fastapi import APIRouter, HTTPException, Query
from lib.native_sender import estimate_gas_fee  # ✅ import yang diperlukan

estimate_gas_router = APIRouter()  # 🔹 router khusus untuk estimate gas
logger = logging.getLogger(__name__)


@estimate_gas_router.get(
    "/estimate-gas",
    summary="Estimate Gas Fee",
    description="Estimate the gas fee required for sending a specific token to a destination wallet on a selected blockchain chain.",
)
async def estimate_gas(
    chain: str = Query(..., description="Blockchain chain: eth, bsc, bnb, sol, trx"),
    token: str = Query(..., description="Token symbol to send, e.g., ETH, USDT, SOL"),
    destination_wallet: str = Query(..., description="Destination wallet address"),
    amount: float = Query(..., description="Amount of token to send"),
):
    """
    Estimate the gas fee for sending a specific token on a blockchain.

    - **chain**: Blockchain chain (eth, bsc, bnb, sol, trx)
    - **token**: Token symbol to send (e.g., ETH, USDT, SOL)
    - **destination_wallet**: Wallet address to receive the token
    - **amount**: Amount of token to send
    """
    try:
        gas_fee = await estimate_gas_fee(token, chain, destination_wallet, amount)
        return {"status": "success", "gas_fee": gas_fee}
    except Exception as e:
        logger.error(f"❌ Failed to estimate gas fee: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
