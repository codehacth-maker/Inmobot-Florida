import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    FLORIDA_ZONES = [
        'Miami-Dade',
        'Broward (Fort Lauderdale)',
        'Palm Beach',
        'Orlando',
        'Tampa Bay',
        'Jacksonville',
        'Naples',
        'Sarasota'
    ]
