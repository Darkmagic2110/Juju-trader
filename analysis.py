import pandas as pd
import ta
from api_client import AlphaVantageAPI
from config import SHORT_TERM_PERIOD, LONG_TERM_PERIOD

class TechnicalAnalysis:
    def __init__(self):
        self.api = AlphaVantageAPI()

    def calculate_signals(self, symbol):
        """Calculate technical indicators and generate trading signals"""
        df = self.api.get_historical_data(symbol)
        if df is None:
            return None

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

        # Analysis logic
        signal = self._generate_signal(current_price, sma_short, sma_long, rsi)

        return {
            'price': current_price,
            'sma_short': sma_short,
            'sma_long': sma_long,
            'rsi': rsi,
            'signal': signal
        }

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