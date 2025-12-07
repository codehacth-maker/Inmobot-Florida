import os
import requests
import json
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        # Usar DEEPSEEK_API_KEY (o OPENAI_API_KEY como respaldo)
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️  Advertencia: DEEPSEEK_API_KEY no configurado")
            self.api_key = None
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        self.system_prompt = "Eres un agente inmobiliario especializado en el mercado de Florida. Tu nombre es InmoBot. Eres experto en compra, venta, alquiler e inversión en propiedades en Florida. Responde de manera amable, profesional y concisa. Siempre preguntas por detalles específicos como presupuesto, tipo de propiedad y ubicación preferida."
    
    async def generar_respuesta(self, mensaje_usuario: str, user_id: int) -> str:
        if not self.api_key:
            return "Hola! Soy InmoBot, tu asistente inmobiliario. ¿En qué puedo ayudarte hoy con propiedades en Florida?"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": mensaje_usuario}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error DeepSeek API: {response.status_code} - {response.text}")
                return "Hola! Soy InmoBot. Actualmente estoy aprendiendo sobre el mercado de Florida. ¿En qué puedo ayudarte?"
                
        except Exception as e:
            print(f"Error en AI handler: {e}")
            return "Hola! Soy tu asistente inmobiliario. ¿Tienes alguna pregunta sobre propiedades en Florida?"

# Instancia global para importar
ai = AIHandler()
