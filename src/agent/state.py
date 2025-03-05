from dataclasses import dataclass, field
from typing import Any, Optional, Annotated
import operator


DEFAULT_PRICE_EXTRACTION_SCHEMA = {
    "title": "company_pricing_information",
    "description": "Information about a company's pricing structure and features",
    "type": "object",
    "properties": {
        "company_name": {
            "type": "string",
            "description": "Name of the company to research."
        },
        "pricing_tiers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the pricing tier (e.g., Basic, Pro, Enterprise)"
                    },
                    "price": {
                        "type": "string",
                        "description": "Price for this tier (including currency and billing frequency)"
                    },
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of features included in this tier"
                    }
                }
            },
            "description": "Available pricing tiers and their features",
        },
        "free_tier_available": {
            "type": "boolean",
            "description": "Whether a free tier or trial is available",
        },
        "enterprise_pricing": {
            "type": "string",
            "description": "Information about enterprise pricing if available",
        },
        "additional_fees": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any additional fees or charges not included in base pricing",
        }
    },
    "required": ["pricing_tiers", "company_name"]
}

DEFAULT_EXTRACTION_SCHEMA = {
  "title": "company_marketing_analysis",
  "description": "Comprehensive marketing profile analysis for a company, focusing on brand, audience, messaging, channels, and competitive positioning",
  "type": "object",
  "properties": {
    "company_name": {
      "type": "string",
      "description": "Name of the company to research."
    },
    "brand_mission_vision": {
      "type": "string",
      "description": "Company's overarching mission statement and vision."
    },
    "unique_selling_proposition": {
      "type": "string",
      "description": "What distinctly sets this company apart from competitors."
    },
    "target_audience_personas": {
      "type": "array",
      "description": "Key audience segments/personas the company targets",
      "items": {
        "type": "object",
        "properties": {
          "persona_name": {
            "type": "string",
            "description": "Name or label of the persona (e.g., 'Tech-savvy freelancer')."
          },
          "demographics": {
            "type": "string",
            "description": "General demographic info (age range, location, etc.)."
          },
          "pain_points": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Common challenges or problems faced by this persona."
          },
          "motivations": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Key motivations or drivers leading this persona to seek solutions."
          }
        }
      }
    },
    "brand_voice": {
      "type": "string",
      "description": "Tone and style of communication used by the brand (e.g., friendly, formal, authoritative)."
    },
    "marketing_channels": {
      "type": "array",
      "description": "Channels used for marketing outreach (online/offline).",
      "items": {
        "type": "object",
        "properties": {
          "channel_name": {
            "type": "string",
            "description": "Name of the channel (e.g., Facebook, Google Ads, Trade Shows)."
          },
          "campaign_types": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Specific campaigns or strategies used on this channel (e.g., social ads, influencer partnerships)."
          },
          "effectiveness_rating": {
            "type": "string",
            "description": "Qualitative or quantitative assessment of how effective the channel has been (e.g., high, medium, low)."
          }
        }
      }
    },
    "competitive_landscape": {
      "type": "array",
      "description": "Key competitors and brief analysis of their positioning.",
      "items": {
        "type": "object",
        "properties": {
          "competitor_name": {
            "type": "string",
            "description": "Name of the competitor."
          },
          "strengths": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Competitor's strengths in terms of branding, marketing, product differentiation, etc."
          },
          "weaknesses": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Competitor's weaknesses or areas where they may fall short."
          },
          "marketing_positioning": {
            "type": "string",
            "description": "Short summary of how the competitor positions itself in the market."
          }
        }
      }
    },
    "swot_analysis": {
      "type": "object",
      "description": "High-level SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.",
      "properties": {
        "strengths": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Internal attributes that are helpful in achieving objectives."
        },
        "weaknesses": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Internal attributes that are harmful in achieving objectives."
        },
        "opportunities": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "External conditions that are helpful in achieving objectives."
        },
        "threats": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "External conditions that could damage performance."
        }
      }
    },
    "marketing_goals_and_kpis": {
      "type": "array",
      "description": "List of marketing objectives and their corresponding key performance indicators (KPIs).",
      "items": {
        "type": "object",
        "properties": {
          "goal": {
            "type": "string",
            "description": "High-level marketing goal (e.g., increase brand awareness)."
          },
          "kpi": {
            "type": "string",
            "description": "Measure used to track progress towards the goal (e.g., social media reach, leads per month)."
          }
        }
      }
    },
    "key_brand_messages": {
      "type": "array",
      "description": "Core messages and slogans communicated by the brand.",
      "items": {
        "type": "string"
      }
    },
    "overall_positioning_statement": {
      "type": "string",
      "description": "Single, concise statement that describes how the brand is positioned in the market."
    },
    "brand_reputation_overview": {
      "type": "string",
      "description": "General sentiment or perception of the brand in the marketplace (e.g., positive, negative, neutral)."
    }
  },
  "required": [
    "company_name",
    "unique_selling_proposition",
    "target_audience_personas",
    "marketing_channels"
  ]
}


@dataclass(kw_only=True)
class InputState:
    """Input state defines the interface between the graph and the user (external API)."""

    urls: list[str]
    "URLs to scrape for company information."

    extraction_schema: dict[str, Any] = field(
        default_factory=lambda: DEFAULT_EXTRACTION_SCHEMA
    )
    "The json schema defines the information the agent is tasked with filling out."

    user_notes: Optional[dict[str, Any]] = field(default=None)
    "Any notes from the user to start the research process."


@dataclass(kw_only=True)
class OverallState:
    """Input state defines the interface between the graph and the user (external API)."""

    urls: list[str]
    "URLs to scrape for company information."

    extraction_schema: dict[str, Any] = field(
        default_factory=lambda: DEFAULT_EXTRACTION_SCHEMA
    )
    "The json schema defines the information the agent is tasked with filling out."

    user_notes: str = field(default=None)
    "Any notes from the user to start the research process."

    completed_notes: Annotated[list, operator.add] = field(default_factory=list)
    "Notes from completed research related to the schema"

    info: dict[str, Any] = field(default=None)
    """
    A dictionary containing the extracted and processed information
    based on the user's query and the graph's execution.
    This is the primary output of the enrichment process.
    """

    is_satisfactory: bool = field(default=None)
    "True if all required fields are well populated, False otherwise"

    reflection_steps_taken: int = field(default=0)
    "Number of times the reflection node has been executed"


@dataclass(kw_only=True)
class OutputState:
    """The response object for the end user.

    This class defines the structure of the output that will be provided
    to the user after the graph's execution is complete.
    """

    info: dict[str, dict[str, Any]]
    """
    A dictionary mapping company URLs to their extracted information
    based on the user's query and the graph's execution.
    """
