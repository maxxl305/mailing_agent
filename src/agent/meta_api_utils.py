# src/agent/meta_api_utils.py - Utilities for Real Meta API Integration

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class MetaAPICredentials:
    """Meta API credentials and configuration."""
    access_token: str
    api_version: str = "v18.0"
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    

class MetaAPIError(Exception):
    """Custom exception for Meta API errors."""
    
    def __init__(self, message: str, error_code: Optional[int] = None, error_type: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.error_type = error_type
        super().__init__(self.message)


class MetaAdLibraryRealClient:
    """
    Real Meta Ad Library API Client.
    This will replace the MockClient once Meta Developer Account is set up.
    """
    
    def __init__(self, credentials: MetaAPICredentials):
        self.credentials = credentials
        self.base_url = f"https://graph.facebook.com/{credentials.api_version}"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting tracking
        self._request_times: List[datetime] = []
        self._rate_limit_per_hour = 150  # Meta's free tier limit
        
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
            wait_time = 3600 / self._rate_limit_per_hour  # Wait time in seconds
            logger.warning(f"Rate limit reached. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        
        self._record_request()
        
        # Add access token to params
        params["access_token"] = self.credentials.access_token
        
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
                        limit: int = 100,
                        fields: List[str] = None) -> Dict[str, Any]:
        """
        Search ads in Meta Ad Library.
        
        Args:
            search_terms: Search query (usually company name)
            ad_reached_countries: List of country codes
            ad_delivery_date_min: Minimum delivery date (YYYY-MM-DD)
            ad_delivery_date_max: Maximum delivery date (YYYY-MM-DD)
            limit: Maximum number of results
            fields: List of fields to retrieve
            
        Returns:
            Dict with ad library search results
        """
        
        if ad_reached_countries is None:
            ad_reached_countries = ["DE"]
        
        if fields is None:
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
    
    async def get_page_info(self, page_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """
        Get information about a Facebook/Instagram page.
        
        Args:
            page_id: Facebook page ID
            fields: List of fields to retrieve
            
        Returns:
            Dict with page information
        """
        
        if fields is None:
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
    
    async def get_ad_insights(self, ad_id: str) -> Dict[str, Any]:
        """
        Get insights for a specific ad (if available).
        Note: This requires special permissions and may not be available for all ads.
        """
        
        params = {
            "fields": "impressions,reach,spend,cpm,cpc,ctr"
        }
        
        return await self._make_request(f"{ad_id}/insights", params)


class MetaAdLibraryFactory:
    """Factory class to create appropriate Meta Ad Library client."""
    
    @staticmethod
    def create_client(use_mock: bool = True, 
                     credentials: Optional[MetaAPICredentials] = None) -> Union['MetaAdLibraryMockClient', 'MetaAdLibraryRealClient']:
        """
        Create appropriate client based on configuration.
        
        Args:
            use_mock: Whether to use mock client
            credentials: Meta API credentials (required for real client)
            
        Returns:
            Client instance (Mock or Real)
        """
        
        if use_mock:
            from .meta_ad_client import MetaAdLibraryMockClient
            return MetaAdLibraryMockClient()
        else:
            if not credentials or not credentials.access_token:
                raise ValueError("Real Meta API client requires valid credentials")
            return MetaAdLibraryRealClient(credentials)


class AdDataProcessor:
    """Utility class for processing and analyzing Meta ad data."""
    
    @staticmethod
    def extract_company_mentions(ad_text: str, company_name: str) -> int:
        """Count mentions of company name in ad text."""
        if not ad_text or not company_name:
            return 0
        return ad_text.lower().count(company_name.lower())
    
    @staticmethod
    def analyze_creative_themes(ads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze common themes in ad creatives."""
        theme_words = {}
        
        for ad in ads:
            # Get all text content from ad
            text_content = []
            text_content.extend(ad.get("ad_creative_bodies", []))
            text_content.extend(ad.get("ad_creative_link_titles", []))
            text_content.extend(ad.get("ad_creative_link_descriptions", []))
            
            # Count words
            for text in text_content:
                if text:
                    words = text.lower().split()
                    for word in words:
                        # Filter meaningful words (length > 3, not common words)
                        if len(word) > 3 and word not in ['with', 'your', 'this', 'that', 'they', 'have', 'will', 'from']:
                            theme_words[word] = theme_words.get(word, 0) + 1
        
        # Return top themes
        return dict(sorted(theme_words.items(), key=lambda x: x[1], reverse=True)[:10])
    
    @staticmethod
    def calculate_campaign_duration_stats(ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate campaign duration statistics."""
        durations = []
        
        for ad in ads:
            start_time = ad.get("ad_delivery_start_time")
            stop_time = ad.get("ad_delivery_stop_time")
            
            if start_time:
                start_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                
                if stop_time:
                    stop_date = datetime.fromisoformat(stop_time.replace('Z', '+00:00'))
                    duration = (stop_date - start_date).days
                    durations.append(duration)
                else:
                    # Still running - calculate current duration
                    current_duration = (datetime.now() - start_date.replace(tzinfo=None)).days
                    durations.append(current_duration)
        
        if not durations:
            return {"average_duration": 0, "min_duration": 0, "max_duration": 0}
        
        return {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_campaigns": len(durations)
        }
    
    @staticmethod
    def estimate_spend_from_impressions(impressions_data: Dict[str, str]) -> Optional[float]:
        """Estimate spend based on impressions data."""
        try:
            lower_bound = int(impressions_data.get("lower_bound", "0").replace(",", ""))
            upper_bound = int(impressions_data.get("upper_bound", "0").replace(",", ""))
            
            # Average impressions
            avg_impressions = (lower_bound + upper_bound) / 2
            
            # Estimate CPM (Cost Per Mille) - industry average €0.50-€2.00
            estimated_cpm = 1.0  # Conservative estimate
            
            # Calculate estimated spend
            estimated_spend = (avg_impressions / 1000) * estimated_cpm
            
            return round(estimated_spend, 2)
            
        except (ValueError, KeyError):
            return None


# ⭐ Integration Helper for switching from Mock to Real API
class MetaAPIIntegration:
    """Helper class to manage the transition from Mock to Real Meta API."""
    
    @staticmethod
    def validate_credentials(access_token: str, app_id: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate Meta API credentials.
        
        Returns:
            Tuple of (is_valid, message)
        """
        
        if not access_token:
            return False, "Access token is required"
        
        if len(access_token) < 50:
            return False, "Access token appears to be invalid (too short)"
        
        # TODO: Add actual API validation call
        # For now, just basic format validation
        return True, "Credentials appear valid (full validation requires API call)"
    
    @staticmethod
    async def test_api_connection(credentials: MetaAPICredentials) -> tuple[bool, str]:
        """
        Test connection to Meta API.
        
        Returns:
            Tuple of (is_connected, message)
        """
        
        try:
            async with MetaAdLibraryRealClient(credentials) as client:
                # Try a simple search to test connection
                result = await client.search_ads("test", ["US"], limit=1)
                return True, f"Successfully connected to Meta API v{credentials.api_version}"
                
        except MetaAPIError as e:
            return False, f"Meta API Error: {e.message}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    @staticmethod
    def migration_checklist() -> List[str]:
        """Return checklist for migrating from Mock to Real API."""
        return [
            "✅ Meta Developer Account created",
            "✅ Business Verification completed", 
            "✅ App created in Meta Developer Console",
            "✅ Ad Library API added to app",
            "✅ Access Token generated",
            "✅ Environment variables configured",
            "⚠️ Rate limits understood and configured",
            "⚠️ Error handling tested",
            "⚠️ Production deployment prepared"
        ]


# Example usage and testing
if __name__ == "__main__":
    print("🔧 Meta API Utils - Integration Helper")
    print("=" * 50)
    
    # Show migration checklist
    print("📋 Migration Checklist:")
    for item in MetaAPIIntegration.migration_checklist():
        print(f"   {item}")
    
    print(f"\n🔍 Ready for production Meta API integration!")
    print(f"📖 Next steps:")
    print(f"   1. Complete Meta Developer setup")
    print(f"   2. Update Configuration.use_mock_meta_api = False")
    print(f"   3. Set META_API_ACCESS_TOKEN environment variable")
    print(f"   4. Test with MetaAPIIntegration.test_api_connection()")