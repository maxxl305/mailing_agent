# main.py - Erweitert mit verbesserter Reflection-Logik und Debug-Tools

import asyncio
from src.agent.graph import graph
from src.agent.state import EXTENDED_EXTRACTION_SCHEMA
from src.agent.debug_utils import debug_state_data, analyze_data_quality, print_quality_report

async def main():
    print("Company Research + Meta Ad Intelligence + Email Generation")
    print("🔧 With IMPROVED Reflection Logic - Less Strict Evaluation!")
    print("=" * 80)
    
    direct_state = {
        "urls": ["https://palestra-fitness.de"],
        "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
        "user_notes": "Fokus auf B2B-Marketing, Digitalisierung und Meta Advertising-Optimierung",
        "completed_notes": [],
        "info": {},
        "is_satisfactory": {},
        "reflection_steps_taken": {},
        "meta_ad_intelligence": {},  # ⭐ NEU
        
        "generate_cold_email": True,
        "email_config": {
            "sender_company": "Max & Jonas Digital Marketing GmbH",
            "sender_name": "Max Siegl", 
            "sender_role": "Meta Advertising Specialist",
            "service_offering": "Meta Advertising-Optimierung und Digitale Marketing-Transformation",
            "email_tone": "professionell mit einem Hauch von Expertise",
            "email_length": "medium",
            "call_to_action": "kostenloses Meta Advertising Audit und Strategiegespräch",
            "email_language": "deutsch"
        },
        "generated_emails": {}
    }
    
    print("📋 Erweiterte Konfiguration:")
    print(f"   🎯 Target: {direct_state['urls'][0]}")
    print(f"   📧 Email: {direct_state['generate_cold_email']}")  
    print(f"   👤 Sender: {direct_state['email_config']['sender_name']}")
    print(f"   🏢 Company: {direct_state['email_config']['sender_company']}")
    print(f"   🎯 Service: {direct_state['email_config']['service_offering']}")
    print(f"   📱 Meta Ad Intelligence: AKTIVIERT")
    print(f"   🔧 Reflection Logic: IMPROVED (Pragmatic)")
    print()
    
    try:
        print("🚀 Starte erweiterte Company Research mit verbesserter Logik...")
        
        # ⚠️ Verwende ainvoke für komplettes Result mit Meta Ad Intelligence
        final_result = await graph.ainvoke(direct_state)
        
        print("\n✅ Erweiterte Analyse erfolgreich abgeschlossen!")
        print(f"📊 Result Keys: {list(final_result.keys())}")
        
        # ⭐ NEUE DEBUG-ANALYSE für jede URL
        print("\n" + "="*80)
        print("🔍 DATA QUALITY ANALYSIS:")
        print("="*80)
        
        for url in direct_state['urls']:
            if url in final_result.get('info', {}):
                website_data = final_result['info'][url]
                meta_data = final_result.get('meta_ad_intelligence', {}).get(url)
                
                quality_report = analyze_data_quality(website_data, meta_data)
                print_quality_report(quality_report, url)
                
                # Check why email generation might have failed
                if not final_result.get('generated_emails', {}).get(url):
                    print(f"\n⚠️  EMAIL GENERATION ANALYSIS for {url}:")
                    print(f"   Email Readiness: {'✅' if quality_report['email_readiness'] else '❌'}")
                    print(f"   Missing Fields: {quality_report['missing_fields']}")
                    if quality_report['recommendations']:
                        print(f"   Recommendations: {quality_report['recommendations'][0]}")
        
        # Website Research Results anzeigen
        if "info" in final_result and final_result["info"]:
            print("\n" + "="*80)
            print("📊 WEBSITE RESEARCH RESULTS:")
            print("="*80)
            
            for url, company_data in final_result["info"].items():
                name = company_data.get('company_name', 'Unbekannt')
                print(f"\n🏢 Unternehmen: {name}")
                print(f"🌐 URL: {url}")
                
                # Key Insights
                usp = company_data.get('unique_selling_proposition', 'N/A')
                print(f"🎯 Unique Selling Proposition:")
                print(f"   {usp}")
                
                # UX Rating
                ux = company_data.get('website_user_experience', {})
                ux_rating = ux.get('overall_ux_rating', 'N/A')
                print(f"\n👥 User Experience Rating: {ux_rating}")
                
                # Show data completeness
                total_fields = len(EXTENDED_EXTRACTION_SCHEMA['properties'])
                filled_fields = len([k for k, v in company_data.items() if v])
                completeness = round((filled_fields / total_fields) * 100, 1)
                print(f"📈 Data Completeness: {completeness}% ({filled_fields}/{total_fields} fields)")
        
        # ⭐ META AD INTELLIGENCE RESULTS
        if "meta_ad_intelligence" in final_result and final_result["meta_ad_intelligence"]:
            print("\n" + "="*80)
            print("🎯 META ADVERTISING INTELLIGENCE RESULTS:")
            print("="*80)
            
            for url, ad_data in final_result["meta_ad_intelligence"].items():
                print(f"\n📱 Meta Ad Analysis für: {url}")
                
                if "llm_analysis" in ad_data:
                    llm_analysis = ad_data["llm_analysis"]
                    
                    print(f"📊 Advertising Status: {llm_analysis.get('advertising_status', 'N/A')}")
                    print(f"🔥 Sophistication Level: {llm_analysis.get('advertising_sophistication_level', 'N/A')}")
                    
                    print(f"\n📈 Active Campaigns Summary:")
                    print(f"   {llm_analysis.get('active_campaigns_summary', 'N/A')}")
                    
                    print(f"\n🎨 Creative Strategy:")
                    print(f"   {llm_analysis.get('creative_strategy_analysis', 'N/A')}")
                    
                    print(f"\n🎯 Targeting Insights:")
                    print(f"   {llm_analysis.get('targeting_insights', 'N/A')}")
                    
                    print(f"\n💰 Budget Assessment:")
                    print(f"   {llm_analysis.get('budget_assessment', 'N/A')}")
                    
                    # Optimization Opportunities
                    opportunities = llm_analysis.get('optimization_opportunities', [])
                    if opportunities:
                        print(f"\n🚀 Optimization Opportunities ({len(opportunities)}):")
                        for i, opp in enumerate(opportunities, 1):
                            print(f"   {i}. {opp}")
                
                # Raw Performance Data
                if "raw_performance_data" in ad_data:
                    raw_data = ad_data["raw_performance_data"]
                    print(f"\n📊 Performance Metrics:")
                    print(f"   Total Ads: {raw_data.get('total_ads', 'N/A')}")
                    print(f"   Active Ads: {raw_data.get('active_ads', 'N/A')}")
                    print(f"   Est. Monthly Spend: {raw_data.get('estimated_monthly_spend', 'N/A')}")
                    print(f"   Sophistication: {raw_data.get('campaign_sophistication', 'N/A')}")
        
        # ⭐ ENHANCED EMAIL RESULTS (jetzt mit Meta Ad Intelligence)
        if "generated_emails" in final_result and final_result["generated_emails"]:
            print("\n" + "="*80)
            print("📧 ENHANCED KALTAKQUISE-EMAIL (mit Meta Ad Intelligence):")
            print("="*80)
            
            for url, email in final_result["generated_emails"].items():
                print(f"\n📬 Personalisierte Email für: {url}")
                print("🎯 Email basierend auf Website + Meta Ad Intelligence:")
                print("-" * 70)
                print(email)
                print("-" * 70)
                
                # Enhanced Email in Datei speichern
                company_name = final_result["info"][url].get('company_name', 'company').lower().replace(' ', '_')
                email_filename = f"enhanced_kaltakquise_email_{company_name}.txt"
                
                with open(email_filename, 'w', encoding='utf-8') as f:
                    f.write(f"ENHANCED KALTAKQUISE-EMAIL MIT META AD INTELLIGENCE\n")
                    f.write(f"FÜR: {url}\n")
                    f.write(f"GENERIERT AM: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                    f.write("="*70 + "\n\n")
                    f.write(email)
                    f.write(f"\n\n" + "="*70)
                    f.write(f"\nBASIERT AUF UMFASSENDER ANALYSE:")
                    f.write(f"\n\n📊 WEBSITE RESEARCH:")
                    f.write(f"\n- USP: {final_result['info'][url].get('unique_selling_proposition', 'N/A')}")
                    f.write(f"\n- UX Rating: {final_result['info'][url].get('website_user_experience', {}).get('overall_ux_rating', 'N/A')}")
                    
                    if url in final_result.get("meta_ad_intelligence", {}):
                        meta_data = final_result["meta_ad_intelligence"][url]
                        if "llm_analysis" in meta_data:
                            llm_analysis = meta_data["llm_analysis"]
                            f.write(f"\n\n📱 META ADVERTISING INTELLIGENCE:")
                            f.write(f"\n- Advertising Status: {llm_analysis.get('advertising_status', 'N/A')}")
                            f.write(f"\n- Sophistication: {llm_analysis.get('advertising_sophistication_level', 'N/A')}")
                            f.write(f"\n- Key Opportunities: {', '.join(llm_analysis.get('optimization_opportunities', [])[:3])}")
                
                print(f"\n💾 Enhanced Email gespeichert in: {email_filename}")
                
            print(f"\n🎉 SUCCESS! Enhanced Email-Generierung mit Meta Ad Intelligence!")
            print(f"📊 Website Research: {len(final_result['info'])} companies")
            print(f"🎯 Meta Ad Intelligence: {len(final_result.get('meta_ad_intelligence', {}))} companies")
            print(f"📧 Generated Emails: {len(final_result['generated_emails'])} emails")
        else:
            print(f"\n❌ Keine Emails generiert - Analyzing why...")
            
            # Analyze why email generation failed
            for url in direct_state['urls']:
                print(f"\n🔍 Email Generation Debug für {url}:")
                
                # Check if data exists
                has_website_data = url in final_result.get('info', {})
                has_meta_data = url in final_result.get('meta_ad_intelligence', {})
                email_requested = direct_state.get('generate_cold_email', False)
                email_config = bool(direct_state.get('email_config'))
                
                print(f"   Website Data: {'✅' if has_website_data else '❌'}")
                print(f"   Meta Ad Data: {'✅' if has_meta_data else '❌'}")
                print(f"   Email Requested: {'✅' if email_requested else '❌'}")
                print(f"   Email Config: {'✅' if email_config else '❌'}")
                
                if has_website_data:
                    website_data = final_result['info'][url]
                    meta_data = final_result.get('meta_ad_intelligence', {}).get(url)
                    quality_report = analyze_data_quality(website_data, meta_data)
                    
                    print(f"   Data Quality Score: {quality_report['overall_score']}%")
                    print(f"   Email Ready: {'✅' if quality_report['email_readiness'] else '❌'}")
                    
                    if not quality_report['email_readiness']:
                        print(f"   Missing: {', '.join(quality_report['missing_fields'])}")
            
            print(f"\n💡 RECOMMENDATION: The improved reflection logic should have fixed this!")
            print(f"   If emails still aren't generated, check the email_config and routing logic.")
        
        # Vollständiges Enhanced Result für Debugging speichern
        import json
        with open("enhanced_analysis_with_improved_logic.json", "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Vollständige Enhanced Analyse gespeichert: enhanced_analysis_with_improved_logic.json")
        
        # Summary Statistics
        print(f"\n📈 IMPROVEMENT SUMMARY:")
        print(f"   🌐 Website Analysis: ✅ Complete")
        print(f"   🎯 Meta Ad Intelligence: ✅ {'Complete' if final_result.get('meta_ad_intelligence') else 'Failed'}")
        print(f"   📧 Email Generation: ✅ {'Complete' if final_result.get('generated_emails') else 'Failed'}")
        print(f"   🧠 Reflection Logic: ✅ Improved (Pragmatic)")
        print(f"   🔧 Debug Tools: ✅ Active")
        
        # Final recommendation
        if final_result.get('generated_emails'):
            print(f"\n🎉 SUCCESS! Die verbesserte Reflection-Logik funktioniert!")
        else:
            print(f"\n⚠️  If email generation still failed, check the debug output above.")
            print(f"   The new pragmatic reflection should be much more lenient.")
                
    except Exception as e:
        print(f"❌ Fehler bei erweiterte Analyse: {str(e)}")
        import traceback
        traceback.print_exc()

# ⭐ NEW: Debug-only function to test data quality
async def debug_reflection_logic():
    """Test the new reflection logic with Palestra Fitness data."""
    print("\n🔍 TESTING NEW REFLECTION LOGIC")
    print("="*50)
    
    # Simple test with minimal config
    test_state = {
        "urls": ["https://palestra-fitness.de"],
        "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
        "user_notes": "Debug test",
        "generate_cold_email": False,  # Just test data extraction
        "meta_ad_intelligence": {},
    }
    
    try:
        result = await graph.ainvoke(test_state)
        
        print(f"📊 Result Keys: {list(result.keys())}")
        
        for url in test_state['urls']:
            if url in result.get('info', {}):
                website_data = result['info'][url]
                meta_data = result.get('meta_ad_intelligence', {}).get(url)
                
                # Use debug tools
                quality_report = analyze_data_quality(website_data, meta_data)
                print_quality_report(quality_report, url)
                
                # Show specific data that was extracted
                print(f"\n📋 Extracted Data Summary for {url}:")
                print(f"   Company Name: {website_data.get('company_name', 'MISSING')}")
                print(f"   USP: {website_data.get('unique_selling_proposition', 'MISSING')[:100]}...")
                print(f"   Marketing Channels: {len(website_data.get('marketing_channels', []))} found")
                print(f"   Online Presence: {'✅' if website_data.get('online_marketing_presence') else '❌'}")
                
    except Exception as e:
        print(f"❌ Debug test failed: {str(e)}")

if __name__ == "__main__":
    print("🎯 Wähle Test-Modus:")
    print("1. Full Analysis mit improved logic (+ Email)")
    print("2. Debug Reflection Logic only")
    
    choice = input("Eingabe (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(debug_reflection_logic())
    else:
        asyncio.run(main())