# state.py - FINALER FIX für OutputState

from dataclasses import dataclass, field
from typing import Any, Optional, Annotated
import operator

# Das gleiche DEFAULT_EXTRACTION_SCHEMA wie vorher... (gekürzt für Übersichtlichkeit)
DEFAULT_EXTRACTION_SCHEMA = {
  "title": "company_marketing_analysis",
  "description": "Comprehensive marketing profile analysis for a company, focusing on brand, audience, messaging, channels, competitive positioning, online presence, SEO and user experience",
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
  "required": ["company_name", "unique_selling_proposition", "target_audience_personas", "marketing_channels", "online_marketing_presence", "seo_performance", "website_user_experience"]
}

@dataclass(kw_only=True)
class InputState:
    """Input state defines the interface between the graph and the user (external API)."""
    urls: list[str]
    extraction_schema: dict[str, Any] = field(default_factory=lambda: DEFAULT_EXTRACTION_SCHEMA)
    user_notes: Optional[str] = field(default=None)
    generate_cold_email: bool = field(default=False)
    email_config: Optional[dict[str, Any]] = field(default=None)

@dataclass(kw_only=True)
class OverallState:
    """Overall state for the entire workflow."""
    urls: list[str]
    extraction_schema: dict[str, Any] = field(default_factory=lambda: DEFAULT_EXTRACTION_SCHEMA)
    user_notes: str = field(default="")
    completed_notes: Annotated[list, operator.add] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)
    is_satisfactory: dict[str, bool] = field(default_factory=dict)
    reflection_steps_taken: dict[str, int] = field(default_factory=dict)
    generate_cold_email: bool = field(default=False)
    email_config: Optional[dict[str, Any]] = field(default=None)
    generated_emails: dict[str, str] = field(default_factory=dict)

# ⚠️ HIER IST DER FIX: OutputState muss generated_emails explizit definieren
@dataclass(kw_only=True)
class OutputState:
    """The response object for the end user."""
    info: dict[str, dict[str, Any]]
    """A dictionary mapping company URLs to their extracted information"""
    
    # ⚠️ WICHTIG: generated_emails explizit mit default_factory definieren
    generated_emails: dict[str, str] = field(default_factory=dict)
    "Generated cold emails for each company if requested"