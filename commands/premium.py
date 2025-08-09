from telegram import Update
from telegram.ext import ContextTypes
from database.database import DatabaseManager

db_manager = DatabaseManager()

class PremiumCommands:
    @staticmethod
    async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate premium key - Only Issei, Admin and Seller can do this"""
        user = update.effective_user
        
        # Check if user has permission
        user_data = await db_manager.get_user(user.id)
        if not user_data or user_data['rank'] not in ['issei', 'admin', 'seller']:
            await update.message.reply_text("❌ *Error: Solo Issei, Administradores y Vendedores pueden generar llaves*", parse_mode='Markdown')
            return
        
        # Check if rank and days are provided
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ *Uso:* /generatekey <rango> <días>\n\n"
                "🎭 *Rangos disponibles:*\n"
                "• premium - Usuario Premium\n"
                "• seller - Vendedor\n"
                "• admin - Administrador\n\n"
                "💎 *Ejemplo:* /generatekey premium 30",
                parse_mode='Markdown'
            )
            return
        
        try:
            rank = context.args[0].lower()
            days = int(context.args[1])
            
            # Validate rank
            valid_ranks = ['premium', 'seller', 'admin']
            if rank not in valid_ranks:
                await update.message.reply_text(
                    "❌ *Error: Rango inválido*\n\n"
                    "🎭 *Rangos válidos:*\n"
                    "• premium\n"
                    "• seller\n"
                    "• admin",
                    parse_mode='Markdown'
                )
                return
            
            # Generate key
            key_data = await db_manager.create_key(rank, days, user.id)
            
            if key_data:
                rank_info = await db_manager.get_rank_info(rank)
                await update.message.reply_text(
                    f"🔑 *¡Llave generada exitosamente!*\n\n"
                    f"🔐 *Código:* `{key_data['key_code']}`\n"
                    f"{rank_info['emoji']} *Rango:* {rank_info['name']}\n"
                    f"⏰ *Duración:* {days} días\n"
                    f"📅 *Generada:* {key_data['created_at'].strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"💫 *¡Comparte esta llave con quien desees!* 💫",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ *Error: No se pudo generar la llave*", parse_mode='Markdown')
                
        except ValueError:
            await update.message.reply_text("❌ *Error: Número de días inválido*", parse_mode='Markdown')
    
    @staticmethod
    async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Redeem premium key - All users can do this"""
        user = update.effective_user
        
        # Check if key is provided
        if not context.args:
            await update.message.reply_text("❌ *Uso:* /redeemkey <código>", parse_mode='Markdown')
            return
        
        key_code = context.args[0].upper()
        
        # Get current user data
        user_data = await db_manager.get_user(user.id)
        if not user_data:
            await update.message.reply_text("❌ *Error: Usuario no encontrado*", parse_mode='Markdown')
            return
        
        # Try to use the key
        key_data = await db_manager.use_key(key_code, user.id)
        
        if key_data:
            rank_info = await db_manager.get_rank_info(key_data['rank'])
            
            # Get updated user data
            updated_user = await db_manager.get_user(user.id)
            
            await update.message.reply_text(
                f"🎉 *¡Llave canjeada exitosamente!*\n\n"
                f"🔐 *Código usado:* `{key_code}`\n"
                f"{rank_info['emoji']} *Nuevo rango:* {rank_info['name']}\n"
                f"⏰ *Duración:* {key_data['days_valid']} días\n"
                f"📅 *Canjeada:* {key_data['used_at'].strftime('%d/%m/%Y %H:%M')}\n\n"
                f"💖 *¡Bienvenido al nuevo nivel de Rias Gremory!* 💖",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ *Error: Llave inválida o ya utilizada*\n\n"
                "🔍 *Verifica:*\n"
                "• El código está correcto\n"
                "• La llave no ha sido usada\n"
                "• La llave no ha expirado",
                parse_mode='Markdown'
            )

# Create instance for import
premium_commands = PremiumCommands()