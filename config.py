# config.py - Generated Configuration

"""
GENERATED CONFIGURATION for Company Research + Meta Intelligence
Created with setup_config.py

To modify: Either edit values below or run setup_config.py again
"""

# ⭐ 1. ZIEL-UNTERNEHMEN (URLs)
TARGET_COMPANIES = [
    "https://www.jvm.com"
]

# ⭐ 2. DEINE FIRMA & PERSÖNLICHE DATEN
YOUR_COMPANY = "Mobile Fusion"
YOUR_NAME = "Jonas Kremser"
YOUR_ROLE = "CEO"

# ⭐ 3. DEIN SERVICE-ANGEBOT (wird durch Template überschrieben)
SERVICE_OFFERING = "Marketing-Optimierung mit intelligenter Competitive Analysis"

# ⭐ 4. EMAIL-EINSTELLUNGEN
EMAIL_CONFIG = {
    "email_tone": "professionell mit transparenten Markt-Insights",
    "email_length": "medium",
    "call_to_action": "kostenloses Assessment und Strategiegespräch",
    "email_language": "deutsch"
}

# ⭐ 5. ANALYSE-EINSTELLUNGEN
ANALYSIS_NOTES = "Intelligent analysis mit professional Meta API assessment - Focus auf B2B-Marketing mit transparenter Competitive Intelligence"

# ⭐ 6. OUTPUT-EINSTELLUNGEN
GENERATE_EMAILS = True
SAVE_DETAILED_RESULTS = True

# ⭐ 7. EMAIL-TEMPLATES
EMAIL_TEMPLATES = {
    "meta_specialist": {
        "service_offering": "Meta Advertising-Optimierung mit Real-Time Market Intelligence",
        "email_tone": "professionell mit echten Competitive Insights",
        "call_to_action": "kostenloses Meta Advertising Audit mit echten Marktdaten"
    },
    
    "digital_marketing": {
        "service_offering": "Digitale Marketing-Transformation und Performance-Optimierung",
        "email_tone": "beratend mit datengestützten Insights",
        "call_to_action": "unverbindliches Strategiegespräch über Ihre digitale Sichtbarkeit"
    },
    
    "growth_hacker": {
        "service_offering": "Growth Hacking und systematische Umsatzsteigerung",
        "email_tone": "direkt mit konkreten Wachstumschancen",
        "call_to_action": "kostenloses Growth-Assessment Ihrer Online-Präsenz"
    },
    
    "consultant": {
        "service_offering": "Marketing-Beratung und strategische Positionierung",
        "email_tone": "sachlich mit fundierten Marktanalysen",
        "call_to_action": "unverbindlichen Termin für eine Marktanalyse"
    }
}

# Aktuell verwendetes Template
CURRENT_TEMPLATE = "meta_specialist"

# ⭐ 8. BRANCHE-SPEZIFISCHE ANPASSUNGEN
INDUSTRY_FOCUS = {
    "fitness": {
        "notes": "Focus auf lokale Fitnessstudios und Health & Wellness Marketing",
        "keywords": ["Mitgliedergewinnung", "Fitnesstrends", "Community Building"]
    },
    "ecommerce": {
        "notes": "Focus auf Online-Shops und E-Commerce Performance",
        "keywords": ["Conversion-Optimierung", "Shopping-Campaigns", "Retargeting"]
    },
    "b2b": {
        "notes": "Focus auf B2B-Unternehmen und Lead-Generierung",
        "keywords": ["Lead-Qualität", "Sales-Funnel", "Account-Based Marketing"]
    },
    "local": {
        "notes": "Focus auf lokale Unternehmen und regionale Sichtbarkeit",
        "keywords": ["Local SEO", "Standort-Marketing", "Lokale Konkurrenz"]
    }
}

# Aktueller Branchen-Focus
CURRENT_INDUSTRY = "local"

# ===================================================================
# INTERNE FUNKTIONEN (normalerweise nicht ändern)
# ===================================================================

def get_email_config():
    """Holt die aktuelle Email-Konfiguration."""
    
    config = EMAIL_CONFIG.copy()
    
    if CURRENT_TEMPLATE in EMAIL_TEMPLATES:
        template = EMAIL_TEMPLATES[CURRENT_TEMPLATE]
        config.update({
            "sender_company": YOUR_COMPANY,
            "sender_name": YOUR_NAME,
            "sender_role": YOUR_ROLE,
            "service_offering": template["service_offering"],
            "email_tone": template["email_tone"],
            "call_to_action": template["call_to_action"]
        })
    else:
        config.update({
            "sender_company": YOUR_COMPANY,
            "sender_name": YOUR_NAME,
            "sender_role": YOUR_ROLE,
            "service_offering": SERVICE_OFFERING
        })
    
    return config

def get_analysis_notes():
    """Holt die Analyse-Notizen mit Branchen-Focus."""
    
    base_notes = ANALYSIS_NOTES
    
    if CURRENT_INDUSTRY in INDUSTRY_FOCUS:
        industry_info = INDUSTRY_FOCUS[CURRENT_INDUSTRY]
        industry_notes = industry_info["notes"]
        keywords = ", ".join(industry_info["keywords"])
        
        enhanced_notes = f"{base_notes} | {industry_notes} | Keywords: {keywords}"
        return enhanced_notes
    
    return base_notes

def get_current_config():
    """Holt die komplette aktuelle Konfiguration."""
    
    return {
        "urls": TARGET_COMPANIES,
        "email_config": get_email_config(),
        "analysis_notes": get_analysis_notes(),
        "generate_emails": GENERATE_EMAILS,
        "save_results": SAVE_DETAILED_RESULTS,
        "template_used": CURRENT_TEMPLATE,
        "industry_focus": CURRENT_INDUSTRY
    }

def print_current_config():
    """Zeigt die aktuelle Konfiguration an."""
    
    config = get_current_config()
    
    print("📋 AKTUELLE KONFIGURATION:")
    print("=" * 50)
    print(f"🎯 Target Companies: {len(config['urls'])}")
    for i, url in enumerate(config['urls'], 1):
        print(f"   {i}. {url}")
    
    print(f"\n👤 Sender: {config['email_config']['sender_name']}")
    print(f"🏢 Company: {config['email_config']['sender_company']}")
    print(f"💼 Role: {config['email_config']['sender_role']}")
    print(f"🎯 Service: {config['email_config']['service_offering']}")
    print(f"📧 Template: {config['template_used']}")
    print(f"🏭 Industry Focus: {config['industry_focus']}")
    print(f"📬 Generate Emails: {'✅' if config['generate_emails'] else '❌'}")
    
    return config

if __name__ == "__main__":
    print("🔧 CONFIGURATION PREVIEW")
    print_current_config()
