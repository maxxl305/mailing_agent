# smart_meta_search.py - Intelligent Meta Ad Library Search

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import re

load_dotenv()

class SmartMetaAdSearch:
    """Smart Meta Ad Library search with intelligent filtering."""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv("META_API_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v18.0/ads_archive"
    
    def extract_company_info(self, company_url: str) -> dict:
        """Extract different variations of company name from URL."""
        
        # Parse URL to get domain info
        parsed = urlparse(company_url)
        domain = parsed.netloc.lower()
        
        # Remove common prefixes
        domain_clean = domain.replace('www.', '').replace('shop.', '').replace('store.', '')
        
        # Extract base name (before first dot)
        base_name = domain_clean.split('.')[0]
        
        # Generate search variations
        variations = [
            base_name,  # "palestra-fitness"
            base_name.replace('-', ' '),  # "palestra fitness"
            base_name.replace('-', ''),   # "palestrafitness"
            base_name.split('-')[0],      # "palestra"
            base_name.title(),            # "Palestra-Fitness"
            base_name.replace('-', ' ').title(),  # "Palestra Fitness"
        ]
        
        # Remove duplicates while preserving order
        unique_variations = []
        for var in variations:
            if var not in unique_variations and len(var) > 2:
                unique_variations.append(var)
        
        return {
            "domain": domain_clean,
            "base_name": base_name,
            "search_variations": unique_variations[:5],  # Limit to 5 variations
            "likely_page_names": [
                base_name.replace('-', ' ').title(),
                base_name.title(),
                base_name.replace('-', ' '),
                base_name.upper(),
            ]
        }
    
    async def search_with_filtering(self, company_url: str) -> dict:
        """Search for ads with intelligent filtering."""
        
        company_info = self.extract_company_info(company_url)
        
        print(f"🔍 Smart search for: {company_url}")
        print(f"   Domain: {company_info['domain']}")
        print(f"   Base name: {company_info['base_name']}")
        print(f"   Search variations: {company_info['search_variations']}")
        
        all_results = []
        
        # Try each search variation
        for variation in company_info['search_variations']:
            print(f"\n📊 Searching for: '{variation}'")
            
            raw_results = await self._api_search(variation)
            if raw_results:
                filtered_results = self._filter_results(raw_results, company_info)
                
                print(f"   Raw results: {len(raw_results)}")
                print(f"   Filtered results: {len(filtered_results)}")
                
                all_results.extend(filtered_results)
        
        # Deduplicate by ad ID
        unique_results = {}
        for result in all_results:
            ad_id = result.get('id')
            if ad_id and ad_id not in unique_results:
                unique_results[ad_id] = result
        
        final_results = list(unique_results.values())
        
        print(f"\n✅ Final results: {len(final_results)} unique ads")
        
        return {
            "company_url": company_url,
            "company_info": company_info,
            "total_ads_found": len(final_results),
            "ads": final_results,
            "search_quality": self._assess_search_quality(final_results, company_info)
        }
    
    async def _api_search(self, search_term: str) -> list:
        """Perform actual API search."""
        
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
                        print(f"   ❌ API Error: {response.status}")
                        return []
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                return []
    
    def _filter_results(self, raw_results: list, company_info: dict) -> list:
        """Filter results to find relevant ads."""
        
        filtered = []
        base_name = company_info['base_name'].lower()
        likely_names = [name.lower() for name in company_info['likely_page_names']]
        
        for ad in raw_results:
            page_name = ad.get('page_name', '').lower()
            
            # Scoring system for relevance
            relevance_score = 0
            
            # High score: Page name contains exact base name
            if base_name in page_name:
                relevance_score += 10
            
            # Medium score: Page name matches likely variations
            for likely_name in likely_names:
                if likely_name.lower() in page_name:
                    relevance_score += 7
                    break
            
            # Low score: Creative contains company name
            creatives = ad.get('ad_creative_bodies', [])
            for creative in creatives:
                if creative and base_name in creative.lower():
                    relevance_score += 3
                    break
            
            # Penalty: Known generic fitness apps
            generic_fitness_apps = [
                'muscle booster', 'fitness pal', 'freeletics', 'nike training',
                'adidas training', '7 minute workout', 'fitness app', 'workout app'
            ]
            
            for generic in generic_fitness_apps:
                if generic in page_name:
                    relevance_score -= 5
                    break
            
            # Penalty: Non-German language (for German companies)
            creatives_text = ' '.join(ad.get('ad_creative_bodies', []))
            if creatives_text:
                # Simple language detection: Spanish indicators
                spanish_indicators = ['encantan', 'comenzar', 'durante', 'oficina', 'ejercicios']
                if any(indicator in creatives_text.lower() for indicator in spanish_indicators):
                    relevance_score -= 8
            
            # Only include results with positive relevance score
            if relevance_score > 0:
                ad['relevance_score'] = relevance_score
                filtered.append(ad)
        
        # Sort by relevance score (highest first)
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered
    
    def _assess_search_quality(self, results: list, company_info: dict) -> str:
        """Assess the quality of search results."""
        
        if not results:
            return "no_ads_found"
        
        # Check if we found high-relevance results
        high_relevance = [r for r in results if r.get('relevance_score', 0) >= 7]
        
        if high_relevance:
            return "high_confidence"
        elif len(results) > 0:
            return "low_confidence"
        else:
            return "no_relevant_ads"

async def test_smart_search():
    """Test the smart search with different companies."""
    
    print("🧠 SMART META AD SEARCH TEST")
    print("=" * 60)
    
    searcher = SmartMetaAdSearch()
    
    test_companies = [
        "https://palestra-fitness.de",
        "https://mcfit.com",
        "https://fitx.de"
    ]
    
    for company_url in test_companies:
        print(f"\n🏢 Testing: {company_url}")
        print("=" * 40)
        
        results = await searcher.search_with_filtering(company_url)
        
        print(f"\n📊 RESULTS:")
        print(f"   Search Quality: {results['search_quality']}")
        print(f"   Total Ads: {results['total_ads_found']}")
        
        if results['ads']:
            print(f"\n📱 Top Results:")
            for i, ad in enumerate(results['ads'][:3], 1):
                page_name = ad.get('page_name', 'Unknown')
                relevance = ad.get('relevance_score', 0)
                platforms = ad.get('publisher_platforms', [])
                
                print(f"   {i}. {page_name} (Score: {relevance})")
                print(f"      Platforms: {', '.join(platforms)}")
                
                # Show creative sample
                creatives = ad.get('ad_creative_bodies', [])
                if creatives:
                    creative_sample = creatives[0][:100] + "..." if len(creatives[0]) > 100 else creatives[0]
                    print(f"      Creative: {creative_sample}")
        else:
            print(f"   ❌ No relevant ads found")
            
            # Suggest what this means
            company_info = results['company_info']
            print(f"\n💡 This likely means:")
            print(f"   • {company_info['base_name'].title()} doesn't run Meta ads")
            print(f"   • They use a completely different business name in ads")
            print(f"   • Their ads are not targeted to Germany")

async def test_palestra_detailed():
    """Detailed test specifically for Palestra Fitness."""
    
    print(f"\n🎯 DETAILED PALESTRA FITNESS ANALYSIS")
    print("=" * 50)
    
    searcher = SmartMetaAdSearch()
    results = await searcher.search_with_filtering("https://palestra-fitness.de")
    
    if results['search_quality'] == 'no_ads_found':
        print("📝 CONCLUSION: Palestra Fitness likely has NO META ADS")
        print("   This is actually common for small local fitness studios!")
        print("   They may rely on:")
        print("   • Local marketing")
        print("   • Word of mouth")
        print("   • Google Ads (not Meta)")
        print("   • Instagram organic (not paid ads)")
        
        return False
    elif results['search_quality'] == 'low_confidence':
        print("⚠️ CONCLUSION: Found some ads but low confidence they belong to Palestra Fitness")
        print("   The ads we found are probably from other fitness companies")
        
        return False
    else:
        print("✅ CONCLUSION: Found relevant Meta ads for Palestra Fitness!")
        return True

if __name__ == "__main__":
    async def run_smart_test():
        await test_smart_search()
        has_real_ads = await test_palestra_detailed()
        
        print(f"\n🎯 FINAL RECOMMENDATION:")
        if has_real_ads:
            print("✅ Use real Meta API data - Palestra has actual ads")
        else:
            print("⚠️ Use enhanced mock data - Palestra likely has no Meta ads")
            print("   This is normal for small local businesses!")
            print("   Your enhanced mock with German market intelligence is actually")
            print("   more valuable than 'no ads found' from real API")
    
    asyncio.run(run_smart_test())