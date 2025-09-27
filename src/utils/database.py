import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from src.utils.logger import logger

class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = "arbitrage_bot.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица для хранения арбитражных возможностей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS opportunities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        path TEXT NOT NULL,
                        profit REAL NOT NULL,
                        estimated_volume REAL,
                        dexes TEXT,
                        status TEXT DEFAULT 'found'
                    )
                ''')
                
                # Таблица для хранения выполненных сделок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        opportunity_id INTEGER,
                        path TEXT NOT NULL,
                        volume REAL,
                        profit REAL,
                        gas_used INTEGER,
                        gas_price INTEGER,
                        tx_hash TEXT UNIQUE,
                        status TEXT NOT NULL,
                        FOREIGN KEY (opportunity_id) REFERENCES opportunities (id)
                    )
                ''')
                
                # Таблица для хранения балансов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS balances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        token TEXT NOT NULL,
                        balance REAL NOT NULL,
                        usd_value REAL
                    )
                ''')
                
                # Таблица для хранения ошибок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS errors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        module TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        severity TEXT DEFAULT 'error'
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def save_opportunity(self, opportunity: Dict[str, Any]) -> int:
        """Сохранение арбитражной возможности в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO opportunities 
                    (timestamp, path, profit, estimated_volume, dexes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    opportunity['timestamp'],
                    ','.join(opportunity['path']),
                    opportunity['profit'],
                    opportunity.get('estimated_volume'),
                    ','.join(opportunity.get('dexes', []))
                ))
                
                opportunity_id = cursor.lastrowid
                conn.commit()
                return opportunity_id
                
        except sqlite3.Error as e:
            logger.error(f"Failed to save opportunity: {e}")
            return -1
    
    def save_trade(self, trade: Dict[str, Any]) -> bool:
        """Сохранение информации о сделке в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trades 
                    (timestamp, opportunity_id, path, volume, profit, gas_used, gas_price, tx_hash, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade['timestamp'],
                    trade.get('opportunity_id'),
                    ','.join(trade['path']),
                    trade.get('volume'),
                    trade.get('profit'),
                    trade.get('gas_used'),
                    trade.get('gas_price'),
                    trade.get('tx_hash'),
                    trade['status']
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to save trade: {e}")
            return False
    
    def save_error(self, module: str, error_message: str, severity: str = "error") -> bool:
        """Сохранение информации об ошибке в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO errors 
                    (timestamp, module, error_message, severity)
                    VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now(),
                    module,
                    error_message,
                    severity
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to save error: {e}")
            return False
    
    def get_recent_trades(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Получение списка сделок за последние N часов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE timestamp >= datetime('now', ?)
                    ORDER BY timestamp DESC
                ''', (f'-{hours} hours',))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get recent trades: {e}")
            return []
    
    def get_daily_profit(self) -> float:
        """Получение суммарной прибыли за сегодня"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT SUM(profit) FROM trades 
                    WHERE date(timestamp) = date('now') AND status = 'success'
                ''')
                
                result = cursor.fetchone()
                return result[0] if result[0] else 0.0
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get daily profit: {e}")
            return 0.0