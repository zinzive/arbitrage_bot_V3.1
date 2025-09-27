# Arbitrage Bot for Polygon Network

Арбитражный бот для сети Polygon, который ищет возможности для прибыльной торговли между различными DEX.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Настройте конфигурационные файлы в `config/`
4. Запустите бота: `python src/main.py`

## Конфигурация

### secrets.yaml
Заполните своими данными:
```yaml
private_key: "your_wallet_private_key"
telegram_bot_token: "your_telegram_bot_token"
telegram_chat_id: "your_telegram_chat_id"
infura_project_id: "your_infura_project_id"
alchemy_api_key: "your_alchemy_api_key"
