# src/agent/meta_ad_client.py - Mock Client für Meta Ad Library API

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio


@dataclass
class MetaAdData:
    """Struktur für Meta Ad Library Daten"""
    ad_id: str
    page_name: str
    ad_creative_body: str
    ad_creative_link_caption: str
    ad_creative_link_description: str
    ad_creative_link_title: str
    ad_delivery_start_time: str
    ad_delivery_stop_time: Optional[str]
    ad_snapshot_url: str
    currency: str
    demographic_distribution: List[Dict[str, Any]]
    impressions: Dict[str, str]
    languages: List[str]
    page_id: str
    publisher_platforms: List[str]
    region_distribution: List[Dict[str, Any]]


class MetaAdLibraryMockClient:
    """
    Mock Client für Meta Ad Library API.
    Simuliert realistische Daten für Company Research.
    Später einfach durch echten Client ersetzen.
    """

    def __init__(self, access_token: str = "mock_token"):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Mock-Daten Templates
        self.mock_industries = {
            "fitness": {
                "ad_themes": [
                    "Transform your body in 30 days",
                    "Join thousands who achieved their dream body",
                    "Professional training from home",
                    "No gym? No problem!",
                    "Summer body starts now"
                ],
                "cta_buttons": ["Jetzt starten", "Mehr erfahren", "Termin buchen", "Kostenlos testen"],
                "demographics": ["25-34", "35-44", "18-24"],
                "genders": ["female", "male", "all"],
                "countries": ["DE", "AT", "CH"],
                "platforms": ["facebook", "instagram"]
            },
            "software": {
                "ad_themes": [
                    "Automate your workflow today",
                    "Boost productivity by 300%",
                    "Free 14-day trial",
                    "Trusted by 50,000+ companies",
                    "Start scaling your business"
                ],
                "cta_buttons": ["Free Trial", "Demo anfordern", "Jetzt testen", "Mehr erfahren"],
                "demographics": ["25-34", "35-44", "45-54"],
                "genders": ["all"],
                "countries": ["DE", "US", "GB", "AT", "CH"],
                "platforms": ["facebook", "instagram", "audience_network"]
            },
            "ecommerce": {
                "ad_themes": [
                    "50% Off - Limited time only",
                    "Free shipping worldwide",
                    "New arrivals just dropped",
                    "Customer rated 5 stars",
                    "Exclusive collection"
                ],
                "cta_buttons": ["Jetzt kaufen", "Shop Now", "Angebot sichern", "Mehr erfahren"],
                "demographics": ["18-24", "25-34", "35-44"],
                "genders": ["female", "male", "all"],
                "countries": ["DE", "AT", "CH", "US"],
                "platforms": ["facebook", "instagram"]
            },
            "default": {
                "ad_themes": [
                    "Discover something amazing",
                    "Limited time offer",
                    "Join our community",
                    "Expert solutions for you",
                    "Transform your business"
                ],
                "cta_buttons": ["Mehr erfahren", "Jetzt starten", "Kontakt", "Demo"],
                "demographics": ["25-34", "35-44"],
                "genders": ["all"],
                "countries": ["DE", "AT", "CH"],
                "platforms": ["facebook", "instagram"]
            }
        }

    def _detect_industry(self, company_url: str) -> str:
        """Erkennt Industrie basierend auf URL für realistische Mock-Daten"""
        url_lower = company_url.lower()
        
        if any(word in url_lower for word in ["fitness", "gym", "sport", "training", "workout"]):
            return "fitness"
        elif any(word in url_lower for word in ["software", "saas", "tech", "app", "platform"]):
            return "software"
        elif any(word in url_lower for word in ["shop", "store", "ecommerce", "fashion", "retail"]):
            return "ecommerce"
        else:
            return "default"

    def _generate_mock_ad(self, company_name: str, industry: str, ad_id: str) -> MetaAdData:
        """Generiert ein einzelnes Mock-Advertisement"""
        industry_data = self.mock_industries[industry]
        
        # Zufällige Auswahl für realistische Variation
        theme = random.choice(industry_data["ad_themes"])
        cta = random.choice(industry_data["cta_buttons"])
        demographic = random.choice(industry_data["demographics"])
        gender = random.choice(industry_data["genders"])
        country = random.choice(industry_data["countries"])
        platforms = random.sample(industry_data["platforms"], 
                                 random.randint(1, len(industry_data["platforms"])))

        # Zeitraum für Ad-Laufzeit
        start_date = datetime.now() - timedelta(days=random.randint(1, 60))
        stop_date = None if random.random() > 0.3 else start_date + timedelta(days=random.randint(7, 30))

        # Mock Impressions (realistische Ranges)
        impression_ranges = {
            "fitness": {"min": "1000-5000", "max": "10000-50000"},
            "software": {"min": "5000-10000", "max": "50000-100000"},
            "ecommerce": {"min": "10000-25000", "max": "100000-500000"},
            "default": {"min": "1000-5000", "max": "10000-50000"}
        }
        
        impressions_range = random.choice([
            impression_ranges[industry]["min"],
            impression_ranges[industry]["max"]
        ])

        return MetaAdData(
            ad_id=ad_id,
            page_name=company_name,
            ad_creative_body=f"{theme} - {company_name}",
            ad_creative_link_caption=f"{company_name} | {cta}",
            ad_creative_link_description=f"Entdecke {theme.lower()} mit {company_name}",
            ad_creative_link_title=theme,
            ad_delivery_start_time=start_date.isoformat(),
            ad_delivery_stop_time=stop_date.isoformat() if stop_date else None,
            ad_snapshot_url=f"https://www.facebook.com/ads/library/?id={ad_id}",
            currency="EUR",
            demographic_distribution=[
                {
                    "age": demographic,
                    "gender": gender,
                    "percentage": str(round(random.uniform(0.3, 0.8), 2))
                }
            ],
            impressions={"lower_bound": impressions_range.split("-")[0], 
                        "upper_bound": impressions_range.split("-")[1]},
            languages=["de", "en"],
            page_id=f"mock_page_{hash(company_name) % 100000}",
            publisher_platforms=platforms,
            region_distribution=[
                {
                    "region": country,
                    "percentage": str(round(random.uniform(0.6, 1.0), 2))
                }
            ]
        )

    async def search_ads(self, 
                        search_terms: str, 
                        ad_reached_countries: List[str] = ["DE"],
                        limit: int = 100) -> Dict[str, Any]:
        """
        Mock-Implementation der Ad Library Search API
        
        Args:
            search_terms: Suchbegriffe (normalerweise Company Name)
            ad_reached_countries: Länder-Filter
            limit: Max Anzahl Results
            
        Returns:
            Dict mit Mock-Advertising-Daten
        """
        
        # Simuliere API-Delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Company Name aus search_terms extrahieren
        company_name = search_terms.strip()
        industry = self._detect_industry(search_terms)
        
        # Realistische Anzahl Ads basierend auf Company Size (simuliert)
        num_ads = random.choices(
            [0, 1, 2, 3, 4, 5, 8, 12, 20],
            weights=[10, 15, 20, 20, 15, 10, 5, 3, 2]  # Meiste Unternehmen haben 2-5 aktive Ads
        )[0]
        
        if num_ads == 0:
            return {
                "data": [],
                "paging": {},
                "has_ads": False,
                "total_count": 0
            }

        # Generiere Mock-Ads
        mock_ads = []
        for i in range(num_ads):
            ad_id = f"mock_ad_{hash(company_name + str(i)) % 1000000}"
            mock_ad = self._generate_mock_ad(company_name, industry, ad_id)
            mock_ads.append(mock_ad.__dict__)

        return {
            "data": mock_ads,
            "paging": {
                "cursors": {
                    "before": "mock_before_cursor",
                    "after": "mock_after_cursor"
                },
                "next": f"https://graph.facebook.com/v18.0/ads_archive?limit={limit}&after=mock_after_cursor"
            },
            "has_ads": True,
            "total_count": num_ads,
            "search_terms": search_terms,
            "countries": ad_reached_countries
        }

    async def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Mock-Implementation für Page Info API"""
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        return {
            "id": page_id,
            "name": f"Mock Page {page_id}",
            "category": "Business",
            "verification_status": "verified" if random.random() > 0.3 else "unverified",
            "page_transparency": {
                "page_created": (datetime.now() - timedelta(days=random.randint(365, 2000))).isoformat(),
                "location": random.choice(["Germany", "Austria", "Switzerland", "United States"])
            }
        }

    def analyze_ad_performance(self, ads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analysiert Mock-Ad-Performance und extrahiert Insights
        
        Args:
            ads_data: Liste von Ad-Daten aus search_ads()
            
        Returns:
            Performance-Analyse Dict
        """
        if not ads_data:
            return {
                "advertising_status": "no_ads_found",
                "performance_summary": "No active advertising campaigns found"
            }

        total_ads = len(ads_data)
        active_ads = len([ad for ad in ads_data if ad.get("ad_delivery_stop_time") is None])
        
        # Platforms Analysis
        all_platforms = []
        for ad in ads_data:
            all_platforms.extend(ad.get("publisher_platforms", []))
        platform_distribution = {platform: all_platforms.count(platform) for platform in set(all_platforms)}
        
        # Demographics Analysis
        age_groups = []
        genders = []
        for ad in ads_data:
            for demo in ad.get("demographic_distribution", []):
                if demo.get("age"):
                    age_groups.append(demo["age"])
                if demo.get("gender"):
                    genders.append(demo["gender"])
        
        # Creative Themes Analysis
        creative_themes = [ad.get("ad_creative_body", "") for ad in ads_data]
        common_words = self._extract_common_themes(creative_themes)
        
        # Estimate spend based on impressions
        total_impressions = 0
        for ad in ads_data:
            impressions = ad.get("impressions", {})
            if impressions:
                # Nimm Durchschnitt von lower/upper bound
                lower = int(impressions.get("lower_bound", "0").replace(",", ""))
                upper = int(impressions.get("upper_bound", "0").replace(",", ""))
                total_impressions += (lower + upper) / 2
        
        # Grosse Schätzung: €0.50-2.00 CPM (Cost per Mille)
        estimated_spend = int(total_impressions * random.uniform(0.0005, 0.002))
        
        return {
            "advertising_status": "active_advertiser" if active_ads > 0 else "inactive_advertiser",
            "total_ads": total_ads,
            "active_ads": active_ads,
            "platform_distribution": platform_distribution,
            "primary_demographics": {
                "age_groups": list(set(age_groups)),
                "gender_targeting": list(set(genders))
            },
            "estimated_monthly_spend": f"€{estimated_spend:,}",
            "common_themes": common_words,
            "campaign_sophistication": self._assess_sophistication(ads_data),
            "performance_summary": f"Running {active_ads} active campaigns with estimated €{estimated_spend:,} monthly spend"
        }

    def _extract_common_themes(self, creative_texts: List[str]) -> List[str]:
        """Extrahiert häufige Themen aus Ad-Texten"""
        common_marketing_words = [
            "kostenlos", "free", "jetzt", "limited", "time", "offer", "neu", "new",
            "professional", "expert", "trusted", "proven", "guaranteed", "premium",
            "exclusive", "discover", "transform", "boost", "improve", "save"
        ]
        
        all_text = " ".join(creative_texts).lower()
        found_themes = [word for word in common_marketing_words if word in all_text]
        return found_themes[:5]  # Top 5 Themen

    def _assess_sophistication(self, ads_data: List[Dict[str, Any]]) -> str:
        """Bewertet Sophistication der Ad-Kampagnen"""
        if len(ads_data) >= 10:
            return "high"
        elif len(ads_data) >= 5:
            return "medium"
        elif len(ads_data) >= 2:
            return "low"
        else:
            return "basic"


# Convenience Functions für Integration
async def get_company_ad_intelligence(company_url: str, 
                                    company_name: str = None,
                                    client: MetaAdLibraryMockClient = None) -> Dict[str, Any]:
    """
    Haupt-Funktion für Company Ad Intelligence
    
    Args:
        company_url: URL der Company (für Industry Detection)
        company_name: Name für Ad Search (optional)
        client: Mock Client Instance (optional)
        
    Returns:
        Vollständige Ad Intelligence Analyse
    """
    if client is None:
        client = MetaAdLibraryMockClient()
    
    if company_name is None:
        # Extrahiere Company Name aus URL
        company_name = company_url.replace("https://", "").replace("http://", "").split(".")[0]
    
    # Suche nach Ads
    ads_response = await client.search_ads(
        search_terms=company_name,
        ad_reached_countries=["DE", "AT", "CH"],
        limit=50
    )
    
    # Performance Analysis
    performance_data = client.analyze_ad_performance(ads_response["data"])
    
    # Kombiniere alle Daten
    return {
        "raw_ads_data": ads_response,
        "performance_analysis": performance_data,
        "company_url": company_url,
        "search_terms": company_name,
        "analysis_timestamp": datetime.now().isoformat()
    }


# Test-Funktion für Entwicklung
async def test_mock_client():
    """Test-Funktion für Mock Client"""
    client = MetaAdLibraryMockClient()
    
    test_companies = [
        "https://palestra-fitness.de",
        "https://shopify.com", 
        "https://example-software.com"
    ]
    
    for company_url in test_companies:
        print(f"\n🧪 Testing: {company_url}")
        intelligence = await get_company_ad_intelligence(company_url)
        
        print(f"📊 Status: {intelligence['performance_analysis']['advertising_status']}")
        print(f"📈 Active Ads: {intelligence['performance_analysis'].get('active_ads', 0)}")
        print(f"💰 Est. Spend: {intelligence['performance_analysis'].get('estimated_monthly_spend', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_mock_client())