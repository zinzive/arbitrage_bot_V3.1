import pytest
import networkx as nx
from src.modules.arbitrage_engine import ArbitrageEngine

class TestArbitrageEngine:
    @pytest.fixture
    def engine(self):
        return ArbitrageEngine(min_profitability=0.005, max_cycle_length=3)
    
    def test_find_opportunities(self, engine):
        # Подготовка тестовых данных
        prices = {
            'quickswap': {
                ('USDT', 'USDC'): 1.01,
                ('USDC', 'USDT'): 0.99,
                ('USDT', 'WETH'): 0.0005,
                ('WETH', 'USDT'): 2000,
            }
        }
        
        opportunities = engine.find_opportunities(prices)
        
        # Проверяем, что движок возвращает список
        assert isinstance(opportunities, list)
    
    def test_calculate_profitability(self, engine):
        # Тестируем расчет прибыльности
        cycle = ['USDT', 'USDC', 'USDT']
        graph = nx.DiGraph()
        graph.add_edge('USDT', 'USDC', price=1.01)
        graph.add_edge('USDC', 'USDT', price=0.99)
        
        profit = engine._calculate_profitability(cycle, graph)
        
        # Расчет: 1.01 * 0.99 = 0.9999 → -0.0001 (убыток)
        assert profit == pytest.approx(-0.0001, 0.0001)
    
    def test_safe_log_positive(self, engine):
        result = engine._safe_log(2.0)
        assert result > 0
    
    def test_safe_log_zero(self, engine):
        result = engine._safe_log(0)
        assert result == 0
    
    def test_safe_log_negative(self, engine):
        result = engine._safe_log(-1.0)
        assert result == 0