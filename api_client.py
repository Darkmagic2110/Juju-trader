import requests
import pandas as pd
from config import COINGECKO_BASE_URL, SUPPORTED_PAIRS

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = COINGECKO_BASE_URL

    def get_price(self, symbol):
        """Get current price for a cryptocurrency"""
        try:
            if symbol not in SUPPORTED_PAIRS:
                return None
            
            coin_id = SUPPORTED_PAIRS[symbol]
            response = requests.get(
                f"{self.base_url}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data[coin_id]["usd"]
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None

    def get_historical_data(self, symbol, days=100):
        """Get historical price data for technical analysis"""
        try:
            if symbol not in SUPPORTED_PAIRS:
                return None
            
            coin_id = SUPPORTED_PAIRS[symbol]
            response = requests.get(
                f"{self.base_url}/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": days,
                    "interval": "daily"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
