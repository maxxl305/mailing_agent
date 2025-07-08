# src/agent/debug_utils.py - Data Quality Debugging Helper

import json
from typing import Dict, Any, List
from datetime import datetime

def analyze_data_quality(company_data: Dict[str, Any], meta_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze the quality of extracted company data.
    
    Args:
        company_data: Website analysis data
        meta_data: Meta advertising intelligence data
    
    Returns:
        Dictionary with quality assessment
    """
    
    quality_report = {
        "timestamp": datetime.now().isoformat(),
        "website_analysis": {},
        "meta_ad_intelligence": {},
        "overall_score": 0,
        "email_readiness": False,
        "missing_fields": [],
        "recommendations": []
    }
    
    # ===== WEBSITE ANALYSIS QUALITY =====
    website_score = 0
    max_website_score = 100
    
    # Core company information (30 points)
    if company_data.get('company_name'):
        website_score += 10
    else:
        quality_report["missing_fields"].append("company_name")
    
    if company_data.get('unique_selling_proposition'):
        website_score += 10
    else:
        quality_report["missing_fields"].append("unique_selling_proposition")
    
    if company_data.get('brand_mission_vision'):
        website_score += 10
    else:
        quality_report["missing_fields"].append("brand_mission_vision")
    
    # Marketing presence (25 points)
    online_presence = company_data.get('online_marketing_presence', {})
    if online_presence.get('social_media_channels'):
        website_score += 10
    if online_presence.get('digital_advertising'):
        website_score += 10
    if online_presence.get('content_marketing'):
        website_score += 5
    
    # SEO & UX (25 points)
    seo_data = company_data.get('seo_performance', {})
    if seo_data.get('technical_seo'):
        website_score += 10
    if seo_data.get('content_optimization'):
        website_score += 5
    
    ux_data = company_data.get('website_user_experience', {})
    if ux_data.get('overall_ux_rating'):
        website_score += 10
    
    # Target audience & positioning (20 points)
    if company_data.get('target_audience_personas'):
        website_score += 10
    if company_data.get('competitive_landscape'):
        website_score += 10
    
    quality_report["website_analysis"] = {
        "score": website_score,
        "max_score": max_website_score,
        "percentage": round((website_score / max_website_score) * 100, 1),
        "grade": get_grade(website_score / max_website_score)
    }
    
    # ===== META AD INTELLIGENCE QUALITY =====
    meta_score = 0
    max_meta_score = 100
    
    if meta_data and meta_data.get('llm_analysis'):
        meta_analysis = meta_data['llm_analysis']
        
        # Advertising status (20 points)
        if meta_analysis.get('advertising_status') not in ['analysis_failed', 'no_ads_found']:
            meta_score += 20
        
        # Creative strategy (20 points)
        if meta_analysis.get('creative_strategy_analysis') and len(meta_analysis.get('creative_strategy_analysis', '')) > 10:
            meta_score += 20
        
        # Targeting insights (20 points)
        if meta_analysis.get('targeting_insights') and len(meta_analysis.get('targeting_insights', '')) > 10:
            meta_score += 20
        
        # Budget assessment (20 points)
        if meta_analysis.get('budget_assessment') and len(meta_analysis.get('budget_assessment', '')) > 10:
            meta_score += 20
        
        # Optimization opportunities (20 points)
        opportunities = meta_analysis.get('optimization_opportunities', [])
        if opportunities and len(opportunities) > 0:
            meta_score += 20
    
    quality_report["meta_ad_intelligence"] = {
        "score": meta_score,
        "max_score": max_meta_score,
        "percentage": round((meta_score / max_meta_score) * 100, 1),
        "grade": get_grade(meta_score / max_meta_score) if meta_score > 0 else "N/A"
    }
    
    # ===== OVERALL ASSESSMENT =====
    # Website is more important than Meta ads for basic functionality
    overall_score = (website_score * 0.7) + (meta_score * 0.3)
    max_overall_score = (max_website_score * 0.7) + (max_meta_score * 0.3)
    
    quality_report["overall_score"] = round((overall_score / max_overall_score) * 100, 1)
    quality_report["grade"] = get_grade(overall_score / max_overall_score)
    
    # ===== EMAIL READINESS =====
    # Email can be generated if we have basic company info and some marketing data
    has_basic_info = bool(company_data.get('company_name')) and (
        bool(company_data.get('unique_selling_proposition')) or 
        bool(company_data.get('brand_mission_vision'))
    )
    
    has_marketing_data = bool(online_presence) or bool(meta_data)
    
    quality_report["email_readiness"] = has_basic_info and has_marketing_data
    
    # ===== RECOMMENDATIONS =====
    if website_score < 60:
        quality_report["recommendations"].append("Website analysis needs improvement - consider re-crawling or different pages")
    
    if meta_score < 40 and meta_data:
        quality_report["recommendations"].append("Meta ad intelligence is limited - company may have minimal advertising presence")
    
    if not quality_report["email_readiness"]:
        quality_report["recommendations"].append("Not enough data for email generation - need more company information")
    
    if quality_report["overall_score"] > 70:
        quality_report["recommendations"].append("Data quality is excellent - ready for email generation")
    
    return quality_report


def get_grade(score_ratio: float) -> str:
    """Convert score ratio to letter grade."""
    if score_ratio >= 0.9:
        return "A"
    elif score_ratio >= 0.8:
        return "B"
    elif score_ratio >= 0.7:
        return "C"
    elif score_ratio >= 0.6:
        return "D"
    else:
        return "F"


def print_quality_report(report: Dict[str, Any], company_url: str = ""):
    """Print a formatted quality report."""
    print(f"\n📊 DATA QUALITY REPORT {f'for {company_url}' if company_url else ''}")
    print("=" * 60)
    
    # Overall score
    print(f"🎯 Overall Score: {report['overall_score']}% (Grade: {report['grade']})")
    
    # Website analysis
    website = report['website_analysis']
    print(f"\n🌐 Website Analysis: {website['score']}/{website['max_score']} ({website['percentage']}% - Grade: {website['grade']})")
    
    # Meta ad intelligence
    meta = report['meta_ad_intelligence']
    if meta['score'] > 0:
        print(f"📱 Meta Ad Intelligence: {meta['score']}/{meta['max_score']} ({meta['percentage']}% - Grade: {meta['grade']})")
    else:
        print(f"📱 Meta Ad Intelligence: Not available")
    
    # Email readiness
    email_status = "✅ Ready" if report['email_readiness'] else "❌ Not Ready"
    print(f"\n📧 Email Generation: {email_status}")
    
    # Missing fields
    if report['missing_fields']:
        print(f"\n❌ Missing Fields: {', '.join(report['missing_fields'])}")
    
    # Recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    print("=" * 60)


def debug_state_data(state, url: str):
    """Debug function to analyze state data quality."""
    print(f"\n🔍 DEBUGGING STATE DATA for {url}")
    print("=" * 50)
    
    # Check if data exists
    has_website_data = bool(state.info.get(url))
    has_meta_data = bool(getattr(state, 'meta_ad_intelligence', {}).get(url))
    
    print(f"📊 Data Presence:")
    print(f"   Website Data: {'✅' if has_website_data else '❌'}")
    print(f"   Meta Ad Data: {'✅' if has_meta_data else '❌'}")
    
    if has_website_data:
        website_data = state.info[url]
        print(f"\n🌐 Website Data Keys: {list(website_data.keys())}")
        
        # Check key fields
        key_fields = ['company_name', 'unique_selling_proposition', 'online_marketing_presence']
        for field in key_fields:
            value = website_data.get(field)
            status = "✅" if value else "❌"
            print(f"   {field}: {status}")
    
    if has_meta_data:
        meta_data = getattr(state, 'meta_ad_intelligence', {})[url]
        print(f"\n📱 Meta Ad Data Keys: {list(meta_data.keys())}")
        
        if 'llm_analysis' in meta_data:
            llm_analysis = meta_data['llm_analysis']
            print(f"   LLM Analysis Keys: {list(llm_analysis.keys())}")
            print(f"   Advertising Status: {llm_analysis.get('advertising_status', 'N/A')}")
    
    # Generate quality report
    if has_website_data:
        website_data = state.info[url]
        meta_data = getattr(state, 'meta_ad_intelligence', {}).get(url)
        
        quality_report = analyze_data_quality(website_data, meta_data)
        print_quality_report(quality_report, url)
    
    print("=" * 50)


# Example usage function
def test_quality_analysis():
    """Test the quality analysis with sample data."""
    
    # Sample good data
    good_data = {
        "company_name": "Test Company",
        "unique_selling_proposition": "We provide excellent services",
        "online_marketing_presence": {
            "social_media_channels": [{"platform": "LinkedIn", "activity_level": "active"}],
            "digital_advertising": ["Google Ads", "Facebook Ads"]
        },
        "seo_performance": {
            "technical_seo": ["Mobile optimization", "Fast loading"],
            "content_optimization": {"keyword_usage": "Good"}
        }
    }
    
    # Sample Meta data
    meta_data = {
        "llm_analysis": {
            "advertising_status": "active_advertiser",
            "creative_strategy_analysis": "Strong creative strategy with focus on benefits",
            "targeting_insights": "Targets professionals aged 25-45",
            "budget_assessment": "Medium budget allocation",
            "optimization_opportunities": ["Expand to new demographics", "Test video formats"]
        }
    }
    
    print("🧪 Testing Quality Analysis with Good Data:")
    quality_report = analyze_data_quality(good_data, meta_data)
    print_quality_report(quality_report, "https://test-company.com")
    
    # Sample poor data
    poor_data = {
        "company_name": "Test Company"
        # Missing most other fields
    }
    
    print("\n🧪 Testing Quality Analysis with Poor Data:")
    quality_report = analyze_data_quality(poor_data)
    print_quality_report(quality_report, "https://poor-company.com")


if __name__ == "__main__":
    test_quality_analysis()