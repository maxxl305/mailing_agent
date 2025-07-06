# test_working.py - Das funktionierende System mit korrekter Result-Extraktion
import asyncio
from src.agent.graph import graph
from src.agent.state import DEFAULT_EXTRACTION_SCHEMA

async def main():
    print("Company Research + Email Generation")
    print("=" * 70)
    
    direct_state = {
        "urls": ["https://palestra-fitness.de"],
        "extraction_schema": DEFAULT_EXTRACTION_SCHEMA,
        "user_notes": "Fokus auf B2B-Marketing und Digitalisierung",
        "completed_notes": [],
        "info": {},
        "is_satisfactory": {},
        "reflection_steps_taken": {},
        
        "generate_cold_email": True,
        "email_config": {
            "sender_company": "Max & Jonas GmbH",
            "sender_name": "Max Siegl", 
            "sender_role": "Depp vom Dienst",
            "service_offering": "Digitale Marketing-Transformation für Industrieunternehmen",
            "email_tone": "professionnel und witzig",
            "email_length": "kurz",
            "call_to_action": "kostenloses Strategiegespräch über Ihre Online-Marketing-Optimierung",
            "email_language": "deutsch"
        },
        "generated_emails": {}
    }
    
    print("📋 Konfiguration:")
    print(f"   🎯 Target: {direct_state['urls'][0]}")
    print(f"   📧 Email: {direct_state['generate_cold_email']}")  
    print(f"   👤 Sender: {direct_state['email_config']['sender_name']}")
    print(f"   🏢 Company: {direct_state['email_config']['sender_company']}")
    print()
    
    try:
        print("🚀 Starte Company Research + Email Generation...")
        
        # ⚠️ FIX: Verwende ainvoke für komplettes Result
        final_result = await graph.ainvoke(direct_state)
        
        print("\n✅ Graph erfolgreich abgeschlossen!")
        print(f"📊 Result Keys: {list(final_result.keys())}")
        
        # Research Results anzeigen
        if "info" in final_result and final_result["info"]:
            print("\n" + "="*70)
            print("📊 COMPANY RESEARCH RESULTS:")
            print("="*70)
            
            for url, company_data in final_result["info"].items():
                name = company_data.get('company_name', 'Unbekannt')
                print(f"\n🏢 Unternehmen: {name}")
                print(f"🌐 URL: {url}")
                
                # Key Insights
                usp = company_data.get('unique_selling_proposition', 'N/A')
                print(f"🎯 Unique Selling Proposition:")
                print(f"   {usp}")
                
                # Target Audiences
                personas = company_data.get('target_audience_personas', [])
                print(f"\n👥 Zielgruppen ({len(personas)}):")
                for persona in personas[:2]:  # Zeige nur die ersten 2
                    print(f"   • {persona.get('persona_name', 'N/A')}")
                    print(f"     Demographics: {persona.get('demographics', 'N/A')}")
                
                # SEO Performance
                seo = company_data.get('seo_performance', {})
                tech_seo = seo.get('technical_seo', [])
                print(f"\n🔍 SEO Technical Features:")
                for feature in tech_seo:
                    print(f"   ✅ {feature}")
                
                # UX Rating
                ux = company_data.get('website_user_experience', {})
                ux_rating = ux.get('overall_ux_rating', 'N/A')
                print(f"\n👥 User Experience Rating:")
                print(f"   {ux_rating}")
                
                # Online Marketing
                marketing = company_data.get('online_marketing_presence', {})
                social_channels = marketing.get('social_media_channels', [])
                print(f"\n📱 Social Media Channels ({len(social_channels)}):")
                for channel in social_channels:
                    platform = channel.get('platform', 'N/A')
                    activity = channel.get('activity_level', 'N/A')
                    print(f"   • {platform}: {activity}")
        
        # Email Results anzeigen
        if "generated_emails" in final_result and final_result["generated_emails"]:
            print("\n" + "="*70)
            print("📧 GENERIERTE KALTAKQUISE-EMAIL:")
            print("="*70)
            
            for url, email in final_result["generated_emails"].items():
                print(f"\n📬 Email für: {url}")
                print("🎯 Personalisierte Kaltakquise basierend auf Research-Daten:")
                print("-" * 60)
                print(email)
                print("-" * 60)
                
                # Email in Datei speichern
                company_name = final_result["info"][url].get('company_name', 'company').lower().replace(' ', '_')
                email_filename = f"kaltakquise_email_{company_name}.txt"
                
                with open(email_filename, 'w', encoding='utf-8') as f:
                    f.write(f"KALTAKQUISE-EMAIL FÜR: {url}\n")
                    f.write(f"GENERIERT AM: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                    f.write("="*60 + "\n\n")
                    f.write(email)
                    f.write(f"\n\n" + "="*60)
                    f.write(f"\nBASIERT AUF RESEARCH-DATEN:")
                    f.write(f"\n- Unique Selling Proposition: {final_result['info'][url].get('unique_selling_proposition', 'N/A')}")
                    f.write(f"\n- SEO Features: {', '.join(final_result['info'][url].get('seo_performance', {}).get('technical_seo', []))}")
                    f.write(f"\n- UX Rating: {final_result['info'][url].get('website_user_experience', {}).get('overall_ux_rating', 'N/A')}")
                
                print(f"\n💾 Email gespeichert in: {email_filename}")
                
            print(f"\n🎉 SUCCESS! Email-Generierung basierend auf umfassendem Company Research erfolgreich!")
            print(f"📊 Research-Datenpunkte: {len(final_result['info'])}")
            print(f"📧 Generierte Emails: {len(final_result['generated_emails'])}")
        else:
            print(f"\n❌ Keine Emails generiert")
            print(f"   Grund: generated_emails = {final_result.get('generated_emails', 'KEY_MISSING')}")
        
        # Vollständiges Result für Debugging speichern
        import json
        with open("complete_analysis_result.json", "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Vollständige Analyse gespeichert: complete_analysis_result.json")
                
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())