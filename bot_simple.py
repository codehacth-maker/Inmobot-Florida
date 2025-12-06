from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, 
CallbackQueryHandler, filters, ContextTypes
from config import Config
from database import db
from ai_handler import ai
from datetime import datetime

class InmoBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
    
    async def start(self, update: Update, context: 
ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        keyboard = [
            [InlineKeyboardButton("🏠 Comprador", 
callback_data="comprador")],
            [InlineKeyboardButton("💰 Inversionista", 
callback_data="inversionista")],
            [InlineKeyboardButton("🔄 Recolocación", 
callback_data="recolocacion")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Hola {user.first_name}! Soy tu asistente inmobiliario de 
Florida. ¿Cómo te puedo ayudar?",
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: 
ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        client_type = query.data
        
        lead_data = {
            'telegram_id': query.from_user.id,
            'first_name': query.from_user.first_name,
            'client_type': client_type,
            'created_at': datetime.now().isoformat()
        }
        
        db.create_lead(lead_data)
        
        await query.edit_message_text(
            f"Gracias por seleccionar {client_type}. Por favor, escribe tu 
nombre completo:"
        )
        context.user_data['step'] = 'nombre'
        context.user_data['client_type'] = client_type
    
    async def handle_message(self, update: Update, context: 
ContextTypes.DEFAULT_TYPE):
        if 'step' in context.user_data:
            step = context.user_data['step']
            
            if step == 'nombre':
                context.user_data['nombre'] = update.message.text
                context.user_data['step'] = 'telefono'
                await update.message.reply_text("Gracias. Ahora escribe tu 
número de teléfono:")
            elif step == 'telefono':
                context.user_data['telefono'] = update.message.text
                context.user_data['step'] = 'email'
                await update.message.reply_text("Ahora escribe tu email:")
            elif step == 'email':
                user_id = update.effective_user.id
                updates = {
                    'full_name': context.user_data['nombre'],
                    'phone': context.user_data['telefono'],
                    'email': update.message.text
                }
                db.update_lead(user_id, updates)
                
                keyboard = []
                for zone in Config.FLORIDA_ZONES:
                    keyboard.append([InlineKeyboardButton(zone, 
callback_data=f"zone_{zone}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Selecciona tu zona de 
interés en Florida:", reply_markup=reply_markup)
                del context.user_data['step']
        else:
            response = ai.generate_response(update.message.text)
            await update.message.reply_text(response)
    
    async def location_handler(self, update: Update, context: 
ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        location = query.data.replace('zone_', '')
        user_id = query.from_user.id
        
        db.update_lead(user_id, {'location': location})
        await query.edit_message_text(f"Perfecto! Un agente te contactará 
pronto para la zona {location}.")
    
    def run(self):
        application = Application.builder().token(self.token).build()
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler, 
pattern='^(comprador|inversionista|recolocacion)$'))
        
application.add_handler(CallbackQueryHandler(self.location_handler, 
pattern='^zone_'))
        application.add_handler(MessageHandler(filters.TEXT & 
~filters.COMMAND, self.handle_message))
        
        print("Bot iniciado...")
        application.run_polling()

if __name__ == '__main__':
    bot = InmoBot()
    bot.run()
