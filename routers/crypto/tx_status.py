# 📍 routers/crypto/tx_status.py
import logging
from fastapi import APIRouter, HTTPException, Query
from solana.rpc.async_api import AsyncClient as SolanaClient
from solders.signature import Signature
from web3 import AsyncWeb3, AsyncHTTPProvider
import asyncio


tx_status_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_solana_tx_status(
    tx_hash: str, rpc_url: str, max_attempts: int = 5, delay: float = 2.0
):
    """Cek status transaksi Solana hingga finalized/confirmed dengan retry"""
    from solders.signature import Signature
    from solana.rpc.async_api import AsyncClient as SolanaClient

    signature = Signature.from_string(tx_hash)
    attempt = 0
    async with SolanaClient(rpc_url) as client:
        while attempt < max_attempts:
            attempt += 1
            try:
                resp = await client.get_transaction(
                    signature, encoding="json", commitment="finalized"
                )
                tx_data = resp.value
                if tx_data is not None:
                    meta = getattr(tx_data, "meta", None)
                    if meta is not None:
                        success = meta.err is None if hasattr(meta, "err") else None
                        return {
                            "status": "success" if success else "failed",
                            "tx_hash": tx_hash,
                            "fee": getattr(meta, "fee", None),
                            "pre_balances": getattr(meta, "pre_balances", None),
                            "post_balances": getattr(meta, "post_balances", None),
                            "err": getattr(meta, "err", None),
                        }
                await asyncio.sleep(delay)
            except Exception as e:
                # log tapi lanjut retry
                logger.warning(f"Attempt {attempt} gagal cek Solana tx: {e}")
                await asyncio.sleep(delay)

    return {
        "status": "pending",
        "tx_hash": tx_hash,
        "note": f"Belum confirmed setelah {max_attempts} percobaan",
    }


@tx_status_router.get(
    "/tx_status",
    summary="Get Transaction Status",
    description=(
        "Check the status of a transaction on supported blockchains using the transaction hash. "
        "Supports Solana, Ethereum, BSC, Polygon, TRON (placeholder), and Base. "
        "RPC URL must be provided via the endpoint."
    ),
)
async def get_tx_status(
    chain: str = Query(
        ..., description="Blockchain chain: eth, bnb, polygon, sol, trx, base"
    ),
    tx_hash: str = Query(..., description="Transaction hash to query the status of"),
    rpc_url: str = Query(..., description="RPC URL for the blockchain node"),
):
    chain = chain.lower()
    try:
        if not rpc_url:
            raise HTTPException(status_code=400, detail="RPC URL harus diberikan")

        if chain == "sol":
            logger.info(f"🔹 Checking Solana tx status: {tx_hash} via {rpc_url}")
            return await get_solana_tx_status(tx_hash, rpc_url)

        elif chain in ["eth", "bnb", "polygon", "base"]:
            logger.info(
                f"🔹 Checking {chain.upper()} tx status: {tx_hash} via {rpc_url}"
            )
            w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
            receipt = await w3.eth.get_transaction_receipt(tx_hash)
            if receipt is None:
                return {"status": "pending", "tx_hash": tx_hash}
            success = receipt.status == 1
            return {
                "status": "success" if success else "failed",
                "tx_hash": tx_hash,
                "blockNumber": receipt.blockNumber,
                "gasUsed": receipt.gasUsed,
                "logs": [dict(log) for log in receipt.logs],
            }

        elif chain == "trx":
            logger.info(f"🔹 Checking TRX tx status (placeholder): {tx_hash}")
            return {
                "status": "pending",
                "tx_hash": tx_hash,
                "note": "TRX async not yet implemented",
            }

        else:
            raise HTTPException(
                status_code=400, detail=f"Chain {chain} is not supported"
            )

    except Exception as e:
        logger.error(f"❌ Failed to check tx_status [{chain}]: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
