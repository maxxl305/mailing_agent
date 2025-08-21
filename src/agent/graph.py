# src/agent/graph.py - Erweitert mit echter Meta Ad Intelligence

import asyncio
from typing import cast, Any, Literal
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field
from langchain_community.document_loaders.firecrawl import FireCrawlLoader

from agent.configuration import Configuration
from agent.state import InputState, OutputState, OverallState
from agent.prompts import (
    REFLECTION_PROMPT,
    INFO_PROMPT,
    COLD_EMAIL_PROMPT,
    META_AD_ANALYSIS_PROMPT,
)
from agent.meta_ad_client import (
    get_company_ad_intelligence
)

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# LLMs
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4,
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

llm = ChatOpenAI(model="gpt-4o")

class ReflectionOutput(BaseModel):
    is_satisfactory: bool = Field(
        description="True if all required fields are well populated, False otherwise"
    )
    missing_fields: list[str] = Field(
        description="List of field names that are missing or incomplete"
    )
    reasoning: str = Field(description="Brief explanation of the assessment")

class ColdEmailOutput(BaseModel):
    subject_line: str = Field(description="Compelling email subject line")
    email_body: str = Field(description="Complete email body text")
    key_insights_used: list[str] = Field(
        description="List of specific research insights referenced in the email"
    )
    personalization_score: int = Field(
        description="Score from 1-10 rating how personalized the email is based on research results for the underlying domain."
    )

# Meta Ad Intelligence Output
class MetaAdIntelligenceOutput(BaseModel):
    advertising_status: str = Field(description="Current advertising status on Meta platforms")
    active_campaigns_summary: str = Field(description="Summary of active campaigns")
    creative_strategy_analysis: str = Field(description="Analysis of creative strategies")
    targeting_insights: str = Field(description="Insights into audience targeting")
    competitive_analysis: str = Field(description="Competitive advertising analysis")
    budget_assessment: str = Field(description="Assessment of advertising spend and budget")
    optimization_opportunities: list[str] = Field(description="Identified optimization opportunities")
    advertising_sophistication_level: str = Field(description="Level of advertising sophistication")

# Company Information Researcher
async def company_information_researcher(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Execute a multi-step web search and information extraction process for comprehensive company analysis with a particular focus on marketing."""
    print("🔍 Starting company_information_researcher...")
    print(f"📧 Email generation requested: {getattr(state, 'generate_cold_email', False)}")
    
    results = {}
    
    for url in state.urls:
        print(f"📊 Processing URL with crawl mode: {url}")
        
        # Initialize FireCrawlLoader with crawl mode for comprehensive analysis
        base_url = url.split('/')[2]  # Extract domain from URL
        loader = FireCrawlLoader(
            api_key=FIRECRAWL_API_KEY,
            url=f"https://{base_url}",
            mode="crawl",
            params={
                "limit": 20,
                "excludes": [
                    "/docs*",
                    "/guides*",
                    "/chains*",
                    "/blog*",
                    "*.pdf",
                    "*.jpg",
                    "*.png",
                    "*.gif",
                    "/networks*"
                ],
                "includes": []
            }
        )
            
        data = loader.load()
        
        # Combine all page contents
        combined_content = ""
        for page in data:
            if isinstance(page, dict) and "content" in page:
                combined_content += f"\nPage URL: {page.get('url', 'Unknown')}\n"
                combined_content += f"Content: {page['content']}\n"
                combined_content += "=" * 80 + "\n"
        
        print(f"📄 Crawled {len(data)} pages for {url}")
        
        # Generate structured notes using the extended marketing analysis schema
        p = INFO_PROMPT.format(
            info=json.dumps(state.extraction_schema, indent=2),
            content=combined_content,
            company=url,
            user_notes=state.user_notes,
        )
        structured_llm = llm.with_structured_output(state.extraction_schema)
        result = structured_llm.invoke(
            [
                {"role": "system", "content": p},
                {
                    "role": "user",
                    "content": "Produce a structured output from this information.",
                },
            ]
        )
        results[url] = result

    return {
        "info": results,
        "is_satisfactory": {url: False for url in state.urls},
        "reflection_steps_taken": {url: 0 for url in state.urls},
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

# Meta Ad Intelligence Analyzer
async def meta_ad_analyzer(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Analyze Meta advertising intelligence for each company URL using real Meta API."""
    print("🎯 Starting Meta Ad Intelligence Analysis (Real API)...")
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    
    # Check if Meta ad analysis is enabled and configured
    if not configurable.should_analyze_meta_ads():
        print("ℹ️  Meta ad analysis disabled or no token available - skipping")
        return {
            "meta_ad_intelligence": {
                url: {
                    "llm_analysis": {
                        "advertising_status": "no_token_available",
                        "active_campaigns_summary": "Meta API access token not configured",
                        "creative_strategy_analysis": "Analysis not available without Meta API token",
                        "targeting_insights": "Analysis not available without Meta API token",
                        "competitive_analysis": "Analysis not available without Meta API token", 
                        "budget_assessment": "Analysis not available without Meta API token",
                        "optimization_opportunities": [],
                        "advertising_sophistication_level": "unknown"
                    },
                    "raw_performance_data": {},
                    "analysis_timestamp": datetime.now().isoformat(),
                    "api_status": "no_token"
                } for url in state.urls
            }
        }
    
    ad_intelligence_results = {}
    meta_config = configurable.get_meta_api_config()
    access_token = meta_config.get("access_token")
    
    for url in state.urls:
        print(f"📱 Analyzing Meta ads for: {url}")
        
        try:
            # Extract company name from URL for search
            company_name = url.replace("https://", "").replace("http://", "").split("/")[0].split(".")[0]
            
            # Get real ad intelligence data
            raw_ad_data = await get_company_ad_intelligence(
                company_url=url,
                company_name=company_name,
                access_token=access_token
            )
            
            # Check if API call was successful
            if raw_ad_data.get("error"):
                print(f"⚠️  Meta API error for {url}: {raw_ad_data.get('message', 'Unknown error')}")
                # Graceful fallback - store error info but continue
                ad_intelligence_results[url] = {
                    "llm_analysis": {
                        "advertising_status": "api_error",
                        "active_campaigns_summary": f"Meta API Error: {raw_ad_data.get('message', 'Unknown error')}",
                        "creative_strategy_analysis": "Analysis not available due to API error",
                        "targeting_insights": "Analysis not available due to API error",
                        "competitive_analysis": "Analysis not available due to API error", 
                        "budget_assessment": "Analysis not available due to API error",
                        "optimization_opportunities": ["Fix Meta API configuration to enable advertising analysis"],
                        "advertising_sophistication_level": "unknown"
                    },
                    "raw_performance_data": raw_ad_data.get("performance_analysis", {}),
                    "analysis_timestamp": raw_ad_data.get("analysis_timestamp"),
                    "api_status": "error",
                    "error_details": raw_ad_data
                }
                continue
            
            # Prepare data for LLM analysis
            performance_analysis = raw_ad_data.get("performance_analysis", {})
            ad_data_summary = {
                "company_url": url,
                "advertising_status": performance_analysis.get("advertising_status", "unknown"),
                "total_ads": performance_analysis.get("total_ads", 0),
                "active_ads": performance_analysis.get("active_ads", 0),
                "estimated_spend": performance_analysis.get("estimated_monthly_spend", "Unknown"),
                "platforms": performance_analysis.get("platform_distribution", {}),
                "demographics": performance_analysis.get("primary_demographics", {}),
                "themes": performance_analysis.get("common_themes", []),
                "sophistication": performance_analysis.get("campaign_sophistication", "unknown"),
                "raw_ads_sample": raw_ad_data.get("raw_ads_data", {}).get("data", [])[:3]
            }
            
            # Only run LLM analysis if we have actual ad data
            if performance_analysis.get("advertising_status") not in ["no_ads_found", "api_error"]:
                # Use LLM to analyze and structure the ad intelligence
                ad_analysis_prompt = META_AD_ANALYSIS_PROMPT.format(
                    company_url=url,
                    ad_data=json.dumps(ad_data_summary, indent=2),
                    user_notes=state.user_notes or "No specific notes provided"
                )
                
                structured_llm = llm.with_structured_output(MetaAdIntelligenceOutput)
                llm_analysis = structured_llm.invoke([
                    {"role": "system", "content": ad_analysis_prompt},
                    {"role": "user", "content": f"Analyze the Meta advertising intelligence for {company_name}"}
                ])
                
                llm_analysis_dict = llm_analysis.dict()
            else:
                # No ads found - create basic analysis
                llm_analysis_dict = {
                    "advertising_status": "no_ads_found",
                    "active_campaigns_summary": "No active advertising campaigns found on Meta platforms",
                    "creative_strategy_analysis": "No advertising creative strategy observed",
                    "targeting_insights": "No targeting data available",
                    "competitive_analysis": "Unable to analyze competitive positioning without advertising data", 
                    "budget_assessment": "No advertising spend detected",
                    "optimization_opportunities": [
                        "Consider starting Meta advertising campaigns",
                        "Establish presence on Facebook and Instagram",
                        "Develop advertising creative strategy"
                    ],
                    "advertising_sophistication_level": "none"
                }
            
            # Combine raw data with LLM analysis
            ad_intelligence_results[url] = {
                "llm_analysis": llm_analysis_dict,
                "raw_performance_data": performance_analysis,
                "analysis_timestamp": raw_ad_data.get("analysis_timestamp"),
                "api_status": raw_ad_data.get("api_status", "success")
            }
            
            print(f"✅ Meta ad analysis completed for {url}")
            print(f"   Status: {llm_analysis_dict['advertising_status']}")
            print(f"   Sophistication: {llm_analysis_dict['advertising_sophistication_level']}")
            
        except Exception as e:
            print(f"❌ Error analyzing Meta ads for {url}: {str(e)}")
            # Graceful fallback
            ad_intelligence_results[url] = {
                "llm_analysis": {
                    "advertising_status": "analysis_failed",
                    "active_campaigns_summary": f"Analysis failed due to error: {str(e)}",
                    "creative_strategy_analysis": "Analysis not available",
                    "targeting_insights": "Analysis not available",
                    "competitive_analysis": "Analysis not available", 
                    "budget_assessment": "Analysis not available",
                    "optimization_opportunities": ["Retry Meta advertising analysis"],
                    "advertising_sophistication_level": "unknown"
                },
                "raw_performance_data": {},
                "analysis_timestamp": datetime.now().isoformat(),
                "api_status": "failed",
                "error_details": {"error": str(e)}
            }
    
    return {
        "meta_ad_intelligence": ad_intelligence_results
    }

def reflection(state: OverallState) -> dict[str, Any]:
    """Reflect on the extracted information for each company - with more lenient satisfaction criteria."""
    print("🤔 Starting reflection...")
    print(f"📧 Email generation flag in reflection: {getattr(state, 'generate_cold_email', False)}")
    
    results = {}
    
    for url in state.urls:
        # Pragmatische Bewertung statt strenger LLM-Evaluation
        website_data = state.info.get(url, {})
        meta_data = state.meta_ad_intelligence.get(url, {}) if hasattr(state, 'meta_ad_intelligence') else {}
        
        # Prüfe ob grundlegende Daten vorhanden sind
        has_company_name = bool(website_data.get('company_name'))
        has_basic_info = bool(website_data.get('unique_selling_proposition')) or bool(website_data.get('brand_mission_vision'))
        has_marketing_channels = bool(website_data.get('marketing_channels'))
        has_online_presence = bool(website_data.get('online_marketing_presence'))
        has_some_meta_data = bool(meta_data)
        
        # Pragmatische Satisfaction-Kriterien
        basic_requirements_met = has_company_name and (has_basic_info or has_marketing_channels)
        good_data_quality = has_online_presence or has_some_meta_data
        
        # Entscheidung: Mehr Fokus auf "brauchbare Daten" statt "vollständige Daten"
        is_satisfactory = basic_requirements_met and good_data_quality
        
        results[url] = is_satisfactory
        
        print(f"   📊 Satisfaction check for {url}:")
        print(f"      Company Name: {'✅' if has_company_name else '❌'}")
        print(f"      Basic Info: {'✅' if has_basic_info else '❌'}")
        print(f"      Marketing Channels: {'✅' if has_marketing_channels else '❌'}")
        print(f"      Online Presence: {'✅' if has_online_presence else '❌'}")
        print(f"      Meta Data: {'✅' if has_some_meta_data else '❌'}")
        print(f"      → Overall Satisfaction: {'✅' if is_satisfactory else '❌'}")
        
        # Zusätzliche Debugging-Info
        if not is_satisfactory:
            print(f"      ⚠️  Missing: {', '.join([
                'Company Name' if not has_company_name else '',
                'Basic Info' if not has_basic_info else '',
                'Marketing Data' if not (has_marketing_channels or has_online_presence) else '',
                'Meta Data' if not has_some_meta_data else ''
            ]).strip(', ')}")

    return {
        "is_satisfactory": results,
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

async def generate_cold_emails(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Generate personalized cold emails based on company research results including Meta ad intelligence."""
    print("📧 Starting email generation...")
    print(f"📊 URLs to process: {state.urls}")
    print(f"🔧 Email config present: {bool(getattr(state, 'email_config', None))}")
    
    if not getattr(state, 'generate_cold_email', False):
        print("❌ generate_cold_email is False - skipping")
        return {"generated_emails": {}}
        
    if not getattr(state, 'email_config', None):
        print("❌ email_config is None - skipping")
        return {"generated_emails": {}}
    
    generated_emails = {}
    
    for url, company_data in state.info.items():
        print(f"📝 Generating email for: {url}")
        
        # Combine website analysis with Meta ad intelligence
        enhanced_company_data = {
            "website_analysis": company_data,
            "meta_advertising_intelligence": state.meta_ad_intelligence.get(url, {}) if hasattr(state, 'meta_ad_intelligence') else {}
        }
        
        # Format the enhanced company data for the prompt
        company_data_str = json.dumps(enhanced_company_data, indent=2)
        
        # Create the enhanced prompt
        email_prompt = COLD_EMAIL_PROMPT.format(
            company_data=company_data_str,
            sender_company=state.email_config.get("sender_company", "Your Company"),
            sender_name=state.email_config.get("sender_name", "Your Name"),
            sender_role=state.email_config.get("sender_role", "Your Role"),
            service_offering=state.email_config.get("service_offering", "Our Services"),
            email_tone=state.email_config.get("email_tone", "professional"),
            email_length=state.email_config.get("email_length", "medium"),
            call_to_action=state.email_config.get("call_to_action", "schedule a call"),
            user_notes=getattr(state, 'user_notes', "") or "No additional notes provided"
        )
        
        # Generate structured email output
        structured_llm = llm.with_structured_output(ColdEmailOutput)
        result = structured_llm.invoke([
            {"role": "system", "content": email_prompt},
            {
                "role": "user", 
                "content": f"Generate a personalized cold email for {company_data.get('company_name', url)} using both website and Meta advertising insights"
            }
        ])
        
        # Format the final email
        formatted_email = f"""Subject: {result.subject_line}

{result.email_body}

---
Research Insights Used:
{chr(10).join(f"• {insight}" for insight in result.key_insights_used)}

Personalization Score: {result.personalization_score}/10
"""
        
        generated_emails[url] = formatted_email
        print(f"✅ Email generated for {url} (Score: {result.personalization_score}/10)")
    
    return {"generated_emails": generated_emails}

def route_from_reflection(
    state: OverallState, config: RunnableConfig
) -> Literal[END, "company_information_researcher", "meta_ad_analyzer", "generate_cold_emails"]:
    """Route the graph based on the reflection output - with more pragmatic routing."""
    print("\n🛤️ Enhanced Routing decision...")
    print(f"📧 generate_cold_email: {getattr(state, 'generate_cold_email', False)}")
    print(f"🔧 email_config present: {bool(getattr(state, 'email_config', None))}")
    print(f"🎯 meta_ad_intelligence present: {hasattr(state, 'meta_ad_intelligence')}")
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Check if we have basic data for all URLs
    has_basic_data = all(
        bool(state.info.get(url, {}).get('company_name')) 
        for url in state.urls
    ) if state.info else False
    
    # Check if Meta Ad analysis is missing
    meta_ad_missing = not hasattr(state, 'meta_ad_intelligence') or not state.meta_ad_intelligence
    
    # Check satisfaction status
    all_satisfactory = all(state.is_satisfactory.values()) if state.is_satisfactory else False
    
    print(f"✅ Has basic data: {has_basic_data}")
    print(f"✅ All satisfactory: {all_satisfactory}")
    print(f"🎯 Meta ad analysis needed: {meta_ad_missing}")

    # Pragmatische Routing Logic:
    
    # 1. If we have basic data but missing Meta Ad analysis, do that first
    if has_basic_data and meta_ad_missing:
        print("➡️ Routing to: meta_ad_analyzer (basic data ready, need Meta ads)")
        return "meta_ad_analyzer"
    
    # 2. If we have basic data + Meta ads and email is requested, generate email
    email_requested = getattr(state, 'generate_cold_email', False) and getattr(state, 'email_config', None)
    if has_basic_data and not meta_ad_missing and email_requested:
        print("➡️ Routing to: generate_cold_emails (all data ready)")
        return "generate_cold_emails"
    
    # 3. If we have basic data and no email needed, end successfully
    if has_basic_data and not email_requested:
        print("➡️ Routing to: END (basic data complete, no email needed)")
        return END
    
    # 4. If we don't have basic data and haven't hit max reflection steps, try again
    current_reflection_steps = max(state.reflection_steps_taken.values()) if state.reflection_steps_taken else 0
    max_steps_reached = current_reflection_steps >= configurable.max_reflection_steps
    
    if not has_basic_data and not max_steps_reached:
        print("➡️ Routing to: company_information_researcher (need more basic data)")
        return "company_information_researcher"
    
    # 5. If we have ANY data and email is requested, try to generate email anyway
    has_any_data = bool(state.info)
    if has_any_data and email_requested:
        print("➡️ Routing to: generate_cold_emails (partial data, try anyway)")
        return "generate_cold_emails"
    
    # 6. Final fallback - end the process
    print("➡️ Routing to: END (fallback - process complete)")
    return END

# Graph Setup
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)

# Nodes hinzufügen
builder.add_node("company_information_researcher", company_information_researcher)
builder.add_node("meta_ad_analyzer", meta_ad_analyzer)
builder.add_node("reflection", reflection)
builder.add_node("generate_cold_emails", generate_cold_emails)

# Edges hinzufügen
builder.add_edge(START, "company_information_researcher")
builder.add_edge("company_information_researcher", "reflection")
builder.add_edge("meta_ad_analyzer", "reflection")
builder.add_conditional_edges("reflection", route_from_reflection)
builder.add_edge("generate_cold_emails", END)

# Compile
graph = builder.compile()