"""
LangChain and OpenAI integration for analyzing ToS changes.
Returns structured output: status, risk_level, and analysis.
"""
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


async def analyze_changes(previous_text: str, current_text: str, openai_api_key: str) -> dict:
    """
    Analyze the legal implications of ToS changes using GPT-4o-mini.

    Returns:
        A dict with keys: status, risk_level, analysis
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=openai_api_key,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a legal analyst specializing in Terms of Service agreements.
You will compare two versions of a Terms of Service document and produce a structured analysis.

You MUST respond with valid JSON only, no markdown fencing, no extra text. Use this exact schema:

{{
  "status": "CHANGED" or "UNCHANGED",
  "risk_level": "<LEVEL> (<Category>)",
  "analysis": "<detailed analysis text>"
}}

Rules for risk_level:
- Use one of: HIGH, MEDIUM, LOW, or NONE
- Include a parenthetical category from: Data Privacy, AI/ML Rights, Billing, User Rights, Dispute Resolution, Liability, General
- Examples: "HIGH (Data Privacy)", "MEDIUM (Billing)", "LOW (General)"

Rules for analysis:
- Identify the specific sections or clauses that changed
- Explain what the change means for users in plain language
- If risk is HIGH, explain why immediate review is needed
- Keep the analysis concise but thorough (2-5 sentences)

Focus especially on changes related to:
1. Data privacy and user data rights
2. AI training rights and data usage for machine learning
3. Billing, subscription, and payment terms
4. User rights and obligations
5. Dispute resolution and arbitration clauses"""),
        ("human", """Analyze the legal implications of these Terms of Service changes.

PREVIOUS VERSION:
{previous_text}

CURRENT VERSION:
{current_text}

Respond with JSON only.""")
    ])

    formatted_prompt = prompt.format_messages(
        previous_text=previous_text[:15000],
        current_text=current_text[:15000],
    )

    response = await llm.ainvoke(formatted_prompt)

    # Parse the JSON response
    content = response.content.strip()
    # Strip markdown code fences if the model adds them despite instructions
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3].strip()

    result = json.loads(content)

    # Validate required keys with defaults
    return {
        "status": result.get("status", "CHANGED"),
        "risk_level": result.get("risk_level", "UNKNOWN"),
        "analysis": result.get("analysis", "Analysis unavailable."),
    }
