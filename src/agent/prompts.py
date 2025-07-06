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
"""

COLD_EMAIL_PROMPT = """
You are an expert sales professional tasked with creating a personalized cold email based on comprehensive company research.

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

Create a personalized cold email that:

1. **Opens with a specific insight** from the research that shows you've done your homework
2. **Identifies a relevant pain point or opportunity** based on their current marketing/SEO/UX situation
3. **Positions your service** as a solution without being pushy
4. **Includes specific details** from their online presence, SEO performance, or user experience analysis
5. **Has a clear, soft call-to-action** that matches the requested CTA type

Email Guidelines:
- Use the specified tone ({email_tone})
- Keep to the requested length ({email_length})
- Reference specific findings from the research
- Avoid generic language
- Make it feel like a genuine, researched outreach
- Include a compelling subject line

Focus especially on insights from:
- Their online marketing presence and gaps
- SEO performance and opportunities  
- Website user experience issues or strengths
- Competitive positioning insights

Generate both a **Subject Line** and the **Email Body**.
"""
