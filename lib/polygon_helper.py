# 📍 lib/polygon_helper.py
import logging
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)


def get_balance(address: str, rpc_url: str):
    """Cek saldo POLYGON dari wallet tertentu"""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise Exception("Polygon RPC tidak terkoneksi!")
        balance_wei = w3.eth.get_balance(Web3.to_checksum_address(address))
        balance_matic = w3.from_wei(balance_wei, "ether")
        logger.info(f"💰 Saldo {address}: {balance_matic} POLYGON")
        return balance_matic
    except Exception as e:
        logger.error(f"❌ Gagal cek saldo {address}: {e}", exc_info=True)
        return None


async def send_polygon(
    destination_wallet: str,
    amount_matic: float,
    rpc_url: str = None,
    private_key: str = None,
):
    """
    Kirim POLYGON ke wallet tujuan.
    rpc_url & private_key bisa dikirim dari endpoint.
    Gas fee dan gas limit otomatis dari RPC.
    """
    if not rpc_url:
        raise ValueError("❌ RPC URL harus diberikan!")
    if not private_key:
        raise ValueError("❌ Private key harus diberikan!")

    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    admin_account = Account.from_key(private_key)

    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise Exception("Polygon RPC tidak terkoneksi!")

        sender_address = admin_account.address

        if destination_wallet.lower() == sender_address.lower():
            raise Exception(
                f"Destination sama dengan source! Transaksi dibatalkan: {destination_wallet}"
            )

        sender_balance = get_balance(sender_address, rpc_url)
        if sender_balance is None or sender_balance < amount_matic:
            raise Exception(
                f"Saldo tidak cukup! Saldo sekarang {sender_balance} POLYGON"
            )

        nonce = w3.eth.get_transaction_count(sender_address)
        value = w3.to_wei(amount_matic, "ether")

        tx_dict = {
            "nonce": nonce,
            "to": Web3.to_checksum_address(destination_wallet),
            "value": value,
            "chainId": w3.eth.chain_id,
        }

        # Estimasi gas otomatis
        gas_estimate = w3.eth.estimate_gas({**tx_dict, "from": sender_address})
        tx_dict["gas"] = gas_estimate

        # Gas price otomatis dari RPC
        tx_dict["gasPrice"] = w3.eth.gas_price

        signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(
            f"✅ Kirim {amount_matic} POLYGON ke {destination_wallet}, tx_hash: {tx_hash.hex()}"
        )
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"❌ Gagal kirim POLYGON: {e}", exc_info=True)
        raise e  # crypto_sender.py yang handle notif
