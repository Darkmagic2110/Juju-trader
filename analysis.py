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
        """Generate trading signal based on indicators and Nigerian time"""
        from datetime import datetime
        import pytz

        # Get Nigerian time
        nigeria_tz = pytz.timezone('Africa/Lagos')
        current_time = datetime.now(nigeria_tz)
        current_hour = current_time.hour
        time_str = current_time.strftime("%I:%M:%S %p WAT")

        # Define trading sessions (in UTC)
        london_session = 7 <= current_hour < 16
        ny_session = 12 <= current_hour < 21
        asian_session = (current_hour >= 22) or (current_hour < 7)

        # Trend analysis
        # Detailed trend analysis
        trend_strength = abs(sma_short - sma_long) / sma_long * 100
        if sma_short > sma_long:
            trend = "BULLISH"
            trend_direction = "🔼 UPTREND"
            if trend_strength > 1.5:
                trend_direction += " (Strong)"
            elif trend_strength > 0.5:
                trend_direction += " (Moderate)"
            else:
                trend_direction += " (Weak)"
        else:
            trend = "BEARISH"
            trend_direction = "🔽 DOWNTREND"
            if trend_strength > 1.5:
                trend_direction += " (Strong)"
            elif trend_strength > 0.5:
                trend_direction += " (Moderate)"
            else:
                trend_direction += " (Weak)"

        # RSI analysis
        if rsi > 70:
            rsi_signal = "OVERBOUGHT"
        elif rsi < 30:
            rsi_signal = "OVERSOLD"
        else:
            rsi_signal = "NEUTRAL"

        # Base signal
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

        # Add timing recommendation
        time_advice = "\n⏰ Best Time to Trade: "
        if london_session and ny_session:  # Overlap
            time_advice += "Now (London-NY overlap - High volatility)"
        elif london_session:
            time_advice += "Now (London session)"
        elif ny_session:
            time_advice += "Now (New York session)"
        elif asian_session:
            time_advice += "Now (Asian session - Lower volatility)"
        else:
            time_advice += "Wait for major session"

        # Add specific hour recommendation
        if signal in ["STRONG BUY", "BUY"]:
            if london_session:
                time_advice += "\n🎯 Optimal Entry: 8:00-10:00 UTC"
            elif ny_session:
                time_advice += "\n🎯 Optimal Entry: 13:00-15:00 UTC"
        elif signal in ["STRONG SELL", "SELL"]:
            if london_session:
                time_advice += "\n🎯 Optimal Entry: 9:00-11:00 UTC"
            elif ny_session:
                time_advice += "\n🎯 Optimal Entry: 14:00-16:00 UTC"

        # Combine all information
        detailed_signal = f"🕒 Time: {time_str}\n"
        detailed_signal += f"📊 Trend: {trend_direction}\n"
        detailed_signal += f"💹 Trend Strength: {trend_strength:.2f}%\n"
        detailed_signal += f"📈 Signal: {signal}\n"
        detailed_signal += time_advice

        return detailed_signal