# src/agent/state.py - Erweitert mit Meta Ad Intelligence

from dataclasses import dataclass, field
from typing import Any, Optional, Annotated
import operator

# Das erweiterte Schema mit Meta Ad Intelligence
EXTENDED_EXTRACTION_SCHEMA = {
    "title": "company_marketing_analysis_with_ad_intelligence",
    "description": "Comprehensive marketing profile analysis including Meta advertising intelligence",
    "type": "object",
    "properties": {
        "company_name": {"type": "string", "description": "Name of the company to research."},
        "brand_mission_vision": {"type": "string", "description": "Company's overarching mission statement and vision."},
        "unique_selling_proposition": {"type": "string", "description": "What distinctly sets this company apart from competitors."},
        
        "target_audience_personas": {
            "type": "array",
            "description": "Key audience segments/personas the company targets",
            "items": {
                "type": "object",
                "properties": {
                    "persona_name": {"type": "string", "description": "Name or label of the persona (e.g., 'Tech-savvy freelancer')."},
                    "demographics": {"type": "string", "description": "General demographic info (age range, location, etc.)."},
                    "pain_points": {"type": "array", "items": {"type": "string"}, "description": "Common challenges or problems faced by this persona."},
                    "motivations": {"type": "array", "items": {"type": "string"}, "description": "Key motivations or drivers leading this persona to seek solutions."}
                }
            }
        },
        
        "online_marketing_presence": {
            "type": "object",
            "description": "Assessment of the company's digital marketing presence and activities",
            "properties": {
                "social_media_channels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string", "description": "Social media platform name (e.g., LinkedIn, Twitter, Instagram)"},
                            "follower_count": {"type": "string", "description": "Approximate follower count if visible"},
                            "activity_level": {"type": "string", "description": "How active they are (daily, weekly, monthly, inactive)"},
                            "content_strategy": {"type": "string", "description": "Brief description of their content approach"}
                        }
                    },
                    "description": "List of social media channels and their usage"
                },
                "digital_advertising": {"type": "array", "items": {"type": "string"}, "description": "Evidence of digital advertising (Google Ads, social ads, display ads, etc.)"},
                "content_marketing": {
                    "type": "object",
                    "properties": {
                        "blog_presence": {"type": "boolean", "description": "Whether they maintain a blog"},
                        "content_frequency": {"type": "string", "description": "How often they publish content"},
                        "content_types": {"type": "array", "items": {"type": "string"}, "description": "Types of content they create (articles, videos, podcasts, etc.)"}
                    }
                },
                "email_marketing": {"type": "string", "description": "Evidence of email marketing efforts (newsletter signup, lead magnets, etc.)"}
            }
        },

        # ⭐ META AD INTELLIGENCE SECTION
        "meta_advertising_intelligence": {
            "type": "object",
            "description": "Comprehensive analysis of Meta (Facebook/Instagram) advertising activities",
            "properties": {
                "advertising_status": {
                    "type": "string", 
                    "enum": ["active_advertiser", "inactive_advertiser", "no_ads_found", "analysis_failed"],
                    "description": "Current advertising status on Meta platforms"
                },
                "active_campaigns": {
                    "type": "object",
                    "description": "Analysis of currently running Meta ad campaigns",
                    "properties": {
                        "total_active_ads": {"type": "integer", "description": "Number of currently active advertisements"},
                        "campaign_duration_analysis": {"type": "string", "description": "How long campaigns typically run"},
                        "advertising_consistency": {"type": "string", "description": "Consistency of advertising efforts over time"},
                        "seasonal_patterns": {"type": "string", "description": "Observable seasonal advertising patterns"}
                    }
                },
                "ad_creative_analysis": {
                    "type": "object",
                    "description": "Analysis of advertising creative strategies and content",
                    "properties": {
                        "creative_formats": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of ad formats used (image, video, carousel, collection, etc.)"
                        },
                        "messaging_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Common themes and messages in advertising content"
                        },
                        "visual_style": {"type": "string", "description": "Description of visual branding and style in ads"},
                        "call_to_action_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Common call-to-action buttons and phrases used"
                        },
                        "landing_page_strategies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Landing page URLs and conversion strategies observed"
                        }
                    }
                },
                "targeting_insights": {
                    "type": "object",
                    "description": "Insights into audience targeting and demographics",
                    "properties": {
                        "geographic_targeting": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Countries/regions where ads are shown"
                        },
                        "demographic_targeting": {
                            "type": "object",
                            "properties": {
                                "age_ranges": {"type": "array", "items": {"type": "string"}, "description": "Age ranges targeted in advertisements"},
                                "gender_targeting": {"type": "string", "description": "Gender targeting strategy if observable"},
                                "platform_distribution": {"type": "string", "description": "Distribution across Facebook, Instagram, Messenger, etc."}
                            }
                        },
                        "audience_size_estimates": {"type": "string", "description": "Estimated reach and audience sizes"}
                    }
                },
                "advertising_budget_analysis": {
                    "type": "object",
                    "description": "Analysis of advertising investment and budget patterns",
                    "properties": {
                        "spend_estimates": {"type": "string", "description": "Estimated advertising spend ranges"},
                        "budget_allocation": {"type": "string", "description": "How budget appears to be allocated across campaigns"},
                        "advertising_intensity": {"type": "string", "enum": ["low", "medium", "high", "very_high"], "description": "Overall advertising intensity level"},
                        "competitor_spend_comparison": {"type": "string", "description": "How their spend compares to industry competitors"}
                    }
                },
                "competitive_advertising_analysis": {
                    "type": "object",
                    "description": "Analysis of competitive landscape in Meta advertising",
                    "properties": {
                        "direct_competitors_advertising": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "competitor_name": {"type": "string", "description": "Name of competing advertiser"},
                                    "advertising_overlap": {"type": "string", "description": "How much their advertising overlaps"},
                                    "competitive_advantages": {"type": "string", "description": "Competitive advantages observed in their ads"},
                                    "missed_opportunities": {"type": "string", "description": "Opportunities the company might be missing compared to this competitor"}
                                }
                            },
                            "description": "Analysis of direct competitors' Meta advertising strategies"
                        },
                        "market_share_insights": {"type": "string", "description": "Insights into market share and presence in Meta advertising"},
                        "advertising_gaps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Gaps in advertising strategy compared to competitors"
                        }
                    }
                },
                "advertising_performance_indicators": {
                    "type": "object",
                    "description": "Indicators of advertising performance and optimization",
                    "properties": {
                        "ad_rotation_frequency": {"type": "string", "description": "How frequently they rotate or update ad creatives"},
                        "ab_testing_evidence": {"type": "string", "description": "Evidence of A/B testing in ad campaigns"},
                        "optimization_sophistication": {"type": "string", "description": "Level of campaign optimization sophistication"},
                        "campaign_objectives_analysis": {"type": "string", "description": "Primary campaign objectives (awareness, traffic, conversions, etc.)"}
                    }
                },
                "advertising_opportunities": {
                    "type": "object",
                    "description": "Identified opportunities for advertising improvement",
                    "properties": {
                        "untapped_markets": {"type": "array", "items": {"type": "string"}, "description": "Geographic or demographic markets not being targeted"},
                        "creative_opportunities": {"type": "array", "items": {"type": "string"}, "description": "Opportunities for creative improvement or new formats"},
                        "messaging_gaps": {"type": "array", "items": {"type": "string"}, "description": "Messaging gaps compared to competitors"},
                        "budget_optimization_potential": {"type": "string", "description": "Potential for budget optimization based on competitor analysis"},
                        "seasonal_opportunities": {"type": "array", "items": {"type": "string"}, "description": "Seasonal advertising opportunities not being leveraged"}
                    }
                }
            }
        },

        # Bestehende Sections bleiben unverändert
        "seo_performance": {
            "type": "object",
            "description": "Assessment of the company's search engine optimization and online visibility",
            "properties": {
                "website_structure": {
                    "type": "object",
                    "properties": {
                        "url_structure": {"type": "string", "description": "Assessment of URL structure quality (clean, descriptive, etc.)"},
                        "meta_information": {"type": "string", "description": "Quality of meta titles and descriptions observed"},
                        "internal_linking": {"type": "string", "description": "Assessment of internal linking structure"}
                    }
                },
                "content_optimization": {
                    "type": "object",
                    "properties": {
                        "keyword_usage": {"type": "string", "description": "Evidence of strategic keyword usage in content"},
                        "content_depth": {"type": "string", "description": "Assessment of content depth and informativeness"},
                        "content_freshness": {"type": "string", "description": "How frequently content appears to be updated"}
                    }
                },
                "technical_seo": {"type": "array", "items": {"type": "string"}, "description": "Observable technical SEO elements (site speed, mobile optimization, schema markup, etc.)"},
                "local_seo": {"type": "string", "description": "Evidence of local SEO optimization if applicable (Google My Business, local keywords, etc.)"}
            }
        },

        "website_user_experience": {
            "type": "object",
            "description": "Assessment of the website's user experience and usability",
            "properties": {
                "navigation_design": {
                    "type": "object",
                    "properties": {
                        "menu_structure": {"type": "string", "description": "Assessment of main navigation clarity and organization"},
                        "search_functionality": {"type": "string", "description": "Quality and availability of site search features"},
                        "breadcrumbs": {"type": "boolean", "description": "Whether breadcrumb navigation is present"}
                    }
                },
                "page_performance": {
                    "type": "object",
                    "properties": {
                        "loading_speed": {"type": "string", "description": "Subjective assessment of page loading speed"},
                        "mobile_responsiveness": {"type": "string", "description": "How well the site adapts to mobile devices"},
                        "cross_browser_compatibility": {"type": "string", "description": "Evidence of cross-browser testing and compatibility"}
                    }
                },
                "conversion_optimization": {
                    "type": "object",
                    "properties": {
                        "call_to_action": {"type": "array", "items": {"type": "string"}, "description": "Quality and placement of call-to-action elements"},
                        "lead_capture": {"type": "string", "description": "Methods used for lead generation (forms, popups, etc.)"},
                        "trust_signals": {"type": "array", "items": {"type": "string"}, "description": "Trust-building elements (testimonials, certifications, security badges, etc.)"}
                    }
                },
                "accessibility": {"type": "string", "description": "Assessment of website accessibility features and compliance"},
                "overall_ux_rating": {"type": "string", "description": "Overall user experience rating (excellent, good, average, poor) with brief justification"}
            }
        },

        "marketing_channels": {
            "type": "array",
            "description": "Channels used for marketing outreach (online/offline).",
            "items": {
                "type": "object",
                "properties": {
                    "channel_name": {"type": "string", "description": "Name of the channel (e.g., Facebook, Google Ads, Trade Shows)."},
                    "campaign_types": {"type": "array", "items": {"type": "string"}, "description": "Specific campaigns or strategies used on this channel (e.g., social ads, influencer partnerships)."},
                    "effectiveness_rating": {"type": "string", "description": "Qualitative or quantitative assessment of how effective the channel has been (e.g., high, medium, low)."}
                }
            }
        },

        "competitive_landscape": {
            "type": "array",
            "description": "Key competitors and brief analysis of their positioning.",
            "items": {
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string", "description": "Name of the competitor."},
                    "strengths": {"type": "array", "items": {"type": "string"}, "description": "Competitor's strengths in terms of branding, marketing, product differentiation, etc."},
                    "weaknesses": {"type": "array", "items": {"type": "string"}, "description": "Competitor's weaknesses or areas where they may fall short."},
                    "marketing_positioning": {"type": "string", "description": "Short summary of how the competitor positions itself in the market."}
                }
            }
        },

        "swot_analysis": {
            "type": "object",
            "description": "High-level SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.",
            "properties": {
                "strengths": {"type": "array", "items": {"type": "string"}, "description": "Internal attributes that are helpful in achieving objectives."},
                "weaknesses": {"type": "array", "items": {"type": "string"}, "description": "Internal attributes that are harmful in achieving objectives."},
                "opportunities": {"type": "array", "items": {"type": "string"}, "description": "External conditions that are helpful in achieving objectives."},
                "threats": {"type": "array", "items": {"type": "string"}, "description": "External conditions that could damage performance."}
            }
        },

        "marketing_goals_and_kpis": {
            "type": "array",
            "description": "List of marketing objectives and their corresponding key performance indicators (KPIs).",
            "items": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "High-level marketing goal (e.g., increase brand awareness)."},
                    "kpi": {"type": "string", "description": "Measure used to track progress towards the goal (e.g., social media reach, leads per month)."}
                }
            }
        },

        "key_brand_messages": {"type": "array", "description": "Core messages and slogans communicated by the brand.", "items": {"type": "string"}},
        "overall_positioning_statement": {"type": "string", "description": "Single, concise statement that describes how the brand is positioned in the market."},
        "brand_reputation_overview": {"type": "string", "description": "General sentiment or perception of the brand in the marketplace (e.g., positive, negative, neutral)."}
    },
    
    # Erweiterte Required Fields mit Meta Ad Intelligence
    "required": [
        "company_name", 
        "unique_selling_proposition", 
        "target_audience_personas", 
        "marketing_channels", 
        "online_marketing_presence", 
        "meta_advertising_intelligence",  # ⭐ NEU
        "seo_performance", 
        "website_user_experience"
    ]
}

@dataclass(kw_only=True)
class InputState:
    """Input state defines the interface between the graph and the user (external API)."""
    urls: list[str]
    extraction_schema: dict[str, Any] = field(default_factory=lambda: EXTENDED_EXTRACTION_SCHEMA)
    user_notes: Optional[str] = field(default=None)
    generate_cold_email: bool = field(default=False)
    email_config: Optional[dict[str, Any]] = field(default=None)

@dataclass(kw_only=True)
class OverallState:
    """Overall state for the entire workflow including Meta ad intelligence."""
    urls: list[str]
    extraction_schema: dict[str, Any] = field(default_factory=lambda: EXTENDED_EXTRACTION_SCHEMA)
    user_notes: str = field(default="")
    completed_notes: Annotated[list, operator.add] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)
    is_satisfactory: dict[str, bool] = field(default_factory=dict)
    reflection_steps_taken: dict[str, int] = field(default_factory=dict)
    generate_cold_email: bool = field(default=False)
    email_config: Optional[dict[str, Any]] = field(default=None)
    generated_emails: dict[str, str] = field(default_factory=dict)
    
    # ⭐ NEU: Meta Ad Intelligence Data
    meta_ad_intelligence: dict[str, dict[str, Any]] = field(default_factory=dict)
    """Meta advertising intelligence data for each company URL"""

@dataclass(kw_only=True)
class OutputState:
    """The response object for the end user including Meta ad intelligence."""
    info: dict[str, dict[str, Any]]
    """A dictionary mapping company URLs to their extracted information"""
    
    generated_emails: dict[str, str] = field(default_factory=dict)
    """Generated cold emails for each company if requested"""
    
    # ⭐ NEU: Meta Ad Intelligence Output
    meta_ad_intelligence: dict[str, dict[str, Any]] = field(default_factory=dict)
    """Meta advertising intelligence analysis for each company"""