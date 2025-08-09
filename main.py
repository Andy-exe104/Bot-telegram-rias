import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Setup basic error logging first, before anything else
def setup_basic_logging():
    """Setup basic error logging that works even if everything else fails"""
    try:
        # Create a simple log file
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"BOT STARTUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n")
    except Exception as e:
        print(f"Could not create error log file: {e}")

def log_error_to_file(error, context=""):
    """Log error to file immediately"""
    try:
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n[{timestamp}] ERROR: {context}\n")
            f.write(f"Error: {str(error)}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
            f.write(f"{'='*50}\n")
    except Exception as e:
        print(f"Could not write to error log: {e}")

# Setup basic logging immediately
setup_basic_logging()

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
    from database.database import DatabaseManager
    from commands.start import start_command
    from commands.info import info_command
    from commands.admin import admin_commands
    from commands.logs import logs_command
    from commands.commit_logs import commit_logs_command
    from config.prefixes import is_valid_prefix, get_command_without_prefix
    from utils.logger import ErrorLogger
except Exception as e:
    log_error_to_file(e, "Import error")
    raise e

# Load environment variables
load_dotenv()

# Initialize error logger
try:
    error_logger = ErrorLogger(
        bot_token=os.getenv('BOT_TOKEN'),
        error_chat_id=os.getenv('ERROR_CHAT_ID')  # Optional: Chat ID to send errors to
    )
except Exception as e:
    log_error_to_file(e, "Error logger initialization")
    error_logger = None

class RiasGremoryBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.db_manager = DatabaseManager()
        
    async def start(self):
        """Start the bot"""
        # Check if bot token is provided
        if not self.bot_token:
            log_error_to_file("BOT_TOKEN environment variable is not set", "Bot initialization")
            if error_logger:
                error_logger.log_error("BOT_TOKEN environment variable is not set", "Bot initialization")
            return
        
        if error_logger:
            error_logger.log_info(f"Bot token: {self.bot_token[:10]}...")
        
        try:
            # Initialize database
            if error_logger:
                error_logger.log_info("Initializing database...")
            await self.db_manager.initialize_database()
            
            # Create application
            if error_logger:
                error_logger.log_info("Creating application...")
            application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers (with and without prefixes)
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(CommandHandler("info", info_command))
            application.add_handler(CommandHandler("logs", logs_command))
            application.add_handler(CommandHandler("commitlogs", commit_logs_command))
            
            # Add admin commands
            application.add_handler(CommandHandler("addadmin", admin_commands.add_admin))
            application.add_handler(CommandHandler("addseller", admin_commands.add_seller))
            application.add_handler(CommandHandler("addpremium", admin_commands.add_premium))
            
            # Add message handler for prefixed commands
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_prefixed_commands))
            
            # Add callback query handler for buttons
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Start the bot
            if error_logger:
                error_logger.log_info("Starting bot...")
            await application.initialize()
            await application.start()
            if error_logger:
                error_logger.log_info("Bot started successfully!")
            await application.run_polling()
            
        except Exception as e:
            log_error_to_file(e, "Bot startup")
            if error_logger:
                error_logger.log_error(e, "Bot startup")
            raise e
    
    async def handle_prefixed_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle commands with prefixes"""
        text = update.message.text.strip()
        
        if not is_valid_prefix(text):
            return
        
        command = get_command_without_prefix(text)
        command_parts = command.split()
        
        if not command_parts:
            return
        
        cmd = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        # Update context args for the command
        context.args = args
        
        # Route to appropriate command
        if cmd == "start":
            await start_command(update, context)
        elif cmd == "info":
            await info_command(update, context)
        elif cmd == "logs":
            await logs_command(update, context)
        elif cmd == "commitlogs":
            await commit_logs_command(update, context)
        elif cmd == "addadmin":
            await admin_commands.add_admin(update, context)
        elif cmd == "addseller":
            await admin_commands.add_seller(update, context)
        elif cmd == "addpremium":
            await admin_commands.add_premium(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "kenny_kx":
            await query.edit_message_text("🎭 *¡Hola! Soy @Kenny_kx, el creador de este bot inspirado en Rias Gremory!* 🎭\n\n"
                                        "💖 *¿Te gusta el anime? ¡Entonces este bot es perfecto para ti!* 💖\n\n"
                                        "🔥 *Comandos disponibles:*\n"
                                        "• /start o *start - Iniciar el bot\n"
                                        "• /info o *info - Ver tu información\n"
                                        "• /addpremium o *addpremium - Dar premium a usuario\n\n"
                                        "🎪 *¡Disfruta de tu experiencia con Rias!* 🎪", 
                                        parse_mode='Markdown')

async def main():
    """Main function"""
    try:
        bot = RiasGremoryBot()
        await bot.start()
    except Exception as e:
        log_error_to_file(e, "Main function")
        raise e

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        log_error_to_file(e, "asyncio.run")
        sys.exit(1)