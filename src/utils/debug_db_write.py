
import os
import time
from supabase import create_client, Client

# Hardcoded from .env content read previously
url = "https://kyrvxikgtifklibusxwf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5cnZ4aWtndGlma2xpYnVzeHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyMTMxMDMsImV4cCI6MjA3MTc4OTEwM30.TyW35cWoe9EvF2hCpQ-di4lGDZeWc0yIU80EZmC1Vnw"

supabase: Client = create_client(url, key)

def test_write():
    print("--- Starting DB Write Test ---")
    
    # 1. Create a Dummy Project
    project_id = "00000000-0000-0000-0000-000000000001"
    print(f"1. Attempting to create/fetch dummy project: {project_id}")
    
    try:
        # Check if exists
        res = supabase.table("projeto").select("id").eq("id", project_id).execute()
        if not res.data:
            print("   Project not found. Creating...")
            data = {"id": project_id, "nome": "DEBUG_PROJECT_TEST"}
            res = supabase.table("projeto").insert(data).execute()
            print(f"   Created: {res.data}")
        else:
            print("   Project exists.")
            
    except Exception as e:
        print(f"❌ Failed to access/create project: {e}")
        return

    # 2. Upsert Prompt
    print(f"\n2. Attempting to upsert prompt for project: {project_id}")
    prompt_text = f"Debug Prompt {time.time()}"
    
    try:
        data = {
            "projeto_id": project_id,
            "prompt_text": prompt_text,
            "updated_at": "now()"
        }
        res = supabase.table("prompt_config").upsert(data, on_conflict="projeto_id").execute()
        print(f"✅ Upsert Result Data: {res.data}")
        
    except Exception as e:
        print(f"❌ Failed to upsert prompt: {e}")
        
    # 3. Verify Read
    print(f"\n3. Verifying read for project: {project_id}")
    try:
        res = supabase.table("prompt_config").select("*").eq("projeto_id", project_id).execute()
        print(f"   Read Result: {res.data}")
        if res.data and res.data[0]['prompt_text'] == prompt_text:
            print("✅ SUCCESS: Data matches!")
        else:
            print("❌ FAILURE: Data mismatch or empty.")
            
    except Exception as e:
        print(f"❌ Failed to read prompt: {e}")

if __name__ == "__main__":
    test_write()
