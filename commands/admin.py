from telegram import Update
from telegram.ext import ContextTypes
from database.database import DatabaseManager

db_manager = DatabaseManager()

class AdminCommands:
    @staticmethod
    async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add admin user - Only Issei can do this"""
        user = update.effective_user
        
        # Check if user is Issei
        user_data = await db_manager.get_user(user.id)
        if not user_data or user_data['rank'] != 'issei':
            await update.message.reply_text("❌ *Error: Solo Issei puede agregar administradores*", parse_mode='Markdown')
            return
        
        # Check if user ID is provided
        if not context.args:
            await update.message.reply_text("❌ *Uso:* /addadmin <user_id>", parse_mode='Markdown')
            return
        
        try:
            target_id = int(context.args[0])
            days = int(context.args[1]) if len(context.args) > 1 else 30
            
            # Update user rank
            updated_user = await db_manager.update_user_rank(target_id, 'admin', days)
            
            if updated_user:
                await update.message.reply_text(
                    f"✅ *¡Administrador agregado exitosamente!*\n\n"
                    f"👤 *Usuario:* {updated_user['first_name']}\n"
                    f"🆔 *ID:* `{target_id}`\n"
                    f"⚡ *Rango:* Admin\n"
                    f"⏰ *Duración:* {days} días\n\n"
                    f"🎭 *¡El poder de Rias Gremory está contigo!* 🎭",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ *Error: Usuario no encontrado*", parse_mode='Markdown')
                
        except ValueError:
            await update.message.reply_text("❌ *Error: ID de usuario inválido*", parse_mode='Markdown')
    
    @staticmethod
    async def add_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add seller user - Only Issei and Admin can do this"""
        user = update.effective_user
        
        # Check if user has permission
        user_data = await db_manager.get_user(user.id)
        if not user_data or user_data['rank'] not in ['issei', 'admin']:
            await update.message.reply_text("❌ *Error: Solo Issei y Administradores pueden agregar vendedores*", parse_mode='Markdown')
            return
        
        # Check if user ID is provided
        if not context.args:
            await update.message.reply_text("❌ *Uso:* /addseller <user_id> [días]", parse_mode='Markdown')
            return
        
        try:
            target_id = int(context.args[0])
            days = int(context.args[1]) if len(context.args) > 1 else 30
            
            # Update user rank
            updated_user = await db_manager.update_user_rank(target_id, 'seller', days)
            
            if updated_user:
                await update.message.reply_text(
                    f"✅ *¡Vendedor agregado exitosamente!*\n\n"
                    f"👤 *Usuario:* {updated_user['first_name']}\n"
                    f"🆔 *ID:* `{target_id}`\n"
                    f"💎 *Rango:* Seller\n"
                    f"⏰ *Duración:* {days} días\n\n"
                    f"💎 *¡El comercio de Rias Gremory está en tus manos!* 💎",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ *Error: Usuario no encontrado*", parse_mode='Markdown')
                
        except ValueError:
            await update.message.reply_text("❌ *Error: ID de usuario inválido*", parse_mode='Markdown')
    
    @staticmethod
    async def add_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add premium user - Only Issei, Admin and Seller can do this"""
        user = update.effective_user
        
        # Check if user has permission
        user_data = await db_manager.get_user(user.id)
        if not user_data or user_data['rank'] not in ['issei', 'admin', 'seller']:
            await update.message.reply_text("❌ *Error: Solo Issei, Administradores y Vendedores pueden agregar usuarios premium*", parse_mode='Markdown')
            return
        
        # Check if user ID is provided
        if not context.args:
            await update.message.reply_text("❌ *Uso:* /addpremium <user_id> [días]", parse_mode='Markdown')
            return
        
        try:
            target_id = int(context.args[0])
            days = int(context.args[1]) if len(context.args) > 1 else 30
            
            # Update user rank
            updated_user = await db_manager.update_user_rank(target_id, 'premium', days)
            
            if updated_user:
                await update.message.reply_text(
                    f"✅ *¡Usuario Premium agregado exitosamente!*\n\n"
                    f"👤 *Usuario:* {updated_user['first_name']}\n"
                    f"🆔 *ID:* `{target_id}`\n"
                    f"🌟 *Rango:* Premium\n"
                    f"⏰ *Duración:* {days} días\n\n"
                    f"🌟 *¡Bienvenido al club exclusivo de Rias Gremory!* 🌟",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ *Error: Usuario no encontrado*", parse_mode='Markdown')
                
        except ValueError:
            await update.message.reply_text("❌ *Error: ID de usuario inválido*", parse_mode='Markdown')

# Create instance for import
admin_commands = AdminCommands()