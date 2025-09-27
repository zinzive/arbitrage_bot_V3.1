# src/modules/data_fetcher.py
import asyncio
from typing import Dict, List, Tuple
from web3 import Web3
from src.models.dex import Dex
from src.models.token import Token
from src.utils.logger import logger

class DataFetcher:
    """Модуль получения данных о ценах"""
    
    def __init__(self, web3: Web3, dexes: List[Dex], tokens: Dict[str, Token]):
        self.web3 = web3
        self.dexes = dexes
        self.tokens = tokens
    
    async def fetch_price(self, dex: Dex, token_in: Token, token_out: Token) -> float:
        """Получение цены для пары токенов на DEX"""
        try:
            # Получаем количество токенов out для 1 токена in
            amount_in = Web3.to_wei(1, 'ether')  # 1 токен (с учетом decimals)
            
            path = [token_in.address, token_out.address]
            amounts_out = dex.router_contract.functions.getAmountsOut(
                amount_in, path
            ).call()
            
            amount_out = amounts_out[-1]
            price = amount_out / (10 ** token_out.decimals)
            
            # Учитываем комиссию DEX
            return price * (1 - dex.fee)
            
        except Exception as e:
            logger.error(f"Error fetching price from {dex.name} for {token_in.symbol}/{token_out.symbol}: {e}")
            return 0.0
    
    async def fetch_all_prices(self) -> Dict[str, Dict[Tuple[str, str], float]]:
        """Получение всех цен across всех DEX и токенов"""
        prices = {}
        
        for dex in self.dexes:
            dex_prices = {}
            
            # Создаем задачи для всех пар токенов
            tasks = []
            for token_in in self.tokens.values():
                for token_out in self.tokens.values():
                    if token_in != token_out:
                        tasks.append(self.fetch_price(dex, token_in, token_out))
            
            # Выполняем все задачи параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            task_idx = 0
            for token_in in self.tokens.values():
                for token_out in self.tokens.values():
                    if token_in != token_out:
                        price = results[task_idx]
                        if not isinstance(price, Exception) and price > 0:
                            dex_prices[(token_in.symbol, token_out.symbol)] = price
                        task_idx += 1
            
            prices[dex.name] = dex_prices
        
        return prices