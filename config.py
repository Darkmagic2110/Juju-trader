import os

# Configuration settings for the bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Get token from environment variable

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')

# Technical Analysis Parameters
SHORT_TERM_PERIOD = 20
LONG_TERM_PERIOD = 50
UPDATE_INTERVAL = 3600  # 1 hour in seconds

# Supported currency pairs
SUPPORTED_PAIRS = {
    'EUR/USD': 'EURUSD',
    'GBP/USD': 'GBPUSD',
    'USD/JPY': 'USDJPY',
    'USD/CAD': 'USDCAD',
    'AUD/USD': 'AUDUSD'
}

# Message templates
HELP_MESSAGE = """
Available commands:
/start - Start the bot
/help - Show this help message
/price <symbol> - Get current price (e.g., /price EUR/USD)
/alert <symbol> <price> - Set price alert (e.g., /alert EUR/USD 1.2000)
/analysis <symbol> - Get technical analysis (e.g., /analysis EUR/USD)
/pairs - Show supported pairs
/predict - Get buy/sell signals for all pairs
"""