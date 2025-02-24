
import requests
import pandas as pd
import logging
from config import ALPHA_VANTAGE_API_KEY

logger = logging.getLogger(__name__)

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_price(self, symbol):
        """Get current price for a forex pair"""
        try:
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": symbol.split('/')[0],
                "to_currency": symbol.split('/')[1],
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Realtime Currency Exchange Rate" in data:
                return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol):
        """Get historical price data for technical analysis"""
        try:
            params = {
                "function": "FX_DAILY",
                "from_symbol": symbol.split('/')[0],
                "to_symbol": symbol.split('/')[1],
                "apikey": self.api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Time Series FX (Daily)" not in data:
                logger.error("Error: No time series data in response")
                return None

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data["Time Series FX (Daily)"], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            df = df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close'
            })
            df['price'] = df['close']
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
