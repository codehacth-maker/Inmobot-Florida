import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("🏠 Comprador", callback_data="comprador")],
        [InlineKeyboardButton("💰 Inversor", callback_data="inversor")],
        [InlineKeyboardButton("📊 Asesoría", callback_data="asesoria")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"Hola {user.first_name}! Soy tu asistente inmobiliario de Florida. ¿Cómo puedo ayudarte hoy?"
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Registrar en base de datos
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    user_message = update.message.text
    user = update.effective_user
    
    try:
        response = await ai.generar_respuesta(user_message, user.id)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error en handle_message: {e}")
        await update.message.reply_text("Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
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

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Error: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Lo siento, ocurrió un error. Por favor, intenta de nuevo o usa /start."
            )
        except:
            pass

def main() -> None:
    """Start the bot."""
    # Crear la aplicación
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Añadir manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # Ejecutar el bot
    logger.info("Iniciando bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
