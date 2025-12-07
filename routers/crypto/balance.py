# 📍 routers/crypto/balance.py
import logging
from fastapi import APIRouter, HTTPException, Query
from lib.balance_checker import check_balance

balance_router = APIRouter()
logger = logging.getLogger(__name__)


@balance_router.get(
    "/balance",
    summary="Get Wallet Balance",
    description="Check the balance of a wallet for a specific blockchain chain",
)
async def get_wallet_balance(
    chain: str = Query(..., description="Blockchain chain: eth, bsc, bnb, sol, trx"),
    wallet: str = Query(..., description="Wallet address to check balance"),
    rpc_url: str = Query(..., description="RPC URL for mainnet or testnet"),
):
    """
    Check wallet balance per blockchain chain.
    User must provide the RPC URL (mainnet or testnet).
    """
    try:
        bal = await check_balance(chain, wallet, rpc_url)
        return {
            "status": "success",
            "chain": chain.upper(),
            "wallet": wallet,
            "balance": bal,
        }
    except Exception as e:
        logger.error(f"❌ Failed to check balance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
