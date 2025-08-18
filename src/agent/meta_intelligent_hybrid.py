# src/agent/meta_intelligent_hybrid.py - Fixed Version

import asyncio
import aiohttp
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
logger = logging.getLogger(__name__)

class IntelligentMetaHybrid:
    """
    Intelligent Meta Analysis System:
    1. Smart search for real Meta ads
    2. Use real API data if relevant ads found
    3. Clear "no Meta ads" status if no relevant ads
    4. No fake mock data - professional transparency
    """
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv("META_API_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v18.0/ads_archive"
        self.api_available = None
        
    def extract_company_search_terms(self, company_url: str) -> dict:
        """Extract intelligent search terms from company URL."""
        
        parsed = urlparse(company_url)
        domain = parsed.netloc.lower().replace('www.', '')
        base_name = domain.split('.')[0]
        
        # Generate search variations
        variations = [
            base_name,
            base_name.replace('-', ' '),
            base_name.replace('-', ''),
            base_name.title(),
            base_name.replace('-', ' ').title(),
        ]
        
        # Remove duplicates and short terms
        unique_variations = []
        for var in variations:
            if var not in unique_variations and len(var) > 2:
                unique_variations.append(var)
        
        return {
            "domain": domain,
            "base_name": base_name,
            "search_terms": unique_variations[:4],  # Limit API calls
            "expected_page_names": [
                base_name.replace('-', ' ').title(),
                base_name.title(),
                base_name.upper(),
                base_name.replace('-', ' ').upper(),
            ]
        }
    
    async def check_api_availability(self) -> tuple[bool, str]:
        """Check if Meta Ad Library API is available."""
        
        if not self.access_token:
            return False, "No Meta API access token available"
        
        try:
            # Quick test with a known advertiser
            params = {
                "access_token": self.access_token,
                "search_terms": "BMW",
                "ad_reached_countries": '["DE"]',
                "limit": 1,
                "fields": "id"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        self.api_available = True
                        return True, "Meta Ad Library API available"
                    else:
                        data = await response.json()
                        error_info = data.get("error", {})
                        self.api_available = False
                        return False, f"API Error: {error_info.get('message', 'Unknown error')}"
                        
        except Exception as e:
            self.api_available = False
            return False, f"API connection failed: {str(e)}"
    
    async def search_company_ads(self, company_url: str) -> Dict[str, Any]:
        """Search for company ads with intelligent filtering."""
        
        # Check API availability first
        if self.api_available is None:
            api_ok, api_status = await self.check_api_availability()
            if not api_ok:
                return {
                    "success": False,
                    "status": "api_unavailable",
                    "message": api_status,
                    "company_url": company_url,
                    "meta_ads_available": False
                }
        
        company_info = self.extract_company_search_terms(company_url)
        company_name = company_info["base_name"].replace('-', ' ').title()
        
        print(f"🔍 Intelligent Meta search for: {company_name}")
        print(f"   Search terms: {company_info['search_terms']}")
        
        all_relevant_ads = []
        
        # Search with each term
        for search_term in company_info['search_terms']:
            print(f"   📊 Searching: '{search_term}'")
            
            raw_ads = await self._api_search(search_term)
            relevant_ads = self._filter_for_relevance(raw_ads, company_info)
            
            print(f"      Raw: {len(raw_ads)}, Relevant: {len(relevant_ads)}")
            
            all_relevant_ads.extend(relevant_ads)
        
        # Deduplicate by ad ID
        unique_ads = {}
        for ad in all_relevant_ads:
            ad_id = ad.get('id')
            if ad_id and ad_id not in unique_ads:
                unique_ads[ad_id] = ad
        
        final_ads = list(unique_ads.values())
        
        if final_ads:
            print(f"   ✅ Found {len(final_ads)} relevant Meta ads")
            
            # Analyze the real ads
            analysis = self._analyze_real_ads(final_ads, company_name)
            
            return {
                "success": True,
                "status": "real_ads_found",
                "company_url": company_url,
                "company_name": company_name,
                "meta_ads_available": True,
                "total_relevant_ads": len(final_ads),
                "analysis": analysis,
                "sample_ads": final_ads[:3],
                "data_source": "real_meta_api",
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"   📝 No relevant Meta ads found for {company_name}")
            
            return {
                "success": True,
                "status": "no_relevant_ads",
                "company_url": company_url,
                "company_name": company_name,
                "meta_ads_available": False,
                "message": f"{company_name} does not appear to run Meta advertising campaigns",
                "recommendation": "Consider other marketing intelligence sources or focus on website-based insights",
                "data_source": "real_meta_api_search",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _api_search(self, search_term: str) -> List[Dict]:
        """Perform Meta API search."""
        
        params = {
            "access_token": self.access_token,
            "search_terms": search_term,
            "ad_reached_countries": '["DE"]',
            "ad_active_status": "ALL",
            "limit": 50,
            "fields": "id,page_name,ad_delivery_start_time,ad_delivery_stop_time,publisher_platforms,impressions,ad_creative_bodies,ad_creative_link_titles,page_id"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    else:
                        return []
            except Exception:
                return []
    
    def _filter_for_relevance(self, raw_ads: List[Dict], company_info: dict) -> List[Dict]:
        """Filter ads for actual relevance to the company."""
        
        relevant_ads = []
        base_name = company_info['base_name'].lower()
        expected_names = [name.lower() for name in company_info['expected_page_names']]
        
        # Known generic/irrelevant advertisers to exclude
        generic_excludes = [
            'muscle booster', 'fitness pal', 'freeletics', 'nike training',
            'adidas training', '7 minute workout', 'workout app', 'fitness app',
            'calorie counter', 'weight loss', 'diet app', 'nutrition app'
        ]
        
        for ad in raw_ads:
            page_name = ad.get('page_name', '').lower()
            
            # Calculate relevance score
            relevance_score = 0
            
            # High relevance: Exact or close page name match
            if base_name in page_name or any(name in page_name for name in expected_names):
                relevance_score += 15
            
            # Medium relevance: Page name contains base company name
            base_words = base_name.split('-')
            if len(base_words) > 1 and all(word in page_name for word in base_words):
                relevance_score += 10
            
            # Exclude known generic fitness apps
            is_generic = any(generic in page_name for generic in generic_excludes)
            if is_generic:
                relevance_score -= 20
            
            # Exclude non-German language content
            creatives = ad.get('ad_creative_bodies', [])
            if creatives:
                text = ' '.join(creatives).lower()
                # Spanish/other language indicators
                foreign_indicators = ['encantan', 'comenzar', 'ejercicios', 'oficina']
                if any(indicator in text for indicator in foreign_indicators):
                    relevance_score -= 15
            
            # Only include ads with positive relevance
            if relevance_score > 5:
                ad['relevance_score'] = relevance_score
                relevant_ads.append(ad)
        
        # Sort by relevance (highest first)
        relevant_ads.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_ads
    
    def _analyze_real_ads(self, ads: List[Dict], company_name: str) -> Dict[str, Any]:
        """Analyze real Meta ads data."""
        
        total_ads = len(ads)
        active_ads = len([ad for ad in ads if not ad.get('ad_delivery_stop_time')])
        
        # Platform analysis
        all_platforms = set()
        for ad in ads:
            platforms = ad.get('publisher_platforms', [])
            all_platforms.update(platforms)
        
        # Creative analysis
        all_creatives = []
        for ad in ads:
            creatives = ad.get('ad_creative_bodies', [])
            all_creatives.extend(creatives)
        
        # Impression analysis for spend estimation
        total_impressions = 0
        impression_data_available = False
        
        for ad in ads:
            impressions = ad.get('impressions', {})
            if impressions and 'lower_bound' in impressions:
                impression_data_available = True
                try:
                    lower = int(str(impressions['lower_bound']).replace(',', ''))
                    upper = int(str(impressions.get('upper_bound', lower)).replace(',', ''))
                    avg_impressions = (lower + upper) / 2
                    total_impressions += avg_impressions
                except (ValueError, TypeError):
                    pass
        
        # Estimate monthly spend (rough calculation)
        estimated_monthly_spend = 0
        if total_impressions > 0:
            # Rough estimate: €1-3 CPM for German market
            estimated_monthly_spend = int((total_impressions / 1000) * 1.5)
        
        # Campaign sophistication assessment
        if total_ads >= 20:
            sophistication = "high"
        elif total_ads >= 10:
            sophistication = "medium"
        elif total_ads >= 5:
            sophistication = "moderate"
        else:
            sophistication = "basic"
        
        return {
            "advertising_status": "active_advertiser" if active_ads > 0 else "inactive_advertiser",
            "total_ads": total_ads,
            "active_ads": active_ads,
            "platforms": list(all_platforms),
            "estimated_monthly_spend_eur": estimated_monthly_spend if estimated_monthly_spend > 0 else "Unable to estimate",
            "campaign_sophistication": sophistication,
            "impression_data_available": impression_data_available,
            "sample_creatives": all_creatives[:3],
            "analysis_confidence": "high" if total_ads >= 5 else "medium",
            "last_ad_activity": self._get_latest_activity(ads),
            "platform_distribution": self._analyze_platform_distribution(ads)
        }
    
    def _get_latest_activity(self, ads: List[Dict]) -> str:
        """Get the most recent ad activity."""
        latest_date = None
        
        for ad in ads:
            start_time = ad.get('ad_delivery_start_time')
            if start_time:
                try:
                    ad_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if latest_date is None or ad_date > latest_date:
                        latest_date = ad_date
                except:
                    pass
        
        if latest_date:
            return latest_date.strftime('%Y-%m-%d')
        else:
            return "Unknown"
    
    def _analyze_platform_distribution(self, ads: List[Dict]) -> Dict[str, int]:
        """Analyze which platforms are used most."""
        platform_counts = {}
        
        for ad in ads:
            platforms = ad.get('publisher_platforms', [])
            for platform in platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return platform_counts

# ⭐ MAIN INTEGRATION FUNCTION (this is what graph.py imports)
async def get_intelligent_meta_analysis(company_url: str) -> Dict[str, Any]:
    """
    Main function for intelligent Meta analysis.
    Returns either real Meta data or clear "no ads" status.
    """
    
    analyzer = IntelligentMetaHybrid()
    
    try:
        result = await analyzer.search_company_ads(company_url)
        
        # Add metadata for the main system
        result["intelligent_analysis"] = True
        result["fallback_to_mock"] = False  # We don't use mock data anymore
        
        return result
        
    except Exception as e:
        logger.error(f"Intelligent Meta analysis failed for {company_url}: {str(e)}")
        
        return {
            "success": False,
            "status": "analysis_failed",
            "company_url": company_url,
            "meta_ads_available": False,
            "error": str(e),
            "message": "Meta advertising analysis temporarily unavailable",
            "intelligent_analysis": True,
            "fallback_to_mock": False,
            "timestamp": datetime.now().isoformat()
        }

# Test function
async def test_intelligent_system():
    """Test the intelligent system with various companies."""
    
    print("🧠 INTELLIGENT META HYBRID SYSTEM TEST")
    print("=" * 60)
    
    test_companies = [
        "https://palestra-fitness.de",  # Likely no ads
        "https://mcfit.com",            # Definitely has ads
        "https://example-local-shop.de" # Likely no ads
    ]
    
    for company_url in test_companies:
        print(f"\n🏢 Testing: {company_url}")
        print("-" * 40)
        
        result = await get_intelligent_meta_analysis(company_url)
        
        print(f"✅ Success: {result['success']}")
        print(f"📊 Status: {result['status']}")
        print(f"📱 Meta Ads Available: {result['meta_ads_available']}")
        
        if result['meta_ads_available']:
            analysis = result.get('analysis', {})
            print(f"🎯 Campaign Sophistication: {analysis.get('campaign_sophistication', 'N/A')}")
            print(f"💰 Est. Monthly Spend: €{analysis.get('estimated_monthly_spend_eur', 'N/A')}")
            print(f"📈 Total Ads: {analysis.get('total_ads', 0)}")
            print(f"🔧 Data Source: {result.get('data_source', 'N/A')}")
        else:
            print(f"📝 Message: {result.get('message', 'No details available')}")
            print(f"💡 Recommendation: {result.get('recommendation', 'No recommendation')}")

if __name__ == "__main__":
    asyncio.run(test_intelligent_system())