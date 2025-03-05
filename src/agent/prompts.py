INFO_PROMPT = """
You are tasked with synthesizing detailed pricing information from scraped website content about a company, {company}. Your research should focus on extracting pricing and feature information based on the provided schema.

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
