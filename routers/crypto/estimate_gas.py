# 📍 routers/crypto/estimate_gas.py
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from web3 import Web3
import httpx  # untuk Solana/TRX RPC

estimate_gas_router = APIRouter()
logger = logging.getLogger(__name__)


# ===== Response Models =====
class GasFeeResponse(BaseModel):
    status: str
    gas_fee: float

    class Config:
        json_schema_extra = {"example": {"status": "success", "gas_fee": 0.00021}}


class ErrorResponse(BaseModel):
    status: str
    detail: str

    class Config:
        json_schema_extra = {
            "example": {"status": "error", "detail": "Failed to estimate gas fee"}
        }


# ===== Helper Estimate Gas =====
async def estimate_gas_fee(token: str, chain: str, amount: float, rpc_url: str):
    token_lower = token.lower()
    chain_lower = chain.lower()

    if not rpc_url:
        raise ValueError("RPC URL harus dikirim user, tidak ada default")

    logger.info(
        f"🔧 Estimasi gas | token={token}, chain={chain}, amount={amount}, rpc={rpc_url}"
    )

    if chain_lower in ["eth", "bnb", "polygon", "base"]:
        # Web3 compatible chains
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise ValueError(f"RPC {rpc_url} tidak bisa connect")
        gas_price = w3.eth.gas_price
        gas_limit = 21000
        gas_fee = Web3.from_wei(gas_price * gas_limit, "ether")
        return float(gas_fee)

    elif chain_lower == "sol":
        # Hardcode fee per signature (Devnet/Mainnet)
        lamports_per_signature = 5000  # 0.000005 SOL per transaksi
        logger.info(f"💡 Solana fee di-hardcode: {lamports_per_signature} lamports")
        return float(lamports_per_signature / 1e9)

    elif chain_lower == "trx":
        # Hardcode fee TRX seperti Solana
        # 1 transaksi ~ 0.1 TRX, kecil banget
        lamports_per_tx = 100_000  # 0.1 TRX = 100_000 Sun
        gas_fee = lamports_per_tx / 1_000_000
        logger.info(f"💡 TRX fee di-hardcode: {gas_fee} TRX")
        return float(gas_fee)

    else:
        raise ValueError(f"Chain {chain} belum didukung untuk estimate gas")


# ===== Endpoint =====
@estimate_gas_router.get(
    "/estimate-gas",
    summary="Estimate Gas Fee",
    description="Estimate the gas fee required for sending a specific token on a selected blockchain chain.",
    response_model=GasFeeResponse,
)
async def estimate_gas(
    chain: str = Query(..., description="Blockchain chain: eth, bsc, bnb, sol, trx"),
    token: str = Query(..., description="Token symbol to send, e.g., ETH, USDT, SOL"),
    amount: float = Query(..., description="Amount of token to send"),
    rpc_url: str = Query(..., description="Custom RPC URL yang HARUS dikirim user"),
):
    if not rpc_url:
        logger.error("❌ RPC URL tidak dikirim user")
        raise HTTPException(status_code=400, detail="RPC URL harus dikirim dari user")

    try:
        gas_fee = await estimate_gas_fee(token, chain, amount, rpc_url)
        logger.info(
            f"🔹 Gas fee estimated: {gas_fee} {token.upper()} on {chain.upper()}"
        )
        return {"status": "success", "gas_fee": gas_fee}
    except Exception as e:
        logger.error(f"❌ Failed to estimate gas fee: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
