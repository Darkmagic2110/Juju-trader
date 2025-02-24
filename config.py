
import os

# Configuration settings for the bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')

# Technical Analysis Parameters
SHORT_TERM_PERIOD = 20
LONG_TERM_PERIOD = 50
UPDATE_INTERVAL = 3600  # 1 hour in seconds

# Supported cryptocurrency pairs
SUPPORTED_PAIRS = {
    'BTC/USDT': 'BTCUSDT',
    'ETH/USDT': 'ETHUSDT',
    'BNB/USDT': 'BNBUSDT',
    'SOL/USDT': 'SOLUSDT',
    'XRP/USDT': 'XRPUSDT'
}

# Message templates
HELP_MESSAGE = """
Available commands:
/start - Start the bot
/help - Show this help message
/price <symbol> - Get current price (e.g., /price BTC/USDT)
/alert <symbol> <price> - Set price alert (e.g., /alert BTC/USDT 50000)
/analysis <symbol> - Get technical analysis (e.g., /analysis BTC/USDT)
/pairs - Show supported pairs
/predict - Get buy/sell signals for all pairs
"""
