# src/agent/configuration.py - Updated for Real Meta API

import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the enhanced chatbot with Meta Ad Intelligence."""

    # Existing settings
    max_search_queries: int = 4
    max_search_results: int = 3
    max_reflection_steps: int = 0
    include_search_results: bool = False
    
    # ⭐ UPDATED: Meta Ad Intelligence Settings for Production
    enable_meta_ad_analysis: bool = True
    meta_api_access_token: Optional[str] = None
    meta_api_version: str = "v18.0"
    meta_ad_limit: int = 50  # Increased for production
    meta_countries: list[str] = None
    
    # Rate limiting for Meta API (Production settings)
    meta_api_rate_limit: int = 200  # Increased for production
    meta_api_retry_attempts: int = 3
    
    # Analysis depth settings
    meta_ad_analysis_depth: str = "standard"
    include_competitor_analysis: bool = True
    include_creative_analysis: bool = True
    
    # ⭐ UPDATED: Production settings (Mock disabled by default)
    use_mock_meta_api: bool = False  # Changed to False for production
    mock_data_realism: str = "high"
    
    # Output formatting
    include_raw_ad_data: bool = False
    meta_analysis_language: str = "de"

    def __post_init__(self):
        """Post-initialization to set defaults and validate settings."""
        # Set default countries if not provided (Focus on Germany)
        if self.meta_countries is None:
            self.meta_countries = ["DE"]
            
        # Validate analysis depth
        valid_depths = ["basic", "standard", "comprehensive"]
        if self.meta_ad_analysis_depth not in valid_depths:
            self.meta_ad_analysis_depth = "standard"
            
        # Auto-detect production vs development
        if not self.meta_api_access_token:
            token_from_env = os.getenv("META_API_ACCESS_TOKEN")
            if not token_from_env:
                print("⚠️  No Meta API Access Token found - falling back to mock mode")
                self.use_mock_meta_api = True
            else:
                self.meta_api_access_token = token_from_env

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
                    values[f.name] = [c.strip().upper() for c in env_value.split(",")]
                elif f.name.startswith("enable_") or f.name.startswith("include_") or f.name.startswith("use_"):
                    if config_value is not None:
                        values[f.name] = config_value
                    elif env_value is not None:
                        values[f.name] = env_value.lower() in ("true", "1", "yes", "on")
                elif f.name.endswith("_limit") or f.name.endswith("_attempts") or f.name == "max_search_queries":
                    if config_value is not None:
                        values[f.name] = int(config_value)
                    elif env_value is not None:
                        values[f.name] = int(env_value)
                else:
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
            "use_mock": self.use_mock_meta_api,
            "mock_realism": self.mock_data_realism,
        }

    def should_analyze_meta_ads(self) -> bool:
        """Check if Meta ad analysis should be performed."""
        if not self.enable_meta_ad_analysis:
            return False
            
        if self.use_mock_meta_api:
            return True
            
        # For real API, check if token is available
        token = self.meta_api_access_token or os.getenv("META_API_ACCESS_TOKEN")
        return token is not None

    def validate_meta_setup(self) -> tuple[bool, str]:
        """Validate Meta API setup."""
        if not self.enable_meta_ad_analysis:
            return False, "Meta ad analysis is disabled"
        
        if self.use_mock_meta_api:
            return True, "Using Mock API (development mode)"
        
        token = self.meta_api_access_token or os.getenv("META_API_ACCESS_TOKEN")
        if not token:
            return False, "Meta API Access Token missing"
        
        if len(token) < 50:
            return False, "Meta API Access Token appears invalid (too short)"
        
        return True, f"Meta API configured for production (v{self.meta_api_version})"


# ⭐ NEW: Production Environment Helper
class ProductionConfig:
    """Helper for production Meta API setup."""
    
    @staticmethod
    def setup_production_env(meta_access_token: str):
        """Setup production environment with real Meta API."""
        os.environ.update({
            "META_API_ACCESS_TOKEN": meta_access_token,
            "USE_MOCK_META_API": "false",
            "ENABLE_META_AD_ANALYSIS": "true",
            "META_AD_ANALYSIS_DEPTH": "standard",
            "META_COUNTRIES": "DE",
            "META_API_RATE_LIMIT": "200",
            "META_AD_LIMIT": "50",
            "INCLUDE_RAW_AD_DATA": "false",
        })
    
    @staticmethod
    def validate_production_setup() -> tuple[bool, str]:
        """Validate production Meta API setup."""
        config = Configuration.from_runnable_config()
        return config.validate_meta_setup()


# Test configuration
if __name__ == "__main__":
    print("🔧 Testing Production Meta API Configuration...")
    
    config = Configuration.from_runnable_config()
    is_valid, message = config.validate_meta_setup()
    
    print(f"✅ Validation: {message}")
    print(f"🎯 Use Mock: {config.use_mock_meta_api}")
    print(f"📊 Meta Config: {config.get_meta_api_config()}")