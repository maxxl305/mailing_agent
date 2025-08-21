#!/usr/bin/env python3
# test_backend.py - Backend Test ohne Frontend

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_backend():
    """Test das komplette Backend ohne app.py"""
    print("🧪 BACKEND TEST - Ohne Frontend")
    print("=" * 50)
    
    # 1. Import Test
    try:
        from agent.graph import graph
        from agent.state import EXTENDED_EXTRACTION_SCHEMA
        from agent.configuration import Configuration, EnvironmentConfig
        print("✅ Imports erfolgreich")
    except Exception as e:
        print(f"❌ Import Error: {e}")
        return False
    
    # 2. Configuration Test
    try:
        config = Configuration.from_runnable_config()
        print(f"✅ Configuration geladen")
        print(f"   Meta Ad Analysis: {config.enable_meta_ad_analysis}")
        print(f"   Should analyze Meta: {config.should_analyze_meta_ads()}")
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return False
    
    # 3. Meta API Test
    try:
        from agent.meta_ad_client import test_meta_api
        meta_works = await test_meta_api()
        print(f"✅ Meta API Test: {'Funktioniert' if meta_works else 'Token fehlt (OK)'}")
    except Exception as e:
        print(f"⚠️  Meta API Test Error: {e}")
    
    # 4. Kleiner Graph Test
    try:
        print("\n🚀 Graph Test mit echter Website...")
        
        state = {
            "urls": ["https://palestra-fitness.de"],
            "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
            "user_notes": "Backend Test",
            "completed_notes": [],
            "info": {},
            "is_satisfactory": {},
            "reflection_steps_taken": {},
            "meta_ad_intelligence": {},
            "generate_cold_email": False,  # Erstmal ohne Email
            "email_config": None,
            "generated_emails": {}
        }
        
        print("   📊 Starting Graph...")
        result = await graph.ainvoke(state)
        
        # Check Results
        website_data = result.get("info", {}).get("https://palestra-fitness.de", {})
        meta_data = result.get("meta_ad_intelligence", {}).get("https://palestra-fitness.de", {})
        
        print(f"\n✅ Graph Test erfolgreich!")
        print(f"   Website Data: {'✅' if website_data.get('company_name') else '❌'}")
        print(f"   Company Name: {website_data.get('company_name', 'MISSING')}")
        print(f"   USP: {website_data.get('unique_selling_proposition', 'MISSING')[:50]}...")
        
        print(f"   Meta Data: {'✅' if meta_data else '❌'}")
        if meta_data:
            meta_status = meta_data.get("llm_analysis", {}).get("advertising_status", "unknown")
            print(f"   Meta Status: {meta_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_email():
    """Test mit Email Generation"""
    print("\n📧 EMAIL TEST")
    print("=" * 30)
    
    try:
        from agent.graph import graph
        from agent.state import EXTENDED_EXTRACTION_SCHEMA
        
        state = {
            "urls": ["https://palestra-fitness.de"],
            "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
            "user_notes": "Email Test",
            "completed_notes": [],
            "info": {},
            "is_satisfactory": {},
            "reflection_steps_taken": {},
            "meta_ad_intelligence": {},
            "generate_cold_email": True,
            "email_config": {
                "sender_company": "Mobile Fusion",
                "sender_name": "Jonas Kremser",
                "sender_role": "Digital Marketing Consultant", 
                "service_offering": "SEO & Meta Ad Optimierung",
                "email_tone": "professionell",
                "email_length": "medium",
                "call_to_action": "kostenloses Beratungsgespräch",
                "email_language": "deutsch"
            },
            "generated_emails": {}
        }
        
        print("   📧 Starting Email Test...")
        result = await graph.ainvoke(state)
        
        email = result.get("generated_emails", {}).get("https://palestra-fitness.de")
        
        if email:
            print("✅ Email generiert!")
            print(f"   Länge: {len(email)} Zeichen")
            print(f"   Preview: {email[:100]}...")
        else:
            print("❌ Keine Email generiert")
            
    except Exception as e:
        print(f"❌ Email Test Error: {e}")

def main():
    """Main Test Function"""
    print("🔧 BACKEND TESTS FÜR COMPANY RESEARCH TOOL")
    print("=" * 60)
    
    # Check Environment
    print("📋 Environment Check:")
    api_keys = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "FIRECRAWL_API_KEY": bool(os.getenv("FIRECRAWL_API_KEY")),
        "META_API_ACCESS_TOKEN": bool(os.getenv("META_API_ACCESS_TOKEN")),
        "TAVILY_API_KEY": bool(os.getenv("TAVILY_API_KEY"))
    }
    
    for key, exists in api_keys.items():
        status = "✅" if exists else "❌"
        print(f"   {key}: {status}")
    
    if not api_keys["OPENAI_API_KEY"] or not api_keys["FIRECRAWL_API_KEY"]:
        print("\n⚠️  WARNUNG: OpenAI + Firecrawl API Keys sind erforderlich!")
        print("   Meta API Token ist optional (graceful fallback)")
    
    print("\n" + "=" * 60)
    
    # Run Tests
    success = asyncio.run(test_backend())
    
    if success:
        print("\n" + "=" * 60)
        choice = input("📧 Email Test auch ausführen? (y/n): ").lower().strip()
        if choice == 'y':
            asyncio.run(test_with_email())
    
    print("\n" + "=" * 60)
    print("🎯 FAZIT:")
    if success:
        print("✅ Backend funktioniert! Du kannst jetzt app.py anpassen.")
        print("🚀 Nächster Schritt: python start_tool.py")
    else:
        print("❌ Backend hat Probleme. Bitte Fehler beheben vor app.py.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()