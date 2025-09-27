import asyncio
from typing import Dict, Any, Optional
from web3 import Web3
from web3.types import TxReceipt
from eth_abi import abi
from src.utils.logger import logger
from src.models.token import Token

class TransactionExecutor:
    """Модуль исполнения арбитражных сделок"""
    
    def __init__(self, web3: Web3, private_key: str, config: Dict[str, Any]):
        self.web3 = web3
        self.private_key = private_key
        self.config = config
        self.account = web3.eth.account.from_key(private_key)
    
    async def execute_arbitrage(self, opportunity: Dict[str, Any]) -> Optional[TxReceipt]:
        """Исполнение арбитражной сделки"""
        try:
            # Подготовка данных транзакции
            transaction = await self._prepare_transaction(opportunity)
            
            # Оценка газа
            gas_estimate = await self._estimate_gas(transaction)
            transaction['gas'] = int(gas_estimate * 1.2)  # Запас 20%
            
            # Установка цены газа
            gas_price = await self._get_gas_price()
            transaction['gasPrice'] = int(gas_price * self.config['gas_price_multiplier'])
            
            # Подписание транзакции
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Отправка транзакции
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Ожидание подтверждения
            receipt = await self._wait_for_transaction(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Transaction successful: {tx_hash.hex()}")
                return receipt
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to execute arbitrage: {e}")
            return None
    
    async def _prepare_transaction(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка данных транзакции"""
        # Для реальной реализации нужно:
        # 1. Получить ABI контрактов
        # 2. Построить multicall транзакцию или серию транзакций
        # 3. Рассчитать amountOutMin с учетом slippage
        
        # Заглушка для примера
        return {
            'from': self.account.address,
            'to': opportunity['dexes'][0]['router_address'],
            'value': 0,
            'data': b'',
            'nonce': self.web3.eth.get_transaction_count(self.account.address)
        }
    
    async def _estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Оценка количества газа"""
        try:
            return self.web3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.warning(f"Gas estimation failed, using default: {e}")
            return self.config['gas_limit']
    
    async def _get_gas_price(self) -> int:
        """Получение текущей цены газа"""
        return self.web3.eth.gas_price
    
    async def _wait_for_transaction(self, tx_hash: bytes) -> TxReceipt:
        """Ожидание подтверждения транзакции"""
        return self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)