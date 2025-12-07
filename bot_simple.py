#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from config import Config
from datetime import datetime
import json
import os

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Intentar importar los módulos opcionales (si fallan, el bot sigue funcionando)
try:
    from database import db
    DB_AVAILABLE = True
except ImportError:
    logger.warning("Database module not available, continuing without database")
    DB_AVAILABLE = False

try:
    from ai_handler import ai
    AI_AVAILABLE = True
except ImportError:
    logger.warning("AI handler not available, using default responses")
    AI_AVAILABLE = False

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Crear teclado inline
    keyboard = [
        [InlineKeyboardButton("🏠 Comprador", callback_data="comprador")],
        [InlineKeyboardButton("💰 Inversor", callback_data="inversor")],
        [InlineKeyboardButton("📊 Asesoría", callback_data="asesoria")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"¡Hola {user.first_name}! 👋\n\nSoy InmoBot, tu asistente inmobiliario especializado en Florida. 🏖️\n\nPuedo ayudarte con:\n• Búsqueda de propiedades\n• Asesoría de inversión\n• Información de mercados\n• Conexión con agentes\n\n¿En qué puedo asistirte hoy?"
    
    update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Intentar registrar usuario en la base de datos (si está disponible)
    if DB_AVAILABLE:
        try:
            # En versiones antiguas, no podemos usar async directamente
            # Simplemente intentamos registrar, pero si falla, continuamos
            pass
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
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
    update.message.reply_text(help_text, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming text messages."""
    user_message = update.message.text
    user = update.effective_user
    
    # Respuesta por defecto
    response = f"¡Gracias por tu mensaje, {user.first_name}! 📝\n\nHe recibido: '{user_message}'\n\nActualmente estoy procesando tu consulta sobre propiedades en Florida. Pronto tendré más funcionalidades para asistirte mejor.\n\nMientras tanto, puedes usar /help para ver cómo puedo ayudarte."
    
    # Si el AI handler está disponible, intentar usarlo
    if AI_AVAILABLE:
        try:
            # En versiones antiguas no podemos usar async directamente
            # Por ahora usamos respuesta por defecto
            pass
        except Exception as e:
            logger.error(f"Error usando AI handler: {e}")
    
    update.message.reply_text(response)

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    
    if callback_data == "comprador":
        response = "*🏠 MODO COMPRADOR*\n\n¡Excelente elección! Florida es un paraíso para compradores. 🌴\n\nPuedo ayudarte con:\n\n• *Presupuesto:* ¿Cuál es tu rango de inversión?\n• *Tipo de propiedad:* ¿Casa, apartamento, condominio?\n• *Zona preferida:* ¿Miami, Orlando, Tampa, Fort Lauderdale?\n• *Características:* ¿Piscina, cerca de playa, amueblado?\n\nCuéntame más sobre lo que buscas para recomendarte las mejores opciones. 😊"
    
    elif callback_data == "inversor":
        response = "*💰 MODO INVERSOR*\n\n¡Brillante decisión! Florida tiene uno de los mercados inmobiliarios más dinámicos de USA. 📈\n\nPuedo asistirte con:\n\n• *ROI Analysis:* Proyecciones de retorno por zona\n• *Hotspots:* Áreas con mayor apreciación\n• *Estrategias:* Alquiler vacacional, renta larga, fix & flip\n• *Due Diligence:* Verificación de propiedades\n• *Gestión:* Recomendaciones de property managers\n\n¿Cuál es tu capital inicial y horizonte de inversión? 💼"
    
    elif callback_data == "asesoria":
        response = "*📊 ASESORÍA PERSONALIZADA*\n\n¡Perfecto! Cada inversor tiene necesidades únicas. 🎯\n\nPara darte la mejor asesoría, necesito saber:\n\n1. *Objetivo:* ¿Renta, reventa, uso personal?\n2. *Timeline:* ¿Plazo de inversión?\n3. *Presupuesto:* ¿Rango aproximado?\n4. *Experiencia:* ¿Primera inversión o ya tienes propiedades?\n5. *Riesgo:* ¿Perfil conservador o agresivo?\n\nCon esta información, crearé un plan personalizado para ti. 📋"
    
    else:
        response = "Opción no reconocida. Usa /help para ver las opciones disponibles."
    
    query.edit_message_text(response, parse_mode='Markdown')

def error_handler(update: Update, context: CallbackContext) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Solo intentar enviar mensaje si hay un update
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            update.effective_message.reply_text(
                "Lo siento, ocurrió un error. Por favor, intenta de nuevo o usa /start."
            )
        except Exception as e:
            logger.error(f"Error al enviar mensaje de error: {e}")

def main() -> None:
    """Start the bot."""
    # Crear el Updater y pasarle el token del bot
    updater = Updater(Config.TELEGRAM_TOKEN, use_context=True)
    
    # Obtener el dispatcher para registrar handlers
    dispatcher = updater.dispatcher
    
    # Registrar handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    
    # Registrar error handler
    dispatcher.add_error_handler(error_handler)
    
    # Iniciar el bot
    logger.info("✅ Bot iniciado y escuchando...")
    updater.start_polling()
    
    # Mantener el bot ejecutándose hasta que se presione Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
