import requests
import pandas as pd
import logging
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, SUPPORTED_PAIRS

logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self):
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    def get_price(self, symbol):
        """Get current price for a cryptocurrency pair"""
        try:
            if '/' in symbol:
                symbol = symbol.replace('/', '')

            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.info(f"Successfully fetched price for {symbol}: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol, days=100):
        """Get historical price data for technical analysis"""
        try:
            if '/' in symbol:
                symbol = symbol.replace('/', '')

            logger.info(f"Fetching historical data for {symbol}")

            # Get klines/candlestick data
            klines = self.client.get_historical_klines(
                symbol,
                Client.KLINE_INTERVAL_1DAY,
                f"{days} days ago UTC"
            )

            # Create DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 
                'volume', 'close_time', 'quote_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Convert strings to floats
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(float)

            df['price'] = df['close']

            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None