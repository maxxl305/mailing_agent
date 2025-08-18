# src/agent/graph.py - Updated with Intelligent Meta System

import asyncio
from typing import cast, Any, Literal
import os
import json
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

class MetaAdIntelligenceOutput(BaseModel):
    advertising_status: str = Field(description="Current advertising status on Meta platforms")
    active_campaigns_summary: str = Field(description="Summary of active campaigns")
    creative_strategy_analysis: str = Field(description="Analysis of creative strategies")
    targeting_insights: str = Field(description="Insights into audience targeting")
    competitive_analysis: str = Field(description="Competitive advertising analysis")
    budget_assessment: str = Field(description="Assessment of advertising spend and budget")
    optimization_opportunities: list[str] = Field(description="Identified optimization opportunities")
    advertising_sophistication_level: str = Field(description="Level of advertising sophistication")

# Company Information Researcher (unchanged)
async def company_information_researcher(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Execute a multi-step web search and information extraction process for comprehensive company analysis with a particular focus on marketing."""
    print("🔍 Starting company_information_researcher...")
    print(f"📧 Email generation requested: {getattr(state, 'generate_cold_email', False)}")
    
    results = {}
    
    for url in state.urls:
        print(f"📊 Processing URL with crawl mode: {url}")
        
        base_url = url.split('/')[2]
        loader = FireCrawlLoader(
            api_key=FIRECRAWL_API_KEY,
            url=f"https://{base_url}",
            mode="crawl",
            params={
                "limit": 20,
                "excludes": [
                    "/docs*", "/guides*", "/chains*", "/blog*", "*.pdf", 
                    "*.jpg", "*.png", "*.gif", "/networks*"
                ],
                "includes": []
            }
        )
            
        data = loader.load()
        
        combined_content = ""
        for page in data:
            if isinstance(page, dict) and "content" in page:
                combined_content += f"\nPage URL: {page.get('url', 'Unknown')}\n"
                combined_content += f"Content: {page['content']}\n"
                combined_content += "=" * 80 + "\n"
        
        print(f"📄 Crawled {len(data)} pages for {url}")
        
        p = INFO_PROMPT.format(
            info=json.dumps(state.extraction_schema, indent=2),
            content=combined_content,
            company=url,
            user_notes=state.user_notes,
        )
        structured_llm = llm.with_structured_output(state.extraction_schema)
        result = structured_llm.invoke([
            {"role": "system", "content": p},
            {"role": "user", "content": "Produce a structured output from this information."},
        ])
        results[url] = result

    return {
        "info": results,
        "is_satisfactory": {url: False for url in state.urls},
        "reflection_steps_taken": {url: 0 for url in state.urls},
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

# ⭐ NEW: Intelligent Meta Ad Analyzer
async def meta_ad_analyzer(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Intelligent Meta Ad Analysis - Real API or clear 'no ads' status."""
    print("🧠 Starting Intelligent Meta Ad Analysis...")
    
    configuration = Configuration.from_runnable_config(config)
    ad_intelligence_results = {}
    
    # Import intelligent system
    from agent.meta_intelligent_hybrid import get_intelligent_meta_analysis
    
    for url in state.urls:
        print(f"📱 Intelligent Meta analysis for: {url}")
        
        try:
            # Use intelligent analysis
            meta_result = await get_intelligent_meta_analysis(url)
            
            if meta_result["success"]:
                if meta_result["meta_ads_available"]:
                    # Company has real Meta ads - do full analysis
                    print(f"✅ Real Meta ads found for {meta_result['company_name']}")
                    
                    analysis = meta_result["analysis"]
                    
                    # Prepare data for LLM analysis
                    ad_data_summary = {
                        "company_url": url,
                        "company_name": meta_result["company_name"],
                        "advertising_status": analysis["advertising_status"],
                        "total_ads": analysis["total_ads"],
                        "active_ads": analysis["active_ads"],
                        "estimated_monthly_spend": analysis["estimated_monthly_spend_eur"],
                        "campaign_sophistication": analysis["campaign_sophistication"],
                        "platforms": analysis["platforms"],
                        "platform_distribution": analysis["platform_distribution"],
                        "sample_creatives": analysis["sample_creatives"],
                        "last_activity": analysis["last_ad_activity"],
                        "data_source": "real_meta_api",
                        "confidence": analysis["analysis_confidence"]
                    }
                    
                    # LLM Analysis for real data
                    enhanced_prompt = f"""
{META_AD_ANALYSIS_PROMPT}

IMPORTANT: This is REAL Meta advertising data from the official Ad Library API.
Use this authentic data to provide accurate, factual insights about the company's actual advertising strategy.

Data Quality: High - Real API Data
Confidence Level: {analysis["analysis_confidence"]}
"""
                    
                    ad_analysis_prompt = enhanced_prompt.format(
                        company_url=url,
                        ad_data=json.dumps(ad_data_summary, indent=2),
                        user_notes=state.user_notes or "No specific notes provided"
                    )
                    
                    structured_llm = llm.with_structured_output(MetaAdIntelligenceOutput)
                    llm_analysis = structured_llm.invoke([
                        {"role": "system", "content": ad_analysis_prompt},
                        {"role": "user", "content": f"Analyze the real Meta advertising data for {meta_result['company_name']}"}
                    ])
                    
                    # Store results with real data
                    ad_intelligence_results[url] = {
                        "llm_analysis": llm_analysis.dict(),
                        "raw_performance_data": analysis,
                        "analysis_timestamp": meta_result["timestamp"],
                        "api_source": "real_meta_api",
                        "meta_ads_available": True,
                        "intelligence_quality": "high",
                        "company_name": meta_result["company_name"],
                        "total_relevant_ads": meta_result["total_relevant_ads"]
                    }
                    
                    print(f"   📊 {analysis['total_ads']} ads, {analysis['campaign_sophistication']} sophistication")
                    print(f"   💰 Est. spend: €{analysis['estimated_monthly_spend_eur']}")
                    
                else:
                    # No relevant Meta ads found - clear status
                    print(f"📝 No Meta ads found for {meta_result['company_name']}")
                    
                    ad_intelligence_results[url] = {
                        "llm_analysis": {
                            "advertising_status": "no_meta_advertising",
                            "active_campaigns_summary": f"{meta_result['company_name']} does not currently run Meta advertising campaigns",
                            "creative_strategy_analysis": "No Meta advertising activity detected",
                            "targeting_insights": "Meta advertising analysis not available - no active campaigns found",
                            "competitive_analysis": "Consider exploring Meta advertising as competitors may be active on these platforms",
                            "budget_assessment": "No Meta advertising budget detected",
                            "optimization_opportunities": [
                                "Explore Meta advertising as a new marketing channel",
                                "Research competitor presence on Meta platforms",
                                "Consider starting with small-budget Meta campaigns to test audience response"
                            ],
                            "advertising_sophistication_level": "not_applicable"
                        },
                        "raw_performance_data": {
                            "advertising_status": "no_meta_advertising",
                            "total_ads": 0,
                            "active_ads": 0,
                            "platforms": [],
                            "estimated_monthly_spend": "€0",
                            "campaign_sophistication": "none"
                        },
                        "analysis_timestamp": meta_result["timestamp"],
                        "api_source": "real_meta_api_search",
                        "meta_ads_available": False,
                        "intelligence_quality": "not_applicable",
                        "company_name": meta_result["company_name"],
                        "no_ads_message": meta_result["message"],
                        "recommendation": meta_result.get("recommendation", "")
                    }
                    
                    print(f"   💡 Recommendation: {meta_result.get('recommendation', 'No specific recommendation')}")
            else:
                # Analysis failed
                print(f"❌ Meta analysis failed for {url}: {meta_result.get('message', 'Unknown error')}")
                
                ad_intelligence_results[url] = {
                    "llm_analysis": {
                        "advertising_status": "analysis_unavailable",
                        "active_campaigns_summary": "Meta advertising analysis temporarily unavailable",
                        "creative_strategy_analysis": "Unable to analyze Meta advertising data",
                        "targeting_insights": "Meta advertising intelligence not available",
                        "competitive_analysis": "Meta advertising analysis could not be completed",
                        "budget_assessment": "Meta advertising budget analysis unavailable",
                        "optimization_opportunities": [
                            "Retry Meta advertising analysis when service is available",
                            "Focus on other marketing intelligence sources",
                            "Consider manual research of competitor Meta presence"
                        ],
                        "advertising_sophistication_level": "unknown"
                    },
                    "raw_performance_data": {},
                    "analysis_timestamp": meta_result.get("timestamp"),
                    "api_source": "error",
                    "meta_ads_available": False,
                    "intelligence_quality": "error",
                    "error_message": meta_result.get("message", "Analysis failed"),
                    "company_name": url.split("//")[1].split("/")[0] if "//" in url else "Unknown"
                }
                
        except Exception as e:
            print(f"❌ Exception in Meta analysis for {url}: {str(e)}")
            
            # Graceful fallback
            ad_intelligence_results[url] = {
                "llm_analysis": {
                    "advertising_status": "analysis_failed",
                    "active_campaigns_summary": f"Meta advertising analysis failed due to technical issues",
                    "creative_strategy_analysis": "Technical error prevented Meta advertising analysis",
                    "targeting_insights": "Meta advertising data unavailable due to technical issues",
                    "competitive_analysis": "Meta advertising analysis could not be completed",
                    "budget_assessment": "Unable to assess Meta advertising budget",
                    "optimization_opportunities": [
                        "Resolve technical issues with Meta advertising analysis",
                        "Focus on website-based marketing intelligence",
                        "Consider alternative advertising intelligence sources"
                    ],
                    "advertising_sophistication_level": "unknown"
                },
                "raw_performance_data": {},
                "analysis_timestamp": None,
                "api_source": "error",
                "meta_ads_available": False,
                "intelligence_quality": "error",
                "error_message": str(e),
                "company_name": url.split("//")[1].split("/")[0] if "//" in url else "Unknown"
            }
    
    return {
        "meta_ad_intelligence": ad_intelligence_results
    }

def reflection(state: OverallState) -> dict[str, Any]:
    """Reflect on the extracted information - updated for intelligent Meta system."""
    print("🤔 Starting reflection...")
    print(f"📧 Email generation flag in reflection: {getattr(state, 'generate_cold_email', False)}")
    
    results = {}
    
    for url in state.urls:
        website_data = state.info.get(url, {})
        meta_data = state.meta_ad_intelligence.get(url, {}) if hasattr(state, 'meta_ad_intelligence') else {}
        
        # Basic website data requirements
        has_company_name = bool(website_data.get('company_name'))
        has_basic_info = bool(website_data.get('unique_selling_proposition')) or bool(website_data.get('brand_mission_vision'))
        has_marketing_channels = bool(website_data.get('marketing_channels'))
        has_online_presence = bool(website_data.get('online_marketing_presence'))
        
        # Meta data availability (but not required for satisfaction)
        meta_analysis_completed = bool(meta_data)
        
        # Satisfaction based primarily on website data
        basic_requirements_met = has_company_name and (has_basic_info or has_marketing_channels)
        good_data_quality = has_online_presence
        
        # Meta analysis is a bonus but not required
        is_satisfactory = basic_requirements_met and good_data_quality
        
        results[url] = is_satisfactory
        
        print(f"   📊 Satisfaction check for {url}:")
        print(f"      Company Name: {'✅' if has_company_name else '❌'}")
        print(f"      Basic Info: {'✅' if has_basic_info else '❌'}")
        print(f"      Marketing Channels: {'✅' if has_marketing_channels else '❌'}")
        print(f"      Online Presence: {'✅' if has_online_presence else '❌'}")
        print(f"      Meta Analysis: {'✅' if meta_analysis_completed else '❌'} (optional)")
        print(f"      → Overall Satisfaction: {'✅' if is_satisfactory else '❌'}")

    return {
        "is_satisfactory": results,
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

async def generate_cold_emails(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Generate personalized cold emails - updated to handle 'no Meta ads' cases."""
    print("📧 Starting intelligent email generation...")
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
        print(f"📝 Generating intelligent email for: {url}")
        
        # Get Meta intelligence status
        meta_data = state.meta_ad_intelligence.get(url, {}) if hasattr(state, 'meta_ad_intelligence') else {}
        meta_ads_available = meta_data.get('meta_ads_available', False)
        
        # Enhanced company data with Meta status
        enhanced_company_data = {
            "website_analysis": company_data,
            "meta_advertising_intelligence": meta_data if meta_ads_available else {
                "status": "no_meta_advertising",
                "message": "No Meta advertising campaigns detected for this company",
                "opportunity": "Potential to start Meta advertising as a new marketing channel"
            }
        }
        
        company_data_str = json.dumps(enhanced_company_data, indent=2)
        
        # Enhanced email prompt that handles both cases
        email_language = state.email_config.get("email_language", "deutsch")
        
        enhanced_email_prompt = f"""
{COLD_EMAIL_PROMPT}

⭐ CRITICAL LANGUAGE REQUIREMENT:
WRITE THE ENTIRE EMAIL IN {email_language.upper()}!
- Subject line: {email_language}
- Email body: {email_language} 
- All content: {email_language}
- No English phrases or words allowed!

SPECIAL INSTRUCTIONS FOR META ADVERTISING INTELLIGENCE:

Meta Ads Status: {"AVAILABLE - Use real data" if meta_ads_available else "NOT AVAILABLE - Company doesn't run Meta ads"}

{"Use the real Meta advertising data to show specific competitive insights and current campaign analysis." if meta_ads_available else "Focus on the opportunity to START Meta advertising. Position this as an untapped marketing channel with potential for growth."}

Email Strategy:
{"- Reference their current Meta advertising approach and suggest optimizations" if meta_ads_available else "- Highlight that competitors may be using Meta ads while they're not"}
{"- Show specific budget and targeting insights" if meta_ads_available else "- Present Meta advertising as a growth opportunity"}
{"- Competitive analysis based on real advertising data" if meta_ads_available else "- Suggest exploring this new marketing channel"}

⭐ LANGUAGE REMINDER: 
The user specifically requested the email to be written in {email_language.upper()}. 
Make sure EVERY SINGLE WORD of the email (subject + body) is in {email_language}!
"""
        
        email_prompt = enhanced_email_prompt.format(
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
        
        structured_llm = llm.with_structured_output(ColdEmailOutput)
        result = structured_llm.invoke([
            {"role": "system", "content": email_prompt},
            {"role": "user", "content": f"Generate a personalized cold email for {company_data.get('company_name', url)} considering their Meta advertising status: {'Active' if meta_ads_available else 'Not Active'}. IMPORTANT: Write the ENTIRE email in {email_language.upper()} language - subject line, body, everything must be in {email_language}!"}
        ])
        
        # Add Meta status to email insights
        meta_status_insight = "Real Meta advertising data analyzed" if meta_ads_available else "No Meta advertising detected - growth opportunity identified"
        enhanced_insights = result.key_insights_used + [meta_status_insight]
        
        formatted_email = f"""Subject: {result.subject_line}

{result.email_body}

---
Research Insights Used:
{chr(10).join(f"• {insight}" for insight in enhanced_insights)}

Meta Advertising Status: {"✅ Active (real data)" if meta_ads_available else "❌ Not detected (opportunity)"}
Personalization Score: {result.personalization_score}/10
"""
        
        generated_emails[url] = formatted_email
        print(f"✅ Email generated for {url} (Score: {result.personalization_score}/10, Meta: {'Real' if meta_ads_available else 'Opportunity'})")
    
    return {"generated_emails": generated_emails}

def route_from_reflection(
    state: OverallState, config: RunnableConfig
) -> Literal[END, "company_information_researcher", "meta_ad_analyzer", "generate_cold_emails"]:
    """Route the graph based on the reflection output."""
    print("\n🛤️ Intelligent routing decision...")
    print(f"📧 generate_cold_email: {getattr(state, 'generate_cold_email', False)}")
    print(f"🔧 email_config present: {bool(getattr(state, 'email_config', None))}")
    print(f"🧠 meta_ad_intelligence present: {hasattr(state, 'meta_ad_intelligence')}")
    
    configurable = Configuration.from_runnable_config(config)

    has_basic_data = all(
        bool(state.info.get(url, {}).get('company_name')) 
        for url in state.urls
    ) if state.info else False
    
    meta_analysis_missing = not hasattr(state, 'meta_ad_intelligence') or not state.meta_ad_intelligence
    all_satisfactory = all(state.is_satisfactory.values()) if state.is_satisfactory else False
    
    print(f"✅ Has basic data: {has_basic_data}")
    print(f"✅ All satisfactory: {all_satisfactory}")
    print(f"🧠 Meta analysis needed: {meta_analysis_missing}")

    # Always do Meta analysis after website analysis
    if has_basic_data and meta_analysis_missing:
        print("➡️ Routing to: meta_ad_analyzer (website done, need Meta analysis)")
        return "meta_ad_analyzer"
    
    # Generate email if requested and data is ready
    email_requested = getattr(state, 'generate_cold_email', False) and getattr(state, 'email_config', None)
    if has_basic_data and not meta_analysis_missing and email_requested:
        print("➡️ Routing to: generate_cold_emails (all analysis complete)")
        return "generate_cold_emails"
    
    # End if no email requested
    if has_basic_data and not email_requested:
        print("➡️ Routing to: END (analysis complete, no email needed)")
        return END
    
    # Retry website analysis if needed
    current_reflection_steps = max(state.reflection_steps_taken.values()) if state.reflection_steps_taken else 0
    max_steps_reached = current_reflection_steps >= configurable.max_reflection_steps
    
    if not has_basic_data and not max_steps_reached:
        print("➡️ Routing to: company_information_researcher (need more website data)")
        return "company_information_researcher"
    
    # Final fallback
    has_any_data = bool(state.info)
    if has_any_data and email_requested:
        print("➡️ Routing to: generate_cold_emails (partial data, try anyway)")
        return "generate_cold_emails"
    
    print("➡️ Routing to: END (process complete)")
    return END

# Graph building (unchanged)
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)

builder.add_node("company_information_researcher", company_information_researcher)
builder.add_node("meta_ad_analyzer", meta_ad_analyzer)
builder.add_node("reflection", reflection)
builder.add_node("generate_cold_emails", generate_cold_emails)

builder.add_edge(START, "company_information_researcher")
builder.add_edge("company_information_researcher", "reflection")
builder.add_edge("meta_ad_analyzer", "reflection")
builder.add_conditional_edges("reflection", route_from_reflection)
builder.add_edge("generate_cold_emails", END)

graph = builder.compile()
