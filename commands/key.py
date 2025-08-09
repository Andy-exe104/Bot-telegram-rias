from telegram import Update
from telegram.ext import ContextTypes
from database.database import DatabaseManager

db_manager = DatabaseManager()

class KeyCommands:
    @staticmethod
    async def list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all unused keys - Only Issei, Admin and Seller can do this"""
        user = update.effective_user
        
        # Check if user has permission
        user_data = await db_manager.get_user(user.id)
        if not user_data or user_data['rank'] not in ['issei', 'admin', 'seller']:
            await update.message.reply_text("❌ *Error: Solo Issei, Administradores y Vendedores pueden ver las llaves*", parse_mode='Markdown')
            return
        
        # Get unused keys
        keys = await db_manager.get_unused_keys()
        
        if not keys:
            await update.message.reply_text(
                "🔍 *No hay llaves disponibles*\n\n"
                "💎 *Usa /generatekey para crear nuevas llaves*",
                parse_mode='Markdown'
            )
            return
        
        # Create keys list message
        keys_text = "🔑 *Llaves Disponibles:*\n\n"
        
        for i, key in enumerate(keys, 1):
            rank_info = await db_manager.get_rank_info(key['rank'])
            keys_text += f"*{i}.* 🔐 `{key['key_code']}`\n"
            keys_text += f"   {rank_info['emoji']} *Rango:* {rank_info['name']}\n"
            keys_text += f"   ⏰ *Duración:* {key['days_valid']} días\n"
            keys_text += f"   📅 *Creada:* {key['created_at'].strftime('%d/%m/%Y %H:%M')}\n\n"
        
        keys_text += f"💫 *Total de llaves:* {len(keys)}"
        
        await update.message.reply_text(keys_text, parse_mode='Markdown')

# Create instance for import
key_commands = KeyCommands()