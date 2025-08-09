import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from database.database import DatabaseManager
from commands.start import start_command
from commands.info import info_command
from commands.admin import admin_commands
from config.prefixes import is_valid_prefix, get_command_without_prefix

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(s)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RiasGremoryBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.db_manager = DatabaseManager()
        
    async def start(self):
        """Start the bot"""
        # Check if bot token is provided
        if not self.bot_token:
            print("❌ Error: BOT_TOKEN environment variable is not set")
            return
        
        print(f"🔧 Bot token: {self.bot_token[:10]}...")
        
        try:
            # Initialize database
            print("🔧 Initializing database...")
            await self.db_manager.initialize_database()
            
            # Create application
            print("🔧 Creating application...")
            application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers (with and without prefixes)
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("info", info_command))
        
        # Add admin commands
        application.add_handler(CommandHandler("addadmin", admin_commands.add_admin))
        application.add_handler(CommandHandler("addseller", admin_commands.add_seller))
        application.add_handler(CommandHandler("addpremium", admin_commands.add_premium))
        
        # Add message handler for prefixed commands
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_prefixed_commands))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
            # Start the bot
            print("🔧 Starting bot...")
            await application.initialize()
            await application.start()
            print("✅ Bot started successfully!")
            await application.run_polling()
            
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
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
    bot = RiasGremoryBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())