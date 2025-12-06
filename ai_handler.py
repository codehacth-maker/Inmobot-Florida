import requests
from config import Config

class AIHandler:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
    
    def generate_response(self, message):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Eres un agente inmobiliario 
experto en Florida."},
                {"role": "user", "content": message}
            ]
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']

ai = AIHandler()
