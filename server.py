from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio

# Import our existing backend
from src.agent.graph import graph
from src.agent.state import EXTENDED_EXTRACTION_SCHEMA

class EmailConfig(BaseModel):
    sender_name: str
    sender_role: str
    sender_company: str
    service_offering: str
    email_tone: str
    email_length: str
    call_to_action: str

class EmailGenerationRequest(BaseModel):
    urls: List[str]
    email_config: EmailConfig
    user_notes: str = ""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyAnalysisRequest(BaseModel):
    urls: List[str]
    user_notes: str = ""
    

@app.get("/")
async def root():
    return {"status": "production server with real backend"}

@app.post("/api/analyze")
async def analyze_company(request: CompanyAnalysisRequest):
    try:
        print(f"🔍 Real backend analyzing: {request.urls}")
        
        # Run real backend
        state = {
            "urls": request.urls,
            "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
            "user_notes": request.user_notes,
            "generate_cold_email": False,
            "meta_ad_intelligence": {},
        }
        
        result = await graph.ainvoke(state)
        
        # Extract real data for first URL
        url = request.urls[0]
        website_data = result.get("info", {}).get(url, {})
        meta_data = result.get("meta_ad_intelligence", {}).get(url, {})
        llm_analysis = meta_data.get("llm_analysis", {})
        
        print(f"✅ Extracted company: {website_data.get('company_name', 'Unknown')}")
        
        # Return real data in frontend format
        return {
            "success": True,
            "data": {
                "company_name": website_data.get("company_name", "Unbekanntes Unternehmen"),
                "unique_selling_proposition": website_data.get("unique_selling_proposition", "Keine Informationen verfügbar"),
                "brand_mission_vision": website_data.get("brand_mission_vision", "Keine Informationen verfügbar"),
                "target_audiences": website_data.get("target_audience_personas", []),
                "website_user_experience": website_data.get("website_user_experience", {}),
                "seo_performance": website_data.get("seo_performance", {}),
                "meta_ad_intelligence": llm_analysis,
                "advertising_status": llm_analysis.get("advertising_status", "unknown"),
                "optimization_opportunities": llm_analysis.get("optimization_opportunities", [])
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}
    
@app.post("/api/generate-email")
async def generate_email(request: EmailGenerationRequest):
    try:
        print(f"📧 Generating email for: {request.urls}")
        
        state = {
            "urls": request.urls,
            "extraction_schema": EXTENDED_EXTRACTION_SCHEMA,
            "user_notes": request.user_notes,
            "generate_cold_email": True,
            "email_config": {
                "sender_company": request.email_config.sender_company,
                "sender_name": request.email_config.sender_name,
                "sender_role": request.email_config.sender_role,
                "service_offering": request.email_config.service_offering,
                "email_tone": request.email_config.email_tone,
                "email_length": request.email_config.email_length,
                "call_to_action": request.email_config.call_to_action,
                "email_language": "deutsch"
            },
            "meta_ad_intelligence": {},
        }
        
        result = await graph.ainvoke(state)
        
        # Extract email for first URL
        url = request.urls[0]
        emails = result.get("generated_emails", {})
        email_content = emails.get(url, "")
        
        # Parse email content
        if email_content:
            lines = email_content.split('\n')
            subject_line = ""
            body_lines = []
            
            # Find subject
            for line in lines:
                if line.startswith('Subject: '):
                    subject_line = line.replace('Subject: ', '').strip()
                    break
            
            # Find body (after first empty line)
            body_start = False
            for line in lines:
                if body_start:
                    body_lines.append(line)
                elif line.strip() == "" and not body_start:
                    body_start = True
            
            body_text = '\n'.join(body_lines).strip()
            
            return {
                "success": True,
                "data": {
                    "subject": subject_line,
                    "body": body_text,
                    "personalization_score": 8,
                    "research_insights": [
                        "Website-Analyse durchgeführt",
                        "Meta Ad Intelligence berücksichtigt", 
                        "Personalisierte Email generiert"
                    ]
                }
            }
        else:
            return {
                "success": False,
                "error": "No email generated"
            }
            
    except Exception as e:
        print(f"❌ Email generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PRODUCTION Server with real backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
