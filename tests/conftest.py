# tests/conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from web3 import Web3

@pytest.fixture
def mock_database():
    """Фикстура для мока базы данных"""
    db = MagicMock()
    db.save_opportunity.return_value = 1
    db.save_trade.return_value = True
    db.save_error.return_value = True
    db.get_recent_trades.return_value = []
    db.get_daily_profit.return_value = 0.0
    return db

@pytest.fixture
def mock_web3():
    web3 = MagicMock()
    web3.eth.gas_price = 1000000000
    web3.eth.get_transaction_count.return_value = 0
    web3.eth.estimate_gas.return_value = 21000
    web3.eth.send_raw_transaction.return_value = b'mock_tx_hash'
    
    mock_receipt = MagicMock()
    mock_receipt.status = 1
    mock_receipt.gasUsed = 21000
    web3.eth.wait_for_transaction_receipt.return_value = mock_receipt
    
    return web3

@pytest.fixture
def mock_dex():
    dex = MagicMock()
    dex.name = 'quickswap'
    dex.fee = 0.003
    dex.router_contract.functions.getAmountsOut.return_value.call.return_value = [
        10**18, 1010000
    ]
    return dex