# src/agent/prompts.py - Erweitert mit Meta Ad Analysis Prompt

INFO_PROMPT = """
You are tasked with synthesizing detailed company information from scraped website content about a company, {company}. Your research should focus on extracting pricing and feature information based on the provided schema.

Schema for Extraction:
<schema>
{info}
</schema>

Scraped Website Content:
<Website contents>
{content}
</Website contents>

Additional User Notes:
<user_notes>
{user_notes}
</user_notes>

Your output should include:
1. A well-organized summary of key pricing and feature details.
2. Specific figures, and other relevant details, where available.
3. Clear notes aligned with the provided schema, without attempting to mimic its format.
4. Indications of any important data that appears missing or unclear.

Focus your notes on the topics and details described in the schema. Your output should be clear, concise, and maintain the integrity of the original content.
"""

REFLECTION_PROMPT = """You are a research analyst tasked with reviewing the quality and completeness of extracted company information.

Compare the extracted information with the required schema:

<Schema>
{schema}
</Schema>

Here is the extracted information:
<extracted_info>
{info}
</extracted_info>

Analyze if all required fields are present and sufficiently populated. Consider:
1. Are any required fields missing?
2. Are any fields incomplete or containing uncertain information?
3. Are there fields with placeholder values or "unknown" markers?
4. Is the Meta advertising intelligence comprehensive and actionable?
"""

# ⭐ NEU: Meta Ad Analysis Prompt
META_AD_ANALYSIS_PROMPT = """
You are a Meta advertising intelligence analyst tasked with analyzing and interpreting Meta (Facebook/Instagram) advertising data for strategic business insights.

Company Information:
<company_url>
{company_url}
</company_url>

Raw Meta Advertising Data:
<ad_data>
{ad_data}
</ad_data>

Additional Context:
<user_notes>
{user_notes}
</user_notes>

Your task is to analyze this advertising intelligence data and provide structured insights that will be valuable for:
1. **Competitive Analysis** - Understanding how this company uses Meta advertising
2. **Market Intelligence** - Identifying trends and strategies
3. **Opportunity Identification** - Finding gaps and optimization potential
4. **Strategic Recommendations** - Actionable insights for improvement

Focus your analysis on:

**Advertising Status Assessment:**
- Current advertising activity level on Meta platforms
- Consistency and sophistication of campaigns
- Investment level and commitment to Meta advertising

**Creative Strategy Analysis:**
- What messaging themes and creative approaches are they using?
- How sophisticated is their creative strategy?
- What formats and visual styles dominate?
- Are they A/B testing or optimizing creatives?

**Targeting Intelligence:**
- Who are they trying to reach (demographics, geography)?
- How sophisticated is their targeting strategy?
- Are they missing obvious target segments?

**Competitive Positioning:**
- How does their advertising compare to industry standards?
- What competitive advantages or disadvantages are evident?
- Where are the gaps in their strategy?

**Budget and Performance Indicators:**
- What does their spending pattern suggest about priorities?
- Evidence of optimization and performance management
- Sophistication of campaign management

**Strategic Opportunities:**
- Untapped markets or demographics
- Creative opportunities they're missing
- Budget optimization potential
- Seasonal or timing opportunities

Provide specific, actionable insights that could be used for:
- Competitive intelligence reports
- Marketing strategy development  
- Sales prospecting and cold outreach
- Partnership or collaboration opportunities

Be analytical but accessible - your insights should be valuable for both marketing professionals and business development teams.
"""

COLD_EMAIL_PROMPT = """
You are an expert sales professional tasked with creating a personalized cold email based on comprehensive company research including Meta advertising intelligence.

Company Research Data:
<company_data>
{company_data}
</company_data>

Email Configuration:
<email_config>
Sender Company: {sender_company}
Sender Name: {sender_name}
Sender Role: {sender_role}
Service Offering: {service_offering}
Email Tone: {email_tone}
Email Length: {email_length}
Call to Action: {call_to_action}
</email_config>

Additional Context:
<user_notes>
{user_notes}
</user_notes>

Create a personalized cold email that leverages BOTH website analysis AND Meta advertising intelligence:

**Opening Strategy:**
1. **Lead with specific advertising insight** - Reference their current Meta advertising approach
2. **Show research depth** - Mention specific campaigns, targeting, or creative strategies you observed
3. **Identify opportunity gaps** - Point to untapped potential in their advertising strategy

**Value Proposition Integration:**
4. **Connect insights to pain points** - Link what you discovered to business challenges
5. **Position your expertise** - Show how your service addresses their specific advertising gaps
6. **Use competitive intelligence** - Reference how they compare to market standards

**Personalization Elements from Research:**
- Their current advertising status and sophistication level
- Specific targeting or creative opportunities you identified
- Budget optimization potential
- Seasonal or market opportunities they're missing
- Competitive advantages or gaps you observed

**Email Structure:**
- **Subject Line:** Reference specific advertising insight or opportunity
- **Opening:** Specific observation about their Meta advertising strategy
- **Value Bridge:** Connect their current approach to improvement potential  
- **Social Proof:** How you've helped similar companies optimize their advertising
- **Soft CTA:** Invitation to discuss their advertising strategy

**Tone Guidelines:**
- Use the specified tone ({email_tone})
- Keep to the requested length ({email_length})
- Balance expertise with approachability
- Avoid sounding like you're stalking their ads - frame as professional competitive analysis
- Focus on opportunities, not criticisms

**Key Research Integration:**
- Reference specific findings from Meta ad intelligence
- Connect website analysis with advertising strategy
- Show understanding of their market positioning
- Demonstrate value through specific observations

Generate both a **Subject Line** and the **Email Body** that feels like genuine, research-driven business development.
"""