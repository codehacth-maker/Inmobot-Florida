#!/usr/bin/env python3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from datetime import datetime
import os
import sys

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Intentar importar configuraciones y módulos
try:
    from config import Config
    BOT_TOKEN = Config.TELEGRAM_TOKEN
except ImportError:
    logger.error("No se pudo importar Config")
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN no encontrado")
        sys.exit(1)

# Intentar importar módulos opcionales
try:
    from database import db
    DB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database module not available: {e}")
    DB_AVAILABLE = False

try:
    from ai_handler import ai
    AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI handler not available: {e}")
    AI_AVAILABLE = False

# Crear instancia del bot
bot = telebot.TeleBot(BOT_TOKEN)

# Manejador del comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    
    # Crear teclado inline
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🏠 Comprador", callback_data="comprador"),
        InlineKeyboardButton("💰 Inversor", callback_data="inversor")
    )
    keyboard.row(InlineKeyboardButton("📊 Asesoría", callback_data="asesoria"))
    
    welcome_text = f"¡Hola {user.first_name}! 👋\n\nSoy InmoBot, tu asistente inmobiliario especializado en Florida. 🏖️\n\nPuedo ayudarte con:\n• Búsqueda de propiedades\n• Asesoría de inversión\n• Información de mercados\n• Conexión con agentes\n\n¿En qué puedo asistirte hoy?"
    
    bot.reply_to(message, welcome_text, reply_markup=keyboard)
    
    # Intentar registrar usuario en la base de datos
    if DB_AVAILABLE:
        try:
            # Nota: Necesitaríamos ajustar database.py para usar esta biblioteca
            logger.info(f"Usuario {user.id} inició el bot")
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")

# Manejador del comando /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
*🤖 COMANDOS DISPONIBLES:*
/start - Iniciar la conversación
/help - Mostrar esta ayuda

*🏠 FUNCIONALIDADES:*
• Buscar propiedades en Florida
• Asesoría inmobiliaria personalizada
• Cálculo de inversiones y ROI
• Contacto con agentes certificados
• Información sobre zonas y precios

*📍 COMO USARME:*
1. Usa /start para comenzar
2. Selecciona una opción del menú
3. Cuéntame tus necesidades
4. Te guiaré paso a paso

¿Listo para encontrar tu propiedad ideal en Florida? ☀️
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Manejador de mensajes de texto
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user
    user_message = message.text
    
    # Respuesta por defecto
    response = f"¡Gracias por tu mensaje, {user.first_name}! 📝\n\nHe recibido: '{user_message}'\n\nActualmente estoy procesando tu consulta sobre propiedades en Florida. Pronto tendré más funcionalidades para asistirte mejor.\n\nMientras tanto, puedes usar /help para ver cómo puedo ayudarte."
    
    bot.reply_to(message, response)

# Manejador de callbacks de botones
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "comprador":
            response = "*🏠 MODO COMPRADOR*\n\n¡Excelente elección! Florida es un paraíso para compradores. 🌴\n\nPuedo ayudarte con:\n\n• *Presupuesto:* ¿Cuál es tu rango de inversión?\n• *Tipo de propiedad:* ¿Casa, apartamento, condominio?\n• *Zona preferida:* ¿Miami, Orlando, Tampa, Fort Lauderdale?\n• *Características:* ¿Piscina, cerca de playa, amueblado?\n\nCuéntame más sobre lo que buscas para recomendarte las mejores opciones. 😊"
        
        elif call.data == "inversor":
            response = "*💰 MODO INVERSOR*\n\n¡Brillante decisión! Florida tiene uno de los mercados inmobiliarios más dinámicos de USA. 📈\n\nPuedo asistirte con:\n\n• *ROI Analysis:* Proyecciones de retorno por zona\n• *Hotspots:* Áreas con mayor apreciación\n• *Estrategias:* Alquiler vacacional, renta larga, fix & flip\n• *Due Diligence:* Verificación de propiedades\n• *Gestión:* Recomendaciones de property managers\n\n¿Cuál es tu capital inicial y horizonte de inversión? 💼"
        
        elif call.data == "asesoria":
            response = "*📊 ASESORÍA PERSONALIZADA*\n\n¡Perfecto! Cada inversor tiene necesidades únicas. 🎯\n\nPara darte la mejor asesoría, necesito saber:\n\n1. *Objetivo:* ¿Renta, reventa, uso personal?\n2. *Timeline:* ¿Plazo de inversión?\n3. *Presupuesto:* ¿Rango aproximado?\n4. *Experiencia:* ¿Primera inversión o ya tienes propiedades?\n5. *Riesgo:* ¿Perfil conservador o agresivo?\n\nCon esta información, crearé un plan personalizado para ti. 📋"
        
        else:
            response = "Opción no reconocida. Usa /help para ver las opciones disponibles."
        
        # Editar el mensaje original con la respuesta
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            parse_mode='Markdown'
        )
        
        # Responder al callback (quita el reloj de carga)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Error en callback: {e}")
        bot.answer_callback_query(call.id, "Ocurrió un error. Intenta nuevamente.")

# Función principal
def main():
    logger.info("🚀 Iniciando InmoBot...")
    logger.info(f"✅ Token: {'Configurado' if BOT_TOKEN else 'No configurado'}")
    logger.info(f"✅ Database: {'Disponible' if DB_AVAILABLE else 'No disponible'}")
    logger.info(f"✅ AI Handler: {'Disponible' if AI_AVAILABLE else 'No disponible'}")
    
    # Iniciar el bot
    logger.info("🤖 Bot iniciado. Esperando mensajes...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == '__main__':
    main()
