import os
import openai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurado en .env")
        openai.api_key = self.api_key
        
        self.system_prompt = "Eres un agente inmobiliario especializado en el mercado de Florida. Tu nombre es InmoBot. Eres experto en compra, venta, alquiler e inversión en propiedades en Florida. Responde de manera amable, profesional y concisa. Siempre preguntas por detalles específicos como presupuesto, tipo de propiedad y ubicación preferida."
    
    async def generar_respuesta(self, mensaje_usuario: str, user_id: int) -> str:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": mensaje_usuario}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                user=str(user_id)
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.error.AuthenticationError:
            return "Error de autenticación con OpenAI. Por favor, verifica la configuración de la API."
        except openai.error.RateLimitError:
            return "He alcanzado el límite de solicitudes. Por favor, inténtalo de nuevo en un momento."
        except Exception as e:
            print(f"Error en AI handler: {e}")
            return "Lo siento, estoy teniendo problemas para procesar tu solicitud. ¿Podrías intentarlo de nuevo o preguntarme algo más específico sobre propiedades en Florida?"

ai = AIHandler()
