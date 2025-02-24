import pandas as pd
import ta
from api_client import AlphaVantageAPI
from config import SHORT_TERM_PERIOD, LONG_TERM_PERIOD
import logging

logger = logging.getLogger(__name__) # Assuming a logger is configured elsewhere

class TechnicalAnalysis:
    def __init__(self):
        self.api = AlphaVantageAPI()

    def calculate_signals(self, symbol):
        try:
            df = self.api.get_historical_data(symbol)
            if df is None:
                logger.error(f"Could not get historical data for {symbol}")
                return None

            if len(df) < 2:
                logger.warning(f"Limited data available for {symbol}, using current price only")
                current_price = df['price'].iloc[-1]
                return {
                    'price': current_price,
                    'sma_short': current_price,
                    'sma_long': current_price,
                    'rsi': 50,  # Neutral RSI
                    'signal': 'NEUTRAL - Limited Data'
                }

            # Calculate Moving Averages
            df['SMA_short'] = ta.trend.sma_indicator(df['price'], window=SHORT_TERM_PERIOD)
            df['SMA_long'] = ta.trend.sma_indicator(df['price'], window=LONG_TERM_PERIOD)

            # Calculate RSI
            df['RSI'] = ta.momentum.rsi(df['price'], window=14)

            # Generate signals
            current_price = df['price'].iloc[-1]
            sma_short = df['SMA_short'].iloc[-1]
            sma_long = df['SMA_long'].iloc[-1]
            rsi = df['RSI'].iloc[-1]

            # Analysis logic (using original logic, improved with error handling)
            signal = self._generate_signal(current_price, sma_short, sma_long, rsi)

            return {
                'price': current_price,
                'sma_short': sma_short,
                'sma_long': sma_long,
                'rsi': rsi,
                'signal': signal
            }
        except Exception as e:
            logger.error(f"Error calculating signals for {symbol}: {e}")
            return None

    def _generate_signal(self, price, sma_short, sma_long, rsi):
        """Generate trading signal based on indicators"""
        signal = ""

        # Trend analysis
        if sma_short > sma_long:
            trend = "BULLISH"
        else:
            trend = "BEARISH"

        # RSI analysis
        if rsi > 70:
            rsi_signal = "OVERBOUGHT"
        elif rsi < 30:
            rsi_signal = "OVERSOLD"
        else:
            rsi_signal = "NEUTRAL"

        # Combined signal
        if trend == "BULLISH" and rsi_signal == "OVERSOLD":
            signal = "STRONG BUY"
        elif trend == "BULLISH" and rsi_signal == "NEUTRAL":
            signal = "BUY"
        elif trend == "BEARISH" and rsi_signal == "OVERBOUGHT":
            signal = "STRONG SELL"
        elif trend == "BEARISH" and rsi_signal == "NEUTRAL":
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        return signal