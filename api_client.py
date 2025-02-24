import requests
import pandas as pd
import logging
from config import ALPHA_VANTAGE_API_KEY, SUPPORTED_PAIRS

logger = logging.getLogger(__name__)

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_price(self, symbol):
        """Get current price for a currency pair"""
        try:
            if '/' in symbol:
                symbol = symbol.replace('/', '')

            response = requests.get(
                self.base_url,
                params={
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": symbol[:3],
                    "to_currency": symbol[3:],
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
            if '/' in symbol:
                symbol = symbol.replace('/', '')

            logger.info(f"Fetching historical data for {symbol}")

            response = requests.get(
                self.base_url,
                params={
                    "function": "FX_DAILY",
                    "from_symbol": symbol[:3],
                    "to_symbol": symbol[3:],
                    "outputsize": "full" if days > 100 else "compact",
                    "apikey": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()

            # Log the response for debugging
            logger.debug(f"API Response: {data}")

            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API Error: {data['Error Message']}")
                return None
            elif "Note" in data:
                logger.warning(f"API Note: {data['Note']}")

            if "Time Series FX (Daily)" not in data:
                logger.error("Error: No time series data in response")
                # Try getting current price as fallback
                current_price = self.get_price(symbol)
                if current_price:
                    # Create minimal dataset with current price
                    df = pd.DataFrame({
                        'close': [current_price],
                        'price': [current_price]
                    }, index=[pd.Timestamp.now()])
                    return df
                return None

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(
                data["Time Series FX (Daily)"],
                orient="index",
                columns=["open", "high", "low", "close"]
            )

            # Convert to numeric
            df = df.astype(float)
            df["price"] = df["close"]

            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df = df.tail(days)

            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None