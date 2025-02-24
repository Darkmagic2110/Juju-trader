import os

# Configuration settings for the bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Get token from environment variable

# Technical Analysis Parameters
SHORT_TERM_PERIOD = 20
LONG_TERM_PERIOD = 50
UPDATE_INTERVAL = 3600  # 1 hour in seconds

# CoinGecko API
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Supported currency pairs
SUPPORTED_PAIRS = {
    'BTC/USD': 'bitcoin',
    'ETH/USD': 'ethereum',
    'BNB/USD': 'binancecoin',
    'XRP/USD': 'ripple',
    'ADA/USD': 'cardano'
}

# Message templates
HELP_MESSAGE = """
Available commands:
/start - Start the bot
/help - Show this help message
/price <symbol> - Get current price (e.g., /price BTC/USD)
/alert <symbol> <price> - Set price alert (e.g., /alert BTC/USD 30000)
/analysis <symbol> - Get technical analysis (e.g., /analysis BTC/USD)
/pairs - Show supported pairs
"""