import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
        self.client: Client = create_client(self.url, self.key)
        print("✅ Conectado a Supabase")
    
    def create_lead(self, lead_data):
        try:
            response = self.client.table('leads').insert(lead_data).execute()
            print(f"✅ Lead creado: {lead_data.get('telegram_id')}")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error creando lead: {e}")
            return None
    
    def update_lead(self, telegram_id, updates):
        try:
            updates['updated_at'] = datetime.now().isoformat()
            response = self.client.table('leads').update(updates).eq('telegram_id', telegram_id).execute()
            print(f"✅ Lead actualizado: {telegram_id}")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error actualizando lead: {e}")
            return None
    
    def get_lead(self, telegram_id):
        try:
            response = self.client.table('leads').select('*').eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error obteniendo lead: {e}")
            return None
    
    def delete_lead(self, telegram_id):
        try:
            self.client.table('leads').delete().eq('telegram_id', telegram_id).execute()
            print(f"✅ Lead eliminado: {telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Error eliminando lead: {e}")
            return False
    
    async def registrar_usuario(self, user_id, username, first_name, last_name, fecha_registro):
        lead_data = {
            "telegram_id": str(user_id),
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "fecha_registro": fecha_registro.isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return self.create_lead(lead_data)

db = Database()
