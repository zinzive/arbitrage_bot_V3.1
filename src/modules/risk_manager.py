from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.utils.database import Database

class RiskManager:
    """Модуль управления рисками арбитражных сделок"""
    
    def __init__(self, config: Dict[str, Any], database: Database):
        self.config = config
        self.db = database
        self.trade_history: List[Dict[str, Any]] = []
    
    def validate_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Проверка арбитражной возможности на соответствие критериям риска"""
        if not self._check_min_profitability(opportunity):
            logger.info("Opportunity rejected: insufficient profitability")
            return False
        
        if not self._check_max_slippage(opportunity):
            logger.info("Opportunity rejected: excessive slippage")
            return False
        
        if not self._check_trade_limits(opportunity):
            logger.info("Opportunity rejected: trade limits exceeded")
            return False
        
        if not self._check_dex_availability(opportunity):
            logger.info("Opportunity rejected: DEX issues detected")
            return False
        
        return True
    
    def _check_min_profitability(self, opportunity: Dict[str, Any]) -> bool:
        """Проверка минимальной прибыльности"""
        return opportunity['profit'] >= self.config['min_profitability']
    
    def _check_max_slippage(self, opportunity: Dict[str, Any]) -> bool:
        """Проверка максимального проскальзывания"""
        # В реальной реализации нужно рассчитать ожидаемое проскальзывание
        # на основе ликвидности пулов и объема сделки
        estimated_slippage = self._estimate_slippage(opportunity)
        return estimated_slippage <= self.config['max_slippage']
    
    def _estimate_slippage(self, opportunity: Dict[str, Any]) -> float:
        """Оценка проскальзывания для арбитражной возможности"""
        # Упрощенная реализация - в реальности нужен расчет на основе
        # ликвидности в пулах и объема сделки
        base_slippage = 0.001  # 0.1% базовое проскальзывание
        path_length_penalty = len(opportunity['path']) * 0.0005  # 0.05% за каждый шаг
        return base_slippage + path_length_penalty
    
    def _check_trade_limits(self, opportunity: Dict[str, Any]) -> bool:
        """Проверка лимитов торговли"""
        # Проверка максимального объема за период
        recent_trades = self._get_recent_trades(hours=1)
        total_volume = sum(trade['volume'] for trade in recent_trades)
        
        max_hourly_volume = self.config.get('max_hourly_volume', 10000)
        if total_volume + opportunity['estimated_volume'] > max_hourly_volume:
            return False
        
        # Проверка максимального количества сделок за период
        max_hourly_trades = self.config.get('max_hourly_trades', 20)
        if len(recent_trades) >= max_hourly_trades:
            return False
        
        return True
    
    def _get_recent_trades(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Получение recent trades из базы данных"""
        # В реальной реализации нужно запрашивать из базы данных
        # Здесь заглушка для примера
        return self.trade_history
    
    def _check_dex_availability(self, opportunity: Dict[str, Any]) -> bool:
        """Проверка доступности DEX"""
        # В реальной реализации нужно проверять:
        # 1. Доступность RPC нод
        # 2. Достаточность ликвидности в пулах
        # 3. Статус контрактов
        return True
    
    def record_trade(self, trade_data: Dict[str, Any]) -> None:
        """Запись информации о выполненной сделке"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'volume': trade_data.get('volume', 0),
            'profit': trade_data.get('profit', 0),
            'path': trade_data.get('path', [])
        })
        
        # Очистка старых записей (старше 24 часов)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.trade_history = [
            trade for trade in self.trade_history 
            if trade['timestamp'] > cutoff_time
        ]