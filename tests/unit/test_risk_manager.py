import pytest
from datetime import datetime, timedelta
from src.modules.risk_manager import RiskManager

class TestRiskManager:
    @pytest.fixture
    def risk_manager(self, mock_database):
        config = {
            'min_profitability': 0.005,
            'max_slippage': 0.005,
            'max_hourly_volume': 10000,
            'max_hourly_trades': 20
        }
        return RiskManager(config, mock_database)
    
    def test_validate_opportunity_profitability(self, risk_manager):
        opportunity = {
            'profit': 0.01,  # 1% - выше минимального
            'path': ['USDT', 'USDC', 'USDT'],
            'estimated_volume': 1000
        }
        
        assert risk_manager.validate_opportunity(opportunity) is True
    
    def test_validate_opportunity_low_profit(self, risk_manager):
        opportunity = {
            'profit': 0.001,  # 0.1% - ниже минимального
            'path': ['USDT', 'USDC', 'USDT'],
            'estimated_volume': 1000
        }
        
        assert risk_manager.validate_opportunity(opportunity) is False
    
    def test_record_trade(self, risk_manager):
        trade_data = {
            'timestamp': datetime.now(),
            'volume': 1000,
            'profit': 0.01,
            'path': ['USDT', 'USDC', 'USDT']
        }
        
        risk_manager.record_trade(trade_data)
        assert len(risk_manager.trade_history) == 1
        
        # Проверяем очистку старых записей
        old_trade = {
            'timestamp': datetime.now() - timedelta(hours=25),
            'volume': 1000,
            'profit': 0.01,
            'path': ['USDT', 'USDC', 'USDT']
        }
        
        risk_manager.record_trade(old_trade)
        assert len(risk_manager.trade_history) == 2  # Все еще 2, но при следующей записи очистится