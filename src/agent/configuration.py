# src/agent/configuration.py - Enhanced with Meta API Configuration (No Mock)

import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the enhanced chatbot with Meta Ad Intelligence."""

    # Core search settings
    max_search_queries: int = 4  # Max search queries per company
    max_search_results: int = 3  # Max search results per query
    max_reflection_steps: int = 0  # Max reflection steps
    include_search_results: bool = False  # Whether to include search results in the output
    
    # Meta Ad Intelligence Settings
    enable_meta_ad_analysis: bool = True  # Whether to perform Meta ad analysis
    meta_api_access_token: Optional[str] = None  # Meta API access token
    meta_api_version: str = "v18.0"  # Meta API version
    meta_ad_limit: int = 50  # Max ads to analyze per company
    meta_countries: list[str] = None  # Countries to search (default: ["DE", "AT", "CH"])
    
    # Rate limiting for Meta API
    meta_api_rate_limit: int = 200  # Requests per hour
    meta_api_retry_attempts: int = 3  # Number of retry attempts on API errors
    
    # Analysis depth settings
    meta_ad_analysis_depth: str = "standard"  # "basic", "standard", "comprehensive"
    include_competitor_analysis: bool = True  # Whether to include competitor analysis
    include_creative_analysis: bool = True  # Whether to analyze ad creatives
    
    # Output formatting
    include_raw_ad_data: bool = False  # Whether to include raw ad data in output
    meta_analysis_language: str = "de"  # Language for Meta analysis output

    def __post_init__(self):
        """Post-initialization to set defaults and validate settings."""
        # Set default countries if not provided
        if self.meta_countries is None:
            self.meta_countries = ["DE", "AT", "CH"]
            
        # Validate analysis depth
        valid_depths = ["basic", "standard", "comprehensive"]
        if self.meta_ad_analysis_depth not in valid_depths:
            self.meta_ad_analysis_depth = "standard"

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        
        # Get values from environment or config
        values: dict[str, Any] = {}
        for f in fields(cls):
            if f.init:
                env_key = f.name.upper()
                config_value = configurable.get(f.name)
                env_value = os.environ.get(env_key)
                
                # Special handling for different field types
                if f.name == "meta_countries" and env_value:
                    # Parse comma-separated country codes from environment
                    values[f.name] = [c.strip().upper() for c in env_value.split(",")]
                elif f.name.startswith("enable_") or f.name.startswith("include_"):
                    # Boolean fields
                    if config_value is not None:
                        values[f.name] = config_value
                    elif env_value is not None:
                        values[f.name] = env_value.lower() in ("true", "1", "yes", "on")
                elif f.name.endswith("_limit") or f.name.endswith("_attempts") or f.name == "max_search_queries":
                    # Integer fields
                    if config_value is not None:
                        values[f.name] = int(config_value)
                    elif env_value is not None:
                        values[f.name] = int(env_value)
                else:
                    # String and other fields
                    if config_value is not None:
                        values[f.name] = config_value
                    elif env_value is not None:
                        values[f.name] = env_value
        
        return cls(**{k: v for k, v in values.items() if v is not None})

    def get_meta_api_config(self) -> dict[str, Any]:
        """Get Meta API configuration as a dictionary."""
        return {
            "access_token": self.meta_api_access_token or os.getenv("META_API_ACCESS_TOKEN"),
            "api_version": self.meta_api_version,
            "ad_limit": self.meta_ad_limit,
            "countries": self.meta_countries,
            "rate_limit": self.meta_api_rate_limit,
            "retry_attempts": self.meta_api_retry_attempts,
        }

    def should_analyze_meta_ads(self) -> bool:
        """Check if Meta ad analysis should be performed."""
        if not self.enable_meta_ad_analysis:
            return False
            
        # Check if token is available
        token = self.meta_api_access_token or os.getenv("META_API_ACCESS_TOKEN")
        return token is not None

    def get_analysis_settings(self) -> dict[str, Any]:
        """Get analysis settings for the Meta ad analyzer."""
        return {
            "depth": self.meta_ad_analysis_depth,
            "include_competitors": self.include_competitor_analysis,
            "include_creatives": self.include_creative_analysis,
            "include_raw_data": self.include_raw_ad_data,
            "language": self.meta_analysis_language,
        }


# Environment Configuration Helper
class EnvironmentConfig:
    """Helper class for managing environment configuration."""
    
    @staticmethod
    def setup_development_env():
        """Setup development environment."""
        os.environ.update({
            "ENABLE_META_AD_ANALYSIS": "true",
            "META_AD_ANALYSIS_DEPTH": "comprehensive",
            "META_COUNTRIES": "DE,AT,CH",
            "INCLUDE_COMPETITOR_ANALYSIS": "true",
            "INCLUDE_CREATIVE_ANALYSIS": "true",
        })
    
    @staticmethod
    def setup_production_env(meta_access_token: str):
        """Setup production environment with real Meta API."""
        os.environ.update({
            "META_API_ACCESS_TOKEN": meta_access_token,
            "ENABLE_META_AD_ANALYSIS": "true",
            "META_AD_ANALYSIS_DEPTH": "standard",
            "META_COUNTRIES": "DE,AT,CH,US,GB",
            "META_API_RATE_LIMIT": "200",
            "INCLUDE_RAW_AD_DATA": "false",
        })
    
    @staticmethod
    def validate_meta_api_setup() -> tuple[bool, str]:
        """Validate Meta API setup and return status."""
        config = Configuration.from_runnable_config()
        
        if not config.enable_meta_ad_analysis:
            return False, "Meta ad analysis is disabled in configuration"
        
        token = config.meta_api_access_token or os.getenv("META_API_ACCESS_TOKEN")
        if not token:
            return False, "Meta API access token not found. Set META_API_ACCESS_TOKEN environment variable."
        
        return True, f"Meta API configured for production (version {config.meta_api_version})"


# Test configuration validation
if __name__ == "__main__":
    # Test configuration loading
    print("🔧 Testing Configuration...")
    
    # Test development setup
    EnvironmentConfig.setup_development_env()
    dev_config = Configuration.from_runnable_config()
    print(f"📊 Development Config:")
    print(f"   Meta Ad Analysis: {dev_config.enable_meta_ad_analysis}")
    print(f"   Analysis Depth: {dev_config.meta_ad_analysis_depth}")
    print(f"   Countries: {dev_config.meta_countries}")
    
    # Test validation
    is_valid, message = EnvironmentConfig.validate_meta_api_setup()
    print(f"✅ Validation: {message}")
    
    # Test Meta API config
    meta_config = dev_config.get_meta_api_config()
    print(f"🎯 Meta API Config: {meta_config}")
    
    print(f"\n🔍 Ready for Meta API integration!")
    print(f"📖 Next steps:")
    print(f"   1. Set META_API_ACCESS_TOKEN environment variable")
    print(f"   2. Test with real Meta API calls")
    print(f"   3. Verify ad data extraction works")