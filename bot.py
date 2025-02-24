import asyncio
import sys
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, HELP_MESSAGE, SUPPORTED_PAIRS, UPDATE_INTERVAL
from api_client import AlphaVantageAPI
from analysis import TechnicalAnalysis

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Verify token is available
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
    sys.exit(1)

logger.info(f"Starting bot with token starting with: {TELEGRAM_BOT_TOKEN[:5]}...")

class CryptoSignalBot:
    def __init__(self):
        self.api = AlphaVantageAPI()
        self.analysis = TechnicalAnalysis()
        self.price_alerts = {}  # Store price alerts: {user_id: {symbol: target_price}}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        logger.info(f"New user started the bot: {update.effective_user.id}")
        await update.message.reply_text(
            "Welcome to the Forex Trading Signal Bot!\n" + HELP_MESSAGE
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        await update.message.reply_text(HELP_MESSAGE)

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get current price for a symbol."""
        if not context.args or len(context.args) != 1:
            await update.message.reply_text("Please provide a symbol. Example: /price EUR/USD")
            return

        symbol = context.args[0].upper()
        if symbol not in SUPPORTED_PAIRS:
            await update.message.reply_text(f"Unsupported symbol. Use /pairs to see supported pairs.")
            return

        price = self.api.get_price(symbol)
        if price:
            await update.message.reply_text(f"Current {symbol} price: {price:.4f}")
        else:
            await update.message.reply_text("Error fetching price. Please try again later.")

    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get technical analysis for a symbol."""
        if not context.args or len(context.args) != 1:
            await update.message.reply_text("Please provide a symbol. Example: /analysis EUR/USD")
            return

        symbol = context.args[0].upper()
        if symbol not in SUPPORTED_PAIRS:
            await update.message.reply_text(f"Unsupported symbol. Use /pairs to see supported pairs.")
            return

        analysis_result = self.analysis.calculate_signals(symbol)
        if analysis_result:
            message = (
                f"Technical Analysis for {symbol}:\n"
                f"Current Price: {analysis_result['price']:.4f}\n"
                f"Short-term SMA: {analysis_result['sma_short']:.4f}\n"
                f"Long-term SMA: {analysis_result['sma_long']:.4f}\n"
                f"RSI: {analysis_result['rsi']:.2f}\n"
                f"Signal: {analysis_result['signal']}"
            )
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Error performing analysis. Please try again later.")

    async def alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set price alert for a symbol."""
        if not context.args or len(context.args) != 2:
            await update.message.reply_text("Please provide symbol and price. Example: /alert EUR/USD 1.2000")
            return

        symbol = context.args[0].upper()
        try:
            target_price = float(context.args[1])
        except ValueError:
            await update.message.reply_text("Invalid price value.")
            return

        if symbol not in SUPPORTED_PAIRS:
            await update.message.reply_text(f"Unsupported symbol. Use /pairs to see supported pairs.")
            return

        user_id = update.effective_user.id
        if user_id not in self.price_alerts:
            self.price_alerts[user_id] = {}
        self.price_alerts[user_id][symbol] = target_price

        await update.message.reply_text(f"Alert set for {symbol} at {target_price:.4f}")

    async def pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show supported pairs."""
        pairs_list = "\n".join(SUPPORTED_PAIRS.keys())
        await update.message.reply_text(f"Supported pairs:\n{pairs_list}")

    async def predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Predict buy/sell signals for all supported pairs."""
        message = "🎯 Trading Predictions:\n\n"
        for symbol in SUPPORTED_PAIRS:
            analysis_result = self.analysis.calculate_signals(symbol)
            if analysis_result:
                signal = analysis_result['signal']
                price = analysis_result['price']
                emoji = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "⚪️"
                message += f"{emoji} {symbol}: {signal} @ {price:.4f}\n"
        
        await update.message.reply_text(message)

    async def check_alerts(self, context: ContextTypes.DEFAULT_TYPE):
        """Check price alerts periodically."""
        for user_id, alerts in self.price_alerts.items():
            for symbol, target_price in alerts.items():
                current_price = self.api.get_price(symbol)
                if current_price:
                    if current_price >= target_price:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🚨 Alert: {symbol} has reached {current_price:.4f}"
                        )
                        # Remove triggered alert
                        del self.price_alerts[user_id][symbol]

def main():
    """Start the bot."""
    logger.info("Initializing bot application...")
    bot = CryptoSignalBot()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(CommandHandler("price", bot.price))
    application.add_handler(CommandHandler("analysis", bot.analysis_command))
    application.add_handler(CommandHandler("alert", bot.alert))
    application.add_handler(CommandHandler("pairs", bot.pairs))
    application.add_handler(CommandHandler("predict", bot.predict))

    # Add job for checking alerts
    job_queue = application.job_queue
    if job_queue:
        logger.info("Setting up alert check job...")
        job_queue.run_repeating(bot.check_alerts, interval=60)  # Check every minute
    else:
        logger.warning("JobQueue not available. Price alerts will not be active.")

    # Start the bot
    logger.info("Starting bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()