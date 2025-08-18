# main_easy.py - Easy Company Research with config.py

import asyncio
import os
from dotenv import load_dotenv
from config import get_current_config, print_current_config
from src.agent.graph import graph
from src.agent.state import EXTENDED_EXTRACTION_SCHEMA
from src.agent.debug_utils import analyze_data_quality, print_quality_report

load_dotenv()

async def run_easy_analysis():
    """Run analysis with easy configuration from config.py"""
    
    print("🚀 EASY COMPANY RESEARCH + META INTELLIGENCE")
    print("=" * 80)
    
    # Load configuration from config.py
    config = get_current_config()
    
    print("📋 Loaded Configuration:")
    print_current_config()
    
    print(f"\n🔧 Meta API Token: {'✅ Found' if os.getenv('META_API_ACCESS_TOKEN') else '❌ Missing'}")
    
    # Confirm before running
    print(f"\n❓ Run analysis with this configuration?")
    confirm = input("Press ENTER to continue or 'q' to quit: ").strip().lower()
    
    if confirm == 'q':
        print("❌ Analysis cancelled")
        return
    
    # Build state from config
    direct_state = {
        "urls": config["urls"],
        "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
        "user_notes": config["analysis_notes"],
        "completed_notes": [],
        "info": {},
        "is_satisfactory": {},
        "reflection_steps_taken": {},
        "meta_ad_intelligence": {},
        "generate_cold_email": config["generate_emails"],
        "email_config": config["email_config"],
        "generated_emails": {}
    }
    
    try:
        print(f"\n🚀 Starting analysis for {len(config['urls'])} companies...")
        
        # Run the analysis
        final_result = await graph.ainvoke(direct_state)
        
        print(f"\n✅ Analysis completed successfully!")
        
        # Show results summary
        await show_results_summary(final_result, config)
        
        # Save results if requested
        if config["save_results"]:
            await save_detailed_results(final_result, config)
        
        print(f"\n🎉 EASY ANALYSIS COMPLETE!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def show_results_summary(final_result, config):
    """Show a summary of results."""
    
    print(f"\n📊 RESULTS SUMMARY:")
    print("=" * 50)
    
    urls_processed = len(final_result.get('info', {}))
    meta_analysis_done = len(final_result.get('meta_ad_intelligence', {}))
    emails_generated = len(final_result.get('generated_emails', {}))
    
    print(f"🌐 Companies analyzed: {urls_processed}")
    print(f"🧠 Meta intelligence: {meta_analysis_done}")
    print(f"📧 Emails generated: {emails_generated}")
    
    # Show each company
    for url in config["urls"]:
        if url in final_result.get('info', {}):
            website_data = final_result['info'][url]
            meta_data = final_result.get('meta_ad_intelligence', {}).get(url, {})
            
            company_name = website_data.get('company_name', 'Unknown')
            meta_available = meta_data.get('meta_ads_available', False)
            
            print(f"\n🏢 {company_name} ({url})")
            print(f"   📱 Meta Ads: {'✅ Found' if meta_available else '❌ None detected'}")
            
            if meta_available:
                raw_data = meta_data.get('raw_performance_data', {})
                total_ads = raw_data.get('total_ads', 0)
                sophistication = raw_data.get('campaign_sophistication', 'unknown')
                print(f"   📊 {total_ads} ads, {sophistication} sophistication")
            else:
                print(f"   💡 Growth opportunity: No Meta competition detected")
            
            # Show if email was generated
            if url in final_result.get('generated_emails', {}):
                strategy = "Competitive Analysis" if meta_available else "Growth Opportunity"
                print(f"   📧 Email generated: {strategy} approach")

async def save_detailed_results(final_result, config):
    """Save detailed results to files."""
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%d%m%Y_%H%M')
    
    # Save JSON results
    json_filename = f"analysis_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Detailed results saved: {json_filename}")
    
    # Save individual emails
    if final_result.get('generated_emails'):
        print(f"📧 Individual emails saved:")
        
        for url, email in final_result['generated_emails'].items():
            # Get company info
            website_data = final_result.get('info', {}).get(url, {})
            meta_data = final_result.get('meta_ad_intelligence', {}).get(url, {})
            
            company_name = website_data.get('company_name', 'unknown')
            meta_available = meta_data.get('meta_ads_available', False)
            
            # Create filename
            company_clean = company_name.lower().replace(' ', '_').replace('-', '_')
            strategy = "competitive" if meta_available else "opportunity"
            email_filename = f"email_{company_clean}_{strategy}_{timestamp}.txt"
            
            # Save email with metadata
            with open(email_filename, 'w', encoding='utf-8') as f:
                f.write(f"INTELLIGENT COLD EMAIL\n")
                f.write(f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write(f"Company: {company_name}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Strategy: {strategy.title()}\n")
                f.write(f"Template: {config['template_used']}\n")
                f.write(f"Industry Focus: {config['industry_focus']}\n")
                f.write("=" * 70 + "\n\n")
                f.write(email)
                f.write(f"\n\n" + "=" * 70)
                f.write(f"\nMETA INTELLIGENCE STATUS:")
                f.write(f"\n- Meta Ads Detected: {'Yes' if meta_available else 'No'}")
                f.write(f"\n- Email Strategy: {strategy.title()}")
                
                if meta_available:
                    raw_data = meta_data.get('raw_performance_data', {})
                    f.write(f"\n- Total Ads Found: {raw_data.get('total_ads', 'N/A')}")
                    f.write(f"\n- Campaign Sophistication: {raw_data.get('campaign_sophistication', 'N/A')}")
            
            print(f"   📄 {email_filename}")

async def quick_test():
    """Quick test of the configuration."""
    
    print("🧪 QUICK CONFIG TEST")
    print("=" * 40)
    
    config = get_current_config()
    
    print(f"✅ Config loaded successfully")
    print(f"📊 Target URLs: {len(config['urls'])}")
    print(f"👤 Sender: {config['email_config']['sender_name']}")
    print(f"📧 Template: {config['template_used']}")
    print(f"🏭 Industry: {config['industry_focus']}")
    
    # Test Meta API connection
    from src.agent.meta_intelligent_hybrid import IntelligentMetaHybrid
    
    meta_client = IntelligentMetaHybrid()
    api_ok, api_status = await meta_client.check_api_availability()
    
    print(f"🔧 Meta API: {'✅' if api_ok else '❌'} - {api_status}")
    
    if config['urls']:
        print(f"\n🔍 Testing with first URL: {config['urls'][0]}")
        
        try:
            from src.agent.meta_intelligent_hybrid import get_intelligent_meta_analysis
            result = await get_intelligent_meta_analysis(config['urls'][0])
            
            if result['success']:
                company_name = result.get('company_name', 'Unknown')
                meta_available = result.get('meta_ads_available', False)
                
                print(f"✅ Test successful for {company_name}")
                print(f"📱 Meta Ads: {'Found' if meta_available else 'Not detected'}")
            else:
                print(f"⚠️ Test result: {result.get('message', 'Unknown status')}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    print("🎯 Choose Mode:")
    print("1. Run Full Analysis (with current config.py)")
    print("2. Quick Config Test")
    print("3. Show Current Config")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "2":
        asyncio.run(quick_test())
    elif choice == "3":
        config = get_current_config()
        print_current_config()
    else:
        asyncio.run(run_easy_analysis())