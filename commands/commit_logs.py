import subprocess
import os
from telegram import Update
from telegram.ext import ContextTypes

async def commit_logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /commitlogs command - Only Issei can commit logs"""
    user = update.effective_user
    
    # Check if user is Issei
    if user.id != 7560671542:
        await update.message.reply_text("❌ *Error: Solo Issei puede hacer commit de los logs*", parse_mode='Markdown')
        return
    
    try:
        # Check if error_log.txt exists
        if not os.path.exists('error_log.txt'):
            await update.message.reply_text("📋 *No hay logs para hacer commit*", parse_mode='Markdown')
            return
        
        # Get file size
        file_size = os.path.getsize('error_log.txt')
        
        # Add the log file to git
        subprocess.run(['git', 'add', 'error_log.txt'], check=True)
        
        # Commit with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"Update error logs - {timestamp}"
        
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to remote
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        await update.message.reply_text(
            f"✅ *Logs enviados exitosamente!*\n\n"
            f"📁 *Archivo:* error_log.txt\n"
            f"📏 *Tamaño:* {file_size} bytes\n"
            f"📅 *Commit:* {commit_message}\n\n"
            f"🎭 *¡Los errores están ahora en el repositorio!*",
            parse_mode='Markdown'
        )
        
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(
            f"❌ *Error al hacer commit:* {str(e)}\n\n"
            f"🔧 *Comando que falló:* {e.cmd}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error inesperado:* {str(e)}",
            parse_mode='Markdown'
        )