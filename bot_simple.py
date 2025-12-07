from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import Config
from database import db
from ai_handler import ai
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InmoBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        
    def create_application(self):
        """Crear la aplicación correctamente"""
        return Application.builder().token(self.token).build()
    
    def setup_handlers(self, application):
        """Configurar todos los manejadores"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_error_handler(self.error_handler)
        return application
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        keyboard = [
            [InlineKeyboardButton("🏠 Comprador", callback_data="comprador")],
            [InlineKeyboardButton("💰 Inversor", callback_data="inversor")],
            [InlineKeyboardButton("📊 Asesoría", callback_data="asesoria")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"Hola {user.first_name}! Soy tu asistente inmobiliario de Florida. ¿Cómo puedo ayudarte hoy?"
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
        try:
            await db.registrar_usuario(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                fecha_registro=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error al registrar usuario: {e}")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🤖 *Comandos disponibles:*
/start - Iniciar el bot
/help - Mostrar esta ayuda

🏠 *Funcionalidades:*
• Buscar propiedades en Florida
• Asesoría inmobiliaria
• Cálculo de inversiones
• Contacto con agentes

¿En qué puedo ayudarte?
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        user = update.effective_user
        
        try:
            response = await ai.generar_respuesta(user_message, user.id)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error en handle_message: {e}")
            await update.message.reply_text("Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "comprador":
            response = "Perfecto! Como comprador, puedo ayudarte a:\n\n• Buscar propiedades según tu presupuesto\n• Analizar zonas y precios\n• Conectarte con agentes certificados\n\n¿Qué tipo de propiedad buscas?"
        elif callback_data == "inversor":
            response = "Excelente! Como inversor, puedo ayudarte con:\n\n• Análisis de ROI en diferentes zonas\n• Propiedades con mejor potencial de apreciación\n• Estrategias de inversión en Florida\n\n¿Cuál es tu presupuesto de inversión?"
        elif callback_data == "asesoria":
            response = "Claro! Para asesoría personalizada:\n\n• Necesito saber tus objetivos específicos\n• Timeline de inversión\n• Presupuesto aproximado\n\n¿Podrías compartirme más detalles?"
        else:
            response = "Opción no reconocida. Usa /help para ver las opciones."
        
        await query.edit_message_text(response)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Lo siento, ocurrió un error. Por favor, intenta de nuevo o usa /start."
                )
            except:
                pass
    
    def run(self):
        """Iniciar el bot"""
        logger.info("Iniciando bot...")
        application = self.create_application()
        application = self.setup_handlers(application)
        application.run_polling(allowed_updates=Update.ALL_TYPES)

# Punto de entrada principal
if __name__ == "__main__":
    try:
        bot = InmoBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        print(f"Error crítico: {e}")
