from config import settings
from supabase import create_client
import sys

def test_supabase():
    try:
        print(f"Connecting to Supabase: {settings.SUPABASE_URL}")
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        print("Testing query...")
        query = client.table('prompt_config').select('prompt_text').eq('id', 1).maybe_single()
        
        result = query.execute()
        print(f"Result: {result}")
        
        # Test the fix logic
        try:
            if result and hasattr(result, 'data') and result.data and result.data.get('prompt_text'):
                print("✅ Fix logic: Data found")
            else:
                print("✅ Fix logic: No data, handled gracefully (no crash)")
        except Exception as e:
            print(f"❌ Fix logic FAILED: {e}")

    except Exception as e:
        print(f"❌ Connection/Query Error: {e}")

if __name__ == "__main__":
    test_supabase()
