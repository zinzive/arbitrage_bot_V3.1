# tests/unit/test_data_fetcher.py
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from src.modules.data_fetcher import DataFetcher

class TestDataFetcher:
    @pytest.fixture
    def mock_dex(self):
        dex = MagicMock()
        dex.name = 'quickswap'
        dex.fee = 0.003
        dex.router_contract.functions.getAmountsOut.return_value.call.return_value = [
            10**18, 1010000  # 1.01 price
        ]
        return dex
    
    @pytest.fixture
    def mock_tokens(self):
        return {
            'USDT': MagicMock(symbol='USDT', address='0xUSDT', decimals=6),
            'USDC': MagicMock(symbol='USDC', address='0xUSDC', decimals=6)
        }
    
    @pytest.fixture
    def data_fetcher(self, mock_web3, mock_dex, mock_tokens):
        return DataFetcher(mock_web3, [mock_dex], mock_tokens)
    
    @pytest.mark.asyncio
    async def test_fetch_all_prices(self, data_fetcher, mock_dex, mock_tokens):
        # Создаем асинхронный мок для gather
        async def mock_gather(*tasks, return_exceptions=False):
            return [1.00697, 0.99003]  # Два результата для двух пар
        
        # Патчим asyncio.gather
        with patch('src.modules.data_fetcher.asyncio.gather', side_effect=mock_gather):
            prices = await data_fetcher.fetch_all_prices()
            
            # Проверяем структуру возвращаемых данных
            assert isinstance(prices, dict)
            assert 'quickswap' in prices
            assert len(prices['quickswap']) == 2  # Две пары токенов
    
    @pytest.mark.asyncio
    async def test_fetch_price(self, data_fetcher, mock_dex, mock_tokens):
        price = await data_fetcher.fetch_price(
            mock_dex, mock_tokens['USDT'], mock_tokens['USDC']
        )
        assert price == pytest.approx(1.00697, 0.001)