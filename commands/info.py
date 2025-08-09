from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from database.database import DatabaseManager

db_manager = DatabaseManager()

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    user = update.effective_user
    
    # Get user data from database
    user_data = await db_manager.get_user(user.id)
    if not user_data:
        await update.message.reply_text("❌ *Error: Usuario no encontrado en la base de datos*", parse_mode='Markdown')
        return
    
    # Get Colombian time
    colombia_tz = pytz.timezone('America/Bogota')
    colombia_time = datetime.now(colombia_tz)
    
    # Get rank info
    rank_info = await db_manager.get_rank_info(user_data['rank'])
    
    # Calculate time remaining if user has expiration
    time_remaining = ""
    if user_data['expires_at']:
        expires_at = user_data['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        time_diff = expires_at - colombia_time
        if time_diff.total_seconds() > 0:
            days = time_diff.days
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            
            if days > 0:
                time_remaining = f"⏰ *Tiempo restante:* {days} días, {hours} horas"
            elif hours > 0:
                time_remaining = f"⏰ *Tiempo restante:* {hours} horas, {minutes} minutos"
            else:
                time_remaining = f"⏰ *Tiempo restante:* {minutes} minutos"
        else:
            time_remaining = "⏰ *Estado:* Expirado"
    else:
        time_remaining = "⏰ *Estado:* Sin expiración"
    
    # Create info message
    info_text = f"""
💖 *Información de Usuario - Rias Gremory Bot* 💖

👤 *Datos Personales:*
• *ID:* `{user.id}`
• *Nombre:* {user.first_name}
• *Apellido:* {user.last_name or 'No especificado'}
• *Usuario:* @{user.username or 'Sin usuario'}

🎭 *Rango y Estado:*
• *Rango:* {rank_info['emoji']} {rank_info['name']}
• *Descripción:* {rank_info['description']}
• {time_remaining}

📅 *Información de Cuenta:*
• *Fecha de registro:* {user_data['created_at'].strftime('%d/%m/%Y %H:%M')}
• *Última actualización:* {colombia_time.strftime('%d/%m/%Y %H:%M')}

🇨🇴 *Hora en Colombia:* {colombia_time.strftime('%H:%M:%S')}

🔥 *Comandos disponibles según tu rango:*
{get_available_commands(user_data['rank'])}

💫 *¡Gracias por usar el Bot de Rias Gremory!* 💫
    """
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

def get_available_commands(rank: str) -> str:
    """Get available commands based on user rank"""
    commands = {
        'issei': """
• /start - Iniciar bot
• /info - Ver información
• /addadmin - Agregar admin
• /addseller - Agregar seller
• /addpremium - Agregar premium""",
        
        'admin': """
• /start - Iniciar bot
• /info - Ver información
• /addseller - Agregar seller
• /addpremium - Agregar premium""",
        
        'seller': """
• /start - Iniciar bot
• /info - Ver información
• /addpremium - Agregar premium""",
        
        'premium': """
• /start - Iniciar bot
• /info - Ver información""",
        
        'free_user': """
• /start - Iniciar bot
• /info - Ver información"""
    }
    
    return commands.get(rank, commands['free_user'])