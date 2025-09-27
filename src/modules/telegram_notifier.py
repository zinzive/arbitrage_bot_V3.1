import asyncio
from typing import Dict, Any, Optional
import telegram
from telegram.constants import ParseMode
from src.utils.logger import logger

class TelegramNotifier:
    """Модуль отправки уведомлений через Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[telegram.Bot] = None
    
    async def initialize(self) -> None:
        """Инициализация бота Telegram"""
        try:
            self.bot = telegram.Bot(token=self.bot_token)
            await self.bot.get_me()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self.bot = None
    
    async def send_message(self, message: str, parse_mode: ParseMode = ParseMode.HTML) -> bool:
        """Отправка сообщения в Telegram"""
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def notify_opportunity(self, opportunity: Dict[str, Any]) -> None:
        """Уведомление о арбитражной возможности"""
        message = self._format_opportunity_message(opportunity)
        await self.send_message(message)
    
    async def notify_trade(self, trade_data: Dict[str, Any]) -> None:
        """Уведомление о выполненной сделке"""
        message = self._format_trade_message(trade_data)
        await self.send_message(message)
    
    async def notify_error(self, error: str) -> None:
        """Уведомление об ошибке"""
        message = f"❌ <b>Error:</b>\n<code>{error}</code>"
        await self.send_message(message)
    
    def _format_opportunity_message(self, opportunity: Dict[str, Any]) -> str:
        """Форматирование сообщения об арбитражной возможности"""
        profit_percent = opportunity['profit'] * 100
        path = " → ".join(opportunity['path'])
        
        return (
            f"🔍 <b>Arbitrage Opportunity Found!</b>\n\n"
            f"<b>Path:</b> {path}\n"
            f"<b>Profit:</b> {profit_percent:.2f}%\n"
            f"<b>Estimated Volume:</b> ${opportunity.get('estimated_volume', 0):.2f}\n"
            f"<b>Timestamp:</b> {opportunity['timestamp']}"
        )
    
    def _format_trade_message(self, trade_data: Dict[str, Any]) -> str:
        """Форматирование сообщения о сделке"""
        profit_percent = trade_data['profit'] * 100 if trade_data['profit'] else 0
        
        return (
            f"✅ <b>Trade Executed!</b>\n\n"
            f"<b>Path:</b> {' → '.join(trade_data['path'])}\n"
            f"<b>Profit:</b> {profit_percent:.2f}%\n"
            f"<b>Volume:</b> ${trade_data.get('volume', 0):.2f}\n"
            f"<b>TX Hash:</b> <code>{trade_data.get('tx_hash', 'N/A')}</code>\n"
            f"<b>Status:</b> {'Success' if trade_data.get('success', False) else 'Failed'}"
        )