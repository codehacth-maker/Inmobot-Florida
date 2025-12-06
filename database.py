from supabase import create_client, Client
from config import Config
from datetime import datetime

class Database:
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
        print("✅ Conectado a Supabase")
    
    def create_lead(self, lead_data):
        try:
            response = 
self.client.table('leads').insert(lead_data).execute()
            print(f"✅ Lead creado: {lead_data.get('telegram_id')}")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error creando lead: {e}")
            return None
    
    def update_lead(self, telegram_id, updates):
        try:
            updates['updated_at'] = datetime.now().isoformat()
            response = self.client.table('leads')\
                .update(updates)\
                .eq('telegram_id', telegram_id)\
                .execute()
            print(f"✅ Lead actualizado: {telegram_id}")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error actualizando lead: {e}")
            return None

db = Database()
