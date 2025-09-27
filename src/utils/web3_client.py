from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Dict, List
import asyncio
from src.utils.logger import logger

class Web3Client:
    """Клиент для работы с Web3"""
    
    def __init__(self, node_urls: Dict[str, str]):
        self.node_urls = node_urls
        self.w3 = self._connect()
    
    def _connect(self) -> Web3:
        """Подключение к ноде Polygon"""
        for provider_name, url in self.node_urls.items():
            try:
                w3 = Web3(Web3.HTTPProvider(url))
                if w3.is_connected():
                    logger.info(f"Connected to {provider_name} node")
                    # Добавляем middleware для Polygon
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    return w3
            except Exception as e:
                logger.error(f"Failed to connect to {provider_name}: {e}")
        
        raise ConnectionError("Could not connect to any Ethereum node")
    
    async def get_gas_price(self) -> int:
        """Асинхронное получение цены газа"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.w3.eth.gas_price)