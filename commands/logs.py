from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import error_logger

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command - Only Issei can view logs"""
    user = update.effective_user
    
    # Check if user is Issei
    if user.id != 7560671542:
        await update.message.reply_text("❌ *Error: Solo Issei puede ver los logs*", parse_mode='Markdown')
        return
    
    try:
        # Get recent errors
        recent_errors = error_logger.get_recent_errors(30)  # Last 30 lines
        
        if len(recent_errors) > 4000:
            # Split into chunks if too long
            chunks = [recent_errors[i:i+4000] for i in range(0, len(recent_errors), 4000)]
            for i, chunk in enumerate(chunks):
                chunk_message = f"📋 *LOGS PART {i+1}/{len(chunks)}*\n\n```\n{chunk}\n```"
                await update.message.reply_text(chunk_message, parse_mode='Markdown')
        else:
            log_message = f"📋 *LOGS RECIENTES*\n\n```\n{recent_errors}\n```"
            await update.message.reply_text(log_message, parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(f"❌ *Error al obtener logs:* {str(e)}", parse_mode='Markdown')