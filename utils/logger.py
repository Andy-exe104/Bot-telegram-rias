import logging
import os
import traceback
from datetime import datetime
from telegram import Bot
import asyncio

class ErrorLogger:
    def __init__(self, bot_token=None, error_chat_id=None):
        self.bot_token = bot_token
        self.error_chat_id = error_chat_id
        self.bot = None
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup file logging
        self.setup_file_logging()
        
        # Setup bot for Telegram notifications
        if bot_token:
            self.bot = Bot(token=bot_token)
    
    def setup_file_logging(self):
        """Setup file logging"""
        # Create a custom logger
        self.logger = logging.getLogger('RiasBot')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        file_handler = logging.FileHandler('logs/bot_errors.log', encoding='utf-8')
        console_handler = logging.StreamHandler()
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Also log to a file that can be committed to git
        git_log_handler = logging.FileHandler('error_log.txt', encoding='utf-8')
        git_log_handler.setFormatter(log_format)
        self.logger.addHandler(git_log_handler)
    
    def log_error(self, error, context=""):
        """Log error to file and send to Telegram"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_message = f"🚨 ERROR at {timestamp}\n\n"
        
        if context:
            error_message += f"📍 Context: {context}\n\n"
        
        error_message += f"❌ Error: {str(error)}\n\n"
        error_message += f"📋 Traceback:\n{traceback.format_exc()}"
        
        # Log to file
        self.logger.error(error_message)
        
        # Send to Telegram if configured
        if self.bot and self.error_chat_id:
            try:
                # Send error in chunks if too long
                if len(error_message) > 4000:
                    chunks = [error_message[i:i+4000] for i in range(0, len(error_message), 4000)]
                    for i, chunk in enumerate(chunks):
                        chunk_message = f"🚨 ERROR PART {i+1}/{len(chunks)}\n\n{chunk}"
                        asyncio.create_task(self.send_telegram_message(chunk_message))
                else:
                    asyncio.create_task(self.send_telegram_message(error_message))
            except Exception as e:
                self.logger.error(f"Failed to send error to Telegram: {e}")
    
    def log_info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    async def send_telegram_message(self, message):
        """Send message to Telegram error channel"""
        try:
            await self.bot.send_message(
                chat_id=self.error_chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
    
    def get_recent_errors(self, lines=50):
        """Get recent errors from log file"""
        try:
            with open('logs/bot_errors.log', 'r', encoding='utf-8') as f:
                lines_list = f.readlines()
                return ''.join(lines_list[-lines:])
        except FileNotFoundError:
            return "No log file found"
        except Exception as e:
            return f"Error reading log file: {e}"

# Create global logger instance
error_logger = None