import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.modules.data_fetcher import DataFetcher
from src.modules.arbitrage_engine import ArbitrageEngine
from src.modules.risk_manager import RiskManager

class TestArbitrageFlow:
    @pytest.fixture
    def setup_components(self, mock_web3, mock_database):
        # Моки для DEX и токенов
        dex = AsyncMock()
        dex.name = 'quickswap'
        dex.router_contract.functions.getAmountsOut.return_value.call.return_value = [
            10**18, 1010000  # 1.01 price
        ]
        
        tokens = {
            'USDT': MagicMock(symbol='USDT', address='0xUSDT', decimals=6),
            'USDC': MagicMock(symbol='USDC', address='0xUSDC', decimals=6)
        }
        
        # Инициализация компонентов
        data_fetcher = DataFetcher(mock_web3, [dex], tokens)
        arbitrage_engine = ArbitrageEngine(min_profitability=0.005, max_cycle_length=3)
        risk_manager = RiskManager({
            'min_profitability': 0.005,
            'max_slippage': 0.005,
            'max_hourly_volume': 10000,
            'max_hourly_trades': 20
        }, mock_database)
        
        return data_fetcher, arbitrage_engine, risk_manager
    
    @pytest.mark.asyncio
    async def test_full_arbitrage_flow(self, setup_components):
        data_fetcher, arbitrage_engine, risk_manager = setup_components
        
        # Получение цен
        prices = await data_fetcher.fetch_all_prices()
        
        # Поиск арбитражных возможностей
        opportunities = arbitrage_engine.find_opportunities(prices)
        
        # Проверка рисков
        if opportunities:
            is_valid = risk_manager.validate_opportunity(opportunities[0])
            assert isinstance(is_valid, bool)