import requests
import pandas as pd
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY, SUPPORTED_PAIRS
import logging

logger = logging.getLogger(__name__)

class AlphaVantageAPI:
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_price(self, symbol):
        try:
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": symbol[:3],
                "to_currency": symbol[3:],
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None

    def get_sma(self, symbol, period):
        try:
            params = {
                "function": "SMA",
                "symbol": symbol,
                "interval": "daily",
                "time_period": period,
                "series_type": "close",
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return float(list(data["Technical Analysis: SMA"].values())[0]["SMA"])
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return None

    def get_rsi(self, symbol):
        try:
            params = {
                "function": "RSI",
                "symbol": symbol,
                "interval": "daily",
                "time_period": 14,
                "series_type": "close",
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return float(list(data["Technical Analysis: RSI"].values())[0]["RSI"])
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50  # Return neutral RSI on error

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_price(self, symbol):
        """Get current price for a currency pair"""
        try:
            if symbol not in SUPPORTED_PAIRS:
                logger.warning(f"Unsupported symbol requested: {symbol}")
                return None

            instrument = SUPPORTED_PAIRS[symbol]
            logger.info(f"Fetching current price for {symbol} ({instrument})")

            response = requests.get(
                self.base_url,
                params={
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": instrument[:3],
                    "to_currency": instrument[3:],
                    "apikey": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()

            if "Realtime Currency Exchange Rate" not in data:
                logger.error("Error: No exchange rate data in response")
                return None

            rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
            logger.info(f"Successfully fetched price for {symbol}: {rate}")
            return rate

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol, days=100):
        """Get historical price data for technical analysis"""
        try:
            if symbol not in SUPPORTED_PAIRS:
                logger.warning(f"Unsupported symbol requested: {symbol}")
                return None

            instrument = SUPPORTED_PAIRS[symbol]
            logger.info(f"Fetching historical data for {symbol} ({instrument})")

            response = requests.get(
                self.base_url,
                params={
                    "function": "FX_DAILY",
                    "from_symbol": instrument[:3],
                    "to_symbol": instrument[3:],
                    "outputsize": "full" if days > 100 else "compact",
                    "apikey": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()

            if "Time Series FX (Daily)" not in data:
                logger.error("Error: No time series data in response")
                return None

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(
                data["Time Series FX (Daily)"],
                orient="index"
            )

            # Rename columns and convert to numeric
            df.columns = ["open", "high", "low", "close"]
            df = df.astype(float)

            # Add a price column (using closing price)
            df["price"] = df["close"]

            # Convert index to datetime
            df.index = pd.to_datetime(df.index)

            # Sort by date and limit to requested number of days
            df.sort_index(inplace=True)
            df = df.tail(days)

            logger.info(f"Successfully fetched historical data for {symbol}, got {len(df)} days")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None