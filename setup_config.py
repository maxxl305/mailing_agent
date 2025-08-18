# setup_config.py - Interactive Configuration Setup

import os

def interactive_setup():
    """Interactive setup to create/update config.py"""
    
    print("🔧 INTERACTIVE CONFIGURATION SETUP")
    print("=" * 50)
    print("This will help you set up config.py for your cold email research.")
    print()
    
    # 1. Personal Information
    print("👤 STEP 1: Your Information")
    print("-" * 30)
    
    your_name = input("Your Name: ").strip() or "Max Mustermann"
    your_company = input("Your Company: ").strip() or "Your Marketing Agency"
    your_role = input("Your Role: ").strip() or "Marketing Specialist"
    
    # 2. Target Companies
    print(f"\n🎯 STEP 2: Target Companies")
    print("-" * 30)
    print("Enter URLs of companies you want to analyze (one per line).")
    print("Press ENTER on empty line when done.")
    
    target_urls = []
    while True:
        url = input(f"URL {len(target_urls) + 1}: ").strip()
        if not url:
            break
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        target_urls.append(url)
    
    if not target_urls:
        target_urls = ["https://example-company.com"]
        print("No URLs entered, using example URL.")
    
    # 3. Email Template
    print(f"\n📧 STEP 3: Email Template")
    print("-" * 30)
    
    templates = {
        "1": "Meta Advertising Specialist",
        "2": "Digital Marketing Consultant", 
        "3": "Growth Hacker",
        "4": "Marketing Consultant"
    }
    
    print("Choose your email template:")
    for key, value in templates.items():
        print(f"  {key}. {value}")
    
    template_choice = input("Choose (1-4): ").strip() or "1"
    
    template_map = {
        "1": "meta_specialist",
        "2": "digital_marketing",
        "3": "growth_hacker",
        "4": "consultant"
    }
    
    selected_template = template_map.get(template_choice, "meta_specialist")
    
    # 4. Industry Focus
    print(f"\n🏭 STEP 4: Industry Focus")
    print("-" * 30)
    
    industries = {
        "1": "Fitness & Health",
        "2": "E-Commerce & Retail",
        "3": "B2B Services",
        "4": "Local Businesses"
    }
    
    print("Choose your industry focus:")
    for key, value in industries.items():
        print(f"  {key}. {value}")
    
    industry_choice = input("Choose (1-4): ").strip() or "1"
    
    industry_map = {
        "1": "fitness",
        "2": "ecommerce", 
        "3": "b2b",
        "4": "local"
    }
    
    selected_industry = industry_map.get(industry_choice, "fitness")
    
    # 5. Email Settings
    print(f"\n⚙️ STEP 5: Email Settings")
    print("-" * 30)
    
    email_language = input("Email Language (deutsch/english) [deutsch]: ").strip() or "deutsch"
    email_length = input("Email Length (short/medium/long) [medium]: ").strip() or "medium"
    
    # 6. Generate config.py
    print(f"\n📝 STEP 6: Generate Configuration")
    print("-" * 30)
    
    config_content = generate_config_content(
        your_name, your_company, your_role,
        target_urls, selected_template, selected_industry,
        email_language, email_length
    )
    
    # Preview
    print("Preview of your configuration:")
    print("=" * 40)
    print(f"Name: {your_name}")
    print(f"Company: {your_company}")
    print(f"Role: {your_role}")
    print(f"Target URLs: {len(target_urls)} companies")
    print(f"Template: {templates[template_choice]}")
    print(f"Industry: {industries[industry_choice]}")
    print(f"Language: {email_language}")
    print("=" * 40)
    
    # Confirm and save
    save_config = input(f"\nSave this configuration to config.py? (y/n) [y]: ").strip().lower()
    
    if save_config != 'n':
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"\n✅ Configuration saved to config.py!")
        print(f"\n🚀 Next steps:")
        print(f"1. Set your META_API_ACCESS_TOKEN in .env file")
        print(f"2. Run: python main_easy.py")
        print(f"3. Choose option 1 to run the full analysis")
    else:
        print(f"\n❌ Configuration not saved.")

def generate_config_content(name, company, role, urls, template, industry, language, length):
    """Generate the config.py file content."""
    
    urls_str = ",\n    ".join([f'"{url}"' for url in urls])
    
    return f'''# config.py - Generated Configuration

"""
GENERATED CONFIGURATION for Company Research + Meta Intelligence
Created with setup_config.py

To modify: Either edit values below or run setup_config.py again
"""

# ⭐ 1. ZIEL-UNTERNEHMEN (URLs)
TARGET_COMPANIES = [
    {urls_str}
]

# ⭐ 2. DEINE FIRMA & PERSÖNLICHE DATEN
YOUR_COMPANY = "{company}"
YOUR_NAME = "{name}"
YOUR_ROLE = "{role}"

# ⭐ 3. DEIN SERVICE-ANGEBOT (wird durch Template überschrieben)
SERVICE_OFFERING = "Marketing-Optimierung mit intelligenter Competitive Analysis"

# ⭐ 4. EMAIL-EINSTELLUNGEN
EMAIL_CONFIG = {{
    "email_tone": "professionell mit transparenten Markt-Insights",
    "email_length": "{length}",
    "call_to_action": "kostenloses Assessment und Strategiegespräch",
    "email_language": "{language}"
}}

# ⭐ 5. ANALYSE-EINSTELLUNGEN
ANALYSIS_NOTES = "Intelligent analysis mit professional Meta API assessment - Focus auf B2B-Marketing mit transparenter Competitive Intelligence"

# ⭐ 6. OUTPUT-EINSTELLUNGEN
GENERATE_EMAILS = True
SAVE_DETAILED_RESULTS = True

# ⭐ 7. EMAIL-TEMPLATES
EMAIL_TEMPLATES = {{
    "meta_specialist": {{
        "service_offering": "Meta Advertising-Optimierung mit Real-Time Market Intelligence",
        "email_tone": "professionell mit echten Competitive Insights",
        "call_to_action": "kostenloses Meta Advertising Audit mit echten Marktdaten"
    }},
    
    "digital_marketing": {{
        "service_offering": "Digitale Marketing-Transformation und Performance-Optimierung",
        "email_tone": "beratend mit datengestützten Insights",
        "call_to_action": "unverbindliches Strategiegespräch über Ihre digitale Sichtbarkeit"
    }},
    
    "growth_hacker": {{
        "service_offering": "Growth Hacking und systematische Umsatzsteigerung",
        "email_tone": "direkt mit konkreten Wachstumschancen",
        "call_to_action": "kostenloses Growth-Assessment Ihrer Online-Präsenz"
    }},
    
    "consultant": {{
        "service_offering": "Marketing-Beratung und strategische Positionierung",
        "email_tone": "sachlich mit fundierten Marktanalysen",
        "call_to_action": "unverbindlichen Termin für eine Marktanalyse"
    }}
}}

# Aktuell verwendetes Template
CURRENT_TEMPLATE = "{template}"

# ⭐ 8. BRANCHE-SPEZIFISCHE ANPASSUNGEN
INDUSTRY_FOCUS = {{
    "fitness": {{
        "notes": "Focus auf lokale Fitnessstudios und Health & Wellness Marketing",
        "keywords": ["Mitgliedergewinnung", "Fitnesstrends", "Community Building"]
    }},
    "ecommerce": {{
        "notes": "Focus auf Online-Shops und E-Commerce Performance",
        "keywords": ["Conversion-Optimierung", "Shopping-Campaigns", "Retargeting"]
    }},
    "b2b": {{
        "notes": "Focus auf B2B-Unternehmen und Lead-Generierung",
        "keywords": ["Lead-Qualität", "Sales-Funnel", "Account-Based Marketing"]
    }},
    "local": {{
        "notes": "Focus auf lokale Unternehmen und regionale Sichtbarkeit",
        "keywords": ["Local SEO", "Standort-Marketing", "Lokale Konkurrenz"]
    }}
}}

# Aktueller Branchen-Focus
CURRENT_INDUSTRY = "{industry}"

# ===================================================================
# INTERNE FUNKTIONEN (normalerweise nicht ändern)
# ===================================================================

def get_email_config():
    """Holt die aktuelle Email-Konfiguration."""
    
    config = EMAIL_CONFIG.copy()
    
    if CURRENT_TEMPLATE in EMAIL_TEMPLATES:
        template = EMAIL_TEMPLATES[CURRENT_TEMPLATE]
        config.update({{
            "sender_company": YOUR_COMPANY,
            "sender_name": YOUR_NAME,
            "sender_role": YOUR_ROLE,
            "service_offering": template["service_offering"],
            "email_tone": template["email_tone"],
            "call_to_action": template["call_to_action"]
        }})
    else:
        config.update({{
            "sender_company": YOUR_COMPANY,
            "sender_name": YOUR_NAME,
            "sender_role": YOUR_ROLE,
            "service_offering": SERVICE_OFFERING
        }})
    
    return config

def get_analysis_notes():
    """Holt die Analyse-Notizen mit Branchen-Focus."""
    
    base_notes = ANALYSIS_NOTES
    
    if CURRENT_INDUSTRY in INDUSTRY_FOCUS:
        industry_info = INDUSTRY_FOCUS[CURRENT_INDUSTRY]
        industry_notes = industry_info["notes"]
        keywords = ", ".join(industry_info["keywords"])
        
        enhanced_notes = f"{{base_notes}} | {{industry_notes}} | Keywords: {{keywords}}"
        return enhanced_notes
    
    return base_notes

def get_current_config():
    """Holt die komplette aktuelle Konfiguration."""
    
    return {{
        "urls": TARGET_COMPANIES,
        "email_config": get_email_config(),
        "analysis_notes": get_analysis_notes(),
        "generate_emails": GENERATE_EMAILS,
        "save_results": SAVE_DETAILED_RESULTS,
        "template_used": CURRENT_TEMPLATE,
        "industry_focus": CURRENT_INDUSTRY
    }}

def print_current_config():
    """Zeigt die aktuelle Konfiguration an."""
    
    config = get_current_config()
    
    print("📋 AKTUELLE KONFIGURATION:")
    print("=" * 50)
    print(f"🎯 Target Companies: {{len(config['urls'])}}")
    for i, url in enumerate(config['urls'], 1):
        print(f"   {{i}}. {{url}}")
    
    print(f"\\n👤 Sender: {{config['email_config']['sender_name']}}")
    print(f"🏢 Company: {{config['email_config']['sender_company']}}")
    print(f"💼 Role: {{config['email_config']['sender_role']}}")
    print(f"🎯 Service: {{config['email_config']['service_offering']}}")
    print(f"📧 Template: {{config['template_used']}}")
    print(f"🏭 Industry Focus: {{config['industry_focus']}}")
    print(f"📬 Generate Emails: {{'✅' if config['generate_emails'] else '❌'}}")
    
    return config

if __name__ == "__main__":
    print("🔧 CONFIGURATION PREVIEW")
    print_current_config()
'''

if __name__ == "__main__":
    interactive_setup()