import asyncio
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import DatabaseManager

db_manager = DatabaseManager()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Get Colombian time
    colombia_tz = pytz.timezone('America/Bogota')
    colombia_time = datetime.now(colombia_tz)
    hour = colombia_time.hour
    
    # Determine greeting based on time
    if 5 <= hour < 12:
        greeting = "🌅 *¡Buenos días!* 🌅"
    elif 12 <= hour < 18:
        greeting = "☀️ *¡Buenas tardes!* ☀️"
    else:
        greeting = "🌙 *¡Buenas noches!* 🌙"
    
    # Create or get user from database
    user_data = await db_manager.get_user(user.id)
    if not user_data:
        await db_manager.create_user(
            user.id, 
            user.username, 
            user.first_name, 
            user.last_name or ""
        )
        user_data = await db_manager.get_user(user.id)
    
    # Get rank info
    rank_info = await db_manager.get_rank_info(user_data['rank'])
    
    # Create keyboard with Kenny_kx button
    keyboard = [
        [InlineKeyboardButton("🎭 @Kenny_kx 🎭", callback_data="kenny_kx")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Create welcome message
    welcome_text = f"""
{greeting}

💖 *¡Bienvenido al Bot de Rias Gremory!* 💖

🎪 *Hora en Colombia:* {colombia_time.strftime('%H:%M:%S')} 🇨🇴
📅 *Fecha:* {colombia_time.strftime('%d/%m/%Y')}

👤 *Tu información:*
• *Nombre:* {user.first_name}
• *Usuario:* @{user.username or 'Sin usuario'}
• *Rango:* {rank_info['emoji']} {rank_info['name']}
• *Descripción:* {rank_info['description']}

🔥 *Comandos disponibles:*
• /info - Ver tu información detallada
• /redeemkey - Canjear llave premium

💫 *¡Disfruta de tu experiencia con Rias Gremory!* 💫
    """
    
    # Send message with image and button
    await update.message.reply_photo(
        photo="https://64.media.tumblr.com/1e9db433c8a7ae67b4a15fe89be0dac6/abcc58c76184ec29-14/s400x600/52756da1d8e3438fd4dcc98ce02d3ef5d8cdf19f.jpg",
        caption=welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )