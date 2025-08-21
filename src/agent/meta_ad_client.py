# src/agent/meta_ad_client.py - Echte Meta API Implementation

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

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

class MetaAPIError(Exception):
    """Custom exception for Meta API errors."""
    def __init__(self, message: str, error_code: Optional[int] = None, error_type: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.error_type = error_type
        super().__init__(self.message)

class MetaAdLibraryClient:
    """
    Echter Meta Ad Library API Client.
    """
    
    def __init__(self, access_token: str, api_version: str = "v18.0"):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting tracking
        self._request_times: List[datetime] = []
        self._rate_limit_per_hour = 200  # Meta API Limit
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "CompanyResearcher/1.0",
                "Accept": "application/json",
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Remove requests older than 1 hour
        self._request_times = [t for t in self._request_times if t > one_hour_ago]
        
        # Check if we can make another request
        return len(self._request_times) < self._rate_limit_per_hour
    
    def _record_request(self):
        """Record a new API request timestamp."""
        self._request_times.append(datetime.now())
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, MetaAPIError))
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Meta API with rate limiting and error handling."""
        
        if not self._check_rate_limit():
            wait_time = 3600 / self._rate_limit_per_hour
            logger.warning(f"Rate limit reached. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        
        self._record_request()
        
        # Add access token to params
        params["access_token"] = self.access_token
        
        url = f"{self.base_url}/{endpoint}"
        
        if not self.session:
            raise MetaAPIError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status != 200:
                    error_message = data.get("error", {}).get("message", "Unknown error")
                    error_code = data.get("error", {}).get("code")
                    error_type = data.get("error", {}).get("type")
                    
                    raise MetaAPIError(
                        f"Meta API Error: {error_message}",
                        error_code=error_code,
                        error_type=error_type
                    )
                
                return data
                
        except aiohttp.ClientError as e:
            raise MetaAPIError(f"Network error: {str(e)}")
    
    async def search_ads(self, 
                        search_terms: str,
                        ad_reached_countries: List[str] = None,
                        ad_delivery_date_min: Optional[str] = None,
                        ad_delivery_date_max: Optional[str] = None,
                        limit: int = 100) -> Dict[str, Any]:
        """
        Search ads in Meta Ad Library.
        """
        
        if ad_reached_countries is None:
            ad_reached_countries = ["DE"]
        
        fields = [
            "id",
            "ad_creation_time",
            "ad_creative_bodies",
            "ad_creative_link_captions", 
            "ad_creative_link_descriptions",
            "ad_creative_link_titles",
            "ad_delivery_start_time",
            "ad_delivery_stop_time",
            "ad_snapshot_url",
            "bylines",
            "currency",
            "delivery_by_region",
            "demographic_distribution",
            "impressions",
            "languages",
            "page_id",
            "page_name",
            "publisher_platforms",
            "spend"
        ]
        
        params = {
            "search_terms": search_terms,
            "ad_reached_countries": json.dumps(ad_reached_countries),
            "ad_active_status": "ALL",
            "limit": limit,
            "fields": ",".join(fields)
        }
        
        if ad_delivery_date_min:
            params["ad_delivery_date_min"] = ad_delivery_date_min
        if ad_delivery_date_max:
            params["ad_delivery_date_max"] = ad_delivery_date_max
        
        return await self._make_request("ads_archive", params)
    
    async def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Get information about a Facebook/Instagram page."""
        
        fields = [
            "id",
            "name", 
            "category",
            "verification_status",
            "page_transparency"
        ]
        
        params = {
            "fields": ",".join(fields)
        }
        
        return await self._make_request(page_id, params)

class AdDataProcessor:
    """Utility class for processing and analyzing Meta ad data."""
    
    @staticmethod
    def analyze_ad_performance(ads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze ad performance and extract insights from real Meta API data."""
        if not ads_data:
            return {
                "advertising_status": "no_ads_found",
                "performance_summary": "No active advertising campaigns found",
                "total_ads": 0,
                "active_ads": 0
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
        creative_themes = []
        for ad in ads_data:
            creative_themes.extend(ad.get("ad_creative_bodies", []))
        common_words = AdDataProcessor._extract_common_themes(creative_themes)
        
        # Estimate spend based on impressions
        total_impressions = 0
        spend_data = []
        for ad in ads_data:
            impressions = ad.get("impressions", {})
            if impressions:
                lower = AdDataProcessor._parse_number(impressions.get("lower_bound", "0"))
                upper = AdDataProcessor._parse_number(impressions.get("upper_bound", "0"))
                total_impressions += (lower + upper) / 2
            
            # Check if spend data is available
            if ad.get("spend"):
                spend_data.append(ad["spend"])
        
        # Calculate estimated spend
        if spend_data:
            estimated_spend = sum(AdDataProcessor._parse_number(spend.get("lower_bound", "0")) for spend in spend_data)
        else:
            # Fallback: estimate from impressions (€0.50-2.00 CPM)
            estimated_spend = int(total_impressions * 0.001)  # Conservative estimate
        
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
            "campaign_sophistication": AdDataProcessor._assess_sophistication(ads_data),
            "performance_summary": f"Running {active_ads} active campaigns with estimated €{estimated_spend:,} monthly spend"
        }
    
    @staticmethod
    def _parse_number(value: str) -> int:
        """Parse number from string, removing commas."""
        try:
            return int(str(value).replace(",", ""))
        except (ValueError, AttributeError):
            return 0
    
    @staticmethod
    def _extract_common_themes(creative_texts: List[str]) -> List[str]:
        """Extract common themes from ad texts."""
        common_marketing_words = [
            "kostenlos", "free", "jetzt", "limited", "time", "offer", "neu", "new",
            "professional", "expert", "trusted", "proven", "guaranteed", "premium",
            "exclusive", "discover", "transform", "boost", "improve", "save"
        ]
        
        all_text = " ".join(creative_texts).lower()
        found_themes = [word for word in common_marketing_words if word in all_text]
        return found_themes[:5]
    
    @staticmethod
    def _assess_sophistication(ads_data: List[Dict[str, Any]]) -> str:
        """Assess sophistication of ad campaigns."""
        if len(ads_data) >= 10:
            return "high"
        elif len(ads_data) >= 5:
            return "medium"
        elif len(ads_data) >= 2:
            return "low"
        else:
            return "basic"

# Main function for company ad intelligence
async def get_company_ad_intelligence(company_url: str, 
                                    company_name: str = None,
                                    access_token: str = None) -> Dict[str, Any]:
    """
    Haupt-Funktion für Company Ad Intelligence - Echte Meta API.
    """
    
    # Check if access token is available
    if not access_token:
        access_token = os.getenv("META_API_ACCESS_TOKEN")
        if not access_token:
            logger.warning("No Meta API access token found")
            return {
                "error": "no_token",
                "message": "META_API_ACCESS_TOKEN not found in environment variables",
                "performance_analysis": {
                    "advertising_status": "no_token_available",
                    "performance_summary": "Meta API access token required for advertising analysis"
                }
            }
    
    if company_name is None:
        # Extract company name from URL
        company_name = company_url.replace("https://", "").replace("http://", "").split(".")[0]
    
    try:
        async with MetaAdLibraryClient(access_token) as client:
            # Search for ads
            ads_response = await client.search_ads(
                search_terms=company_name,
                ad_reached_countries=["DE", "AT", "CH"],
                limit=50
            )
            
            # Performance Analysis
            performance_data = AdDataProcessor.analyze_ad_performance(ads_response.get("data", []))
            
            # Combine all data
            return {
                "raw_ads_data": ads_response,
                "performance_analysis": performance_data,
                "company_url": company_url,
                "search_terms": company_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "api_status": "success"
            }
            
    except MetaAPIError as e:
        logger.error(f"Meta API Error for {company_url}: {e.message}")
        return {
            "error": "api_error",
            "message": e.message,
            "error_code": e.error_code,
            "error_type": e.error_type,
            "performance_analysis": {
                "advertising_status": "api_error",
                "performance_summary": f"Meta API Error: {e.message}"
            },
            "company_url": company_url,
            "analysis_timestamp": datetime.now().isoformat(),
            "api_status": "failed"
        }
    
    except Exception as e:
        logger.error(f"Unexpected error for {company_url}: {str(e)}")
        return {
            "error": "unexpected_error", 
            "message": str(e),
            "performance_analysis": {
                "advertising_status": "analysis_failed",
                "performance_summary": f"Analysis failed: {str(e)}"
            },
            "company_url": company_url,
            "analysis_timestamp": datetime.now().isoformat(),
            "api_status": "failed"
        }

# Test function for development
async def test_meta_api():
    """Test function for Meta API connectivity."""
    access_token = os.getenv("META_API_ACCESS_TOKEN")
    if not access_token:
        print("❌ META_API_ACCESS_TOKEN not found in environment")
        return False
    
    try:
        async with MetaAdLibraryClient(access_token) as client:
            # Test with a simple search
            result = await client.search_ads("Nike", ["US"], limit=1)
            print("✅ Meta API connection successful")
            print(f"📊 Found {len(result.get('data', []))} ads")
            return True
    except Exception as e:
        print(f"❌ Meta API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_meta_api())