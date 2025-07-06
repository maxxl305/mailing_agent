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
)

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# LLMs
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4,
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

## Select the LLM you want to use
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

# ✅ COMPANY INFORMATION RESEARCHER (nicht Pricing!)
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
        
        # Generate structured notes using the marketing analysis schema
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

    # Email-Config und Flag weitergeben!
    return {
        "info": results,
        "is_satisfactory": {url: False for url in state.urls},
        "reflection_steps_taken": {url: 0 for url in state.urls},
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

def reflection(state: OverallState) -> dict[str, Any]:
    """Reflect on the extracted information for each company."""
    print("🤔 Starting reflection...")
    print(f"📧 Email generation flag in reflection: {getattr(state, 'generate_cold_email', False)}")
    
    structured_llm = llm.with_structured_output(ReflectionOutput)
    results = {}
    
    for url in state.urls:
        # Format reflection prompt
        system_prompt = REFLECTION_PROMPT.format(
            schema=json.dumps(state.extraction_schema, indent=2),
            info=state.info[url],
        )

        # Invoke
        result = cast(
            ReflectionOutput,
            structured_llm.invoke(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Produce a structured reflection output."},
                ]
            ),
        )
        results[url] = result.is_satisfactory
        print(f"   Satisfaction for {url}: {result.is_satisfactory}")

    # Email-Config und Flag weitergeben!
    return {
        "is_satisfactory": results,
        "generate_cold_email": getattr(state, 'generate_cold_email', False),
        "email_config": getattr(state, 'email_config', None)
    }

async def generate_cold_emails(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Generate personalized cold emails based on company research results."""
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
        
        # Format the company data for the prompt
        company_data_str = json.dumps(company_data, indent=2)
        
        # Create the prompt
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
                "content": f"Generate a personalized cold email for {company_data.get('company_name', url)}"
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
) -> Literal[END, "company_information_researcher", "generate_cold_emails"]:  # ✅ GEÄNDERT!
    """Route the graph based on the reflection output."""
    print("\n🛤️ Routing decision...")
    print(f"📧 generate_cold_email: {getattr(state, 'generate_cold_email', False)}")
    print(f"🔧 email_config present: {bool(getattr(state, 'email_config', None))}")
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Check if all URLs have satisfactory results
    all_satisfactory = all(state.is_satisfactory.values()) if state.is_satisfactory else False
    print(f"✅ All satisfactory: {all_satisfactory}")

    # VEREINFACHTE LOGIK: Immer zur Email-Generierung wenn gewünscht
    if getattr(state, 'generate_cold_email', False) and getattr(state, 'email_config', None):
        print("➡️ Routing to: generate_cold_emails")
        return "generate_cold_emails"

    # If satisfactory and no email needed, end
    if all_satisfactory:
        print("➡️ Routing to: END (satisfactory, no email)")
        return END

    # If not satisfactory and haven't hit max steps, continue research
    max_steps_reached = any(
        steps >= configurable.max_reflection_steps 
        for steps in state.reflection_steps_taken.values()
    ) if state.reflection_steps_taken else False
    
    if not max_steps_reached:
        print("➡️ Routing to: company_information_researcher (not satisfactory)")  # ✅ GEÄNDERT!
        return "company_information_researcher"

    # Max steps reached
    print("➡️ Routing to: END (max steps reached)")
    return END

# ✅ KORREKTER Graph-Aufbau mit INFORMATION RESEARCHER
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)

# Nodes hinzufügen - ✅ INFORMATION RESEARCHER!
builder.add_node("company_information_researcher", company_information_researcher)
builder.add_node("reflection", reflection)
builder.add_node("generate_cold_emails", generate_cold_emails)

# Edges hinzufügen - ✅ RICHTIGE VERBINDUNGEN!
builder.add_edge(START, "company_information_researcher")
builder.add_edge("company_information_researcher", "reflection")
builder.add_conditional_edges("reflection", route_from_reflection)
builder.add_edge("generate_cold_emails", END)

# Compile
graph = builder.compile()
