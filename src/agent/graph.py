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
)

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# LLMs

rate_limiter = InMemoryRateLimiter(
    requests_per_second=4,
    check_every_n_seconds=0.1,
    max_bucket_size=10,  # Controls the maximum burst size.
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


async def company_pricing_researcher(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Execute a multi-step web search and information extraction process."""
    results = {}
    for url in state.urls:
        # Initialize FireCrawlLoader
        loader = FireCrawlLoader(
            api_key=FIRECRAWL_API_KEY,
            url=url,
            mode="scrape",
        )
            
        data = loader.load()
        
        # Generate structured notes
        p = INFO_PROMPT.format(
            info=json.dumps(state.extraction_schema, indent=2),
            content=data,
            company=url,  # Pass URL as reference since company name will be extracted
            user_notes=state.user_notes,
        )
        structured_llm = llm.with_structured_output(state.extraction_schema)
        result = structured_llm.invoke(
            [
                {"role": "system", "content": p},
                {
                    "role": "user",
                    "content": "Produce a structured output from these notes.",
                },
            ]
        )
        results[url] = result
    
    return {
        "info": results,
        "is_satisfactory": {url: False for url in state.urls},
        "reflection_steps_taken": {url: 0 for url in state.urls}
    }

async def company_information_researcher(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Execute a multi-step web search and information extraction process."""
    results = {}
    
    for url in state.urls:
        # Initialize FireCrawlLoader with crawl mode
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
                "includes": [
                ]
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
        
        # Generate structured notes
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
        "reflection_steps_taken": {url: 0 for url in state.urls}
    }

def reflection(state: OverallState) -> dict[str, Any]:
    """Reflect on the extracted information for each company."""
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

    return {"is_satisfactory": results}


def route_from_reflection(
    state: OverallState, config: RunnableConfig
) -> Literal[END, "company_pricing_researcher"]:  # type: ignore
    """Route the graph based on the reflection output."""
    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # If we have satisfactory results, end the process
    if state.is_satisfactory:
        return END

    # If results aren't satisfactory but we haven't hit max steps, continue research
    if state.reflection_steps_taken <= configurable.max_reflection_steps:
        return "company_pricing_researcher"

    # If we've exceeded max steps, end even if not satisfactory
    return END


# Add nodes and edges
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)
builder.add_node("company_pricing_researcher", company_pricing_researcher)

# Uncomment here to use the information researcher
# builder.add_node("company_information_researcher", company_information_researcher)
builder.add_node("reflection", reflection)

builder.add_edge(START, "company_pricing_researcher")

# Uncomment here to use the information researcher
# builder.add_edge("company_pricing_researcher", "company_information_researcher")
builder.add_edge("company_pricing_researcher", "reflection")
builder.add_conditional_edges("reflection", route_from_reflection)

# Compile
graph = builder.compile()
