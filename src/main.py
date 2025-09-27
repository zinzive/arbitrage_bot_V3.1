import asyncio
import yaml
from web3 import Web3
from src.utils.web3_client import Web3Client
from src.utils.logger import logger, setup_logger
from src.utils.database import Database
from src.modules.data_fetcher import DataFetcher
from src.modules.arbitrage_engine import ArbitrageEngine
from src.modules.risk_manager import RiskManager
from src.modules.transaction_executor import TransactionExecutor
from src.modules.telegram_notifier import TelegramNotifier
from src.models.token import Token
from src.models.dex import Dex

class ArbitrageBot:
    """Главный класс арбитражного бота"""
    
    def __init__(self):
        self.config = None
        self.secrets = None
        self.web3_client = None
        self.database = None
        self.data_fetcher = None
        self.arbitrage_engine = None
        self.risk_manager = None
        self.transaction_executor = None
        self.telegram_notifier = None
        self.tokens = {}
        self.dexes = []
        self.is_running = False
    
    def load_config(self) -> None:
        """Загрузка конфигурации"""
        try:
            with open('config/config.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
            
            with open('config/secrets.yaml', 'r') as f:
                self.secrets = yaml.safe_load(f)
                
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def initialize_components(self) -> None:
        """Инициализация компонентов бота"""
        # Инициализация Web3 клиента
        node_urls = {
            'main': self.config['node_providers']['polygon']['main'].format(
                infura_project_id=self.secrets['infura_project_id']
            ),
            'backup': self.config['node_providers']['polygon']['backup'].format(
                alchemy_api_key=self.secrets['alchemy_api_key']
            )
        }
        self.web3_client = Web3Client(node_urls)
        
        # Инициализация базы данных
        self.database = Database()
        
        # Инициализация токенов
        self.tokens = {
            name: Token(name, address) 
            for name, address in self.config['tokens'].items()
        }
        
        # Инициализация DEX
        for name, addresses in self.config['dex_addresses'].items():
            # В реальной реализации нужно загрузить ABI контрактов
            router_contract = self.web3_client.w3.eth.contract(
                address=addresses['router'],
                abi=[]  # Здесь должен быть ABI контракта
            )
            factory_contract = self.web3_client.w3.eth.contract(
                address=addresses['factory'],
                abi=[]  # Здесь должен быть ABI контракта
            )
            self.dexes.append(Dex(name, addresses['router'], addresses['factory'], 
                                 router_contract, factory_contract))
        
        # Инициализация модулей
        self.data_fetcher = DataFetcher(self.web3_client.w3, self.dexes, self.tokens)
        self.arbitrage_engine = ArbitrageEngine(
            min_profitability=self.config['settings']['min_profitability'],
            max_cycle_length=self.config['settings']['max_cycle_length']
        )
        self.risk_manager = RiskManager(self.config['settings'], self.database)
        self.transaction_executor = TransactionExecutor(
            self.web3_client.w3, 
            self.secrets['private_key'],
            self.config['settings']
        )
        self.telegram_notifier = TelegramNotifier(
            self.secrets['telegram_bot_token'],
            self.secrets['telegram_chat_id']
        )
    
    async def run(self) -> None:
        """Запуск главного цикла бота"""
        self.is_running = True
        logger.info("Starting arbitrage bot")
        
        # Инициализация Telegram бота
        await self.telegram_notifier.initialize()
        await self.telegram_notifier.send_message("🤖 Arbitrage bot started")
        
        while self.is_running:
            try:
                # Получение цен
                prices = await self.data_fetcher.fetch_all_prices()
                
                # Поиск арбитражных возможностей
                opportunities = self.arbitrage_engine.find_opportunities(prices)
                
                for opportunity in opportunities:
                    # Проверка рисков
                    if self.risk_manager.validate_opportunity(opportunity):
                        # Сохранение возможности в базу данных
                        opportunity_id = self.database.save_opportunity(opportunity)
                        opportunity['id'] = opportunity_id
                        
                        # Отправка уведомления
                        await self.telegram_notifier.notify_opportunity(opportunity)
                        
                        # Исполнение арбитражной сделки
                        receipt = await self.transaction_executor.execute_arbitrage(opportunity)
                        
                        if receipt and receipt.status == 1:
                            # Успешная сделка
                            trade_data = {
                                'timestamp': datetime.now(),
                                'opportunity_id': opportunity_id,
                                'path': opportunity['path'],
                                'volume': opportunity.get('estimated_volume'),
                                'profit': opportunity['profit'],
                                'gas_used': receipt.gasUsed,
                                'gas_price': receipt.effectiveGasPrice,
                                'tx_hash': receipt.transactionHash.hex(),
                                'status': 'success'
                            }
                            
                            # Сохранение и уведомление о сделке
                            self.database.save_trade(trade_data)
                            self.risk_manager.record_trade(trade_data)
                            await self.telegram_notifier.notify_trade(trade_data)
                        else:
                            # Неудачная сделка
                            trade_data = {
                                'timestamp': datetime.now(),
                                'opportunity_id': opportunity_id,
                                'path': opportunity['path'],
                                'status': 'failed'
                            }
                            self.database.save_trade(trade_data)
                            await self.telegram_notifier.notify_error("Trade execution failed")
                
                # Ожидание перед следующей итерацией
                await asyncio.sleep(self.config['settings']['polling_interval'])
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.database.save_error('main', str(e))
                await self.telegram_notifier.notify_error(f"Main loop error: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке
    
    async def stop(self) -> None:
        """Остановка бота"""
        self.is_running = False
        await self.telegram_notifier.send_message("🛑 Arbitrage bot stopped")
        logger.info("Arbitrage bot stopped")

async def main():
    """Главная функция"""
    bot = ArbitrageBot()
    
    try:
        # Настройка логирования
        setup_logger("arbitrage_bot", level=logging.INFO)
        
        # Загрузка конфигурации и инициализация
        bot.load_config()
        bot.initialize_components()
        
        # Запуск бота
        await bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        if bot.telegram_notifier:
            await bot.telegram_notifier.notify_error(f"Bot startup failed: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())