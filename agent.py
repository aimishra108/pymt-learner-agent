import os
import logging
import asyncio
import google.cloud.logging
from typing import Dict, Any
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# --- 1. SETUP & LOGGING ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.0-flash")

# --- 2. CUSTOM TOOLS (BFSI SPECIFIC) ---

def save_user_query(tool_context: ToolContext, query: str) -> Dict[str, str]:
    """Saves the user's specific payment question to the shared state."""
    tool_context.state["USER_QUERY"] = query
    logging.info(f"[State] Query Saved: {query}")
    return {"status": "success"}

def get_internal_bank_specs(tool_context: ToolContext, rail: str) -> str:
    """Mocks an internal bank DB lookup for UK & SEPA rail limits."""
    specs = {
        "FPS": "UK Faster Payments: £1M limit, Instant, 24/7. Uses ISO 20022 (UK).",
        "BACS": "UK BACS: No limit, 3-day cycle (Input/Process/Settle). Legacy Std 18.",
        "CHAPS": "UK CHAPS: Unlimited, High-value, Same-day (Cut-off 15:00). ISO 20022.",
        "SEPA": "SEPA Credit Transfer: EUR only, Next-day. SEPA Instant: 10s SLA, €100k limit."
    }
    return specs.get(rail.upper(), "Technical specs for this rail are not in the local DB.")

def get_sepa_reason_codes(tool_context: ToolContext, code: str) -> str:
    """Provides human-readable explanations for ISO 20022 pacs.002 Status Codes."""
    codes = {
        "ACSP": "Accepted Settlement In Progress: Money is moving.",
        "RJCT": "Rejected: Invalid IBAN, Insufficient Funds, or System Error.",
        "ACWC": "Accepted With Change: Fixed minor details like addresses.",
        "MS03": "Not Specified: Usually a system-level downtime at the receiving bank."
    }
    return codes.get(code.upper(), f"Reason code {code} not found in ISO directory.")

# Wikipedia Tool for general payment history/context
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# --- 3. AGENT DEFINITIONS ---

# Agent A: The Data Gatherer
payment_researcher = Agent(
    name="payment_researcher",
    model=model_name,
    description="Researches UK/SEPA rails via internal DB and Wikipedia.",
    instruction="""
    Identify the payment rail in { USER_QUERY }. 
    Combine 'get_internal_bank_specs' data with 'Wikipedia' context.
    Synthesize facts about speed, cost, and historical significance.
    """,
    tools=[get_internal_bank_specs, wikipedia_tool],
    output_key="raw_research"
)

# Agent B: The Message Architect (ISO 20022 / Legacy)
message_format_expert = Agent(
    name="message_format_expert",
    model=model_name,
    description="Provides XML snippets for pacs.008 and pacs.002.",
    instruction="""
    Based on { USER_QUERY } and { raw_research }:
    1. Provide a pacs.008 (Success) or Standard 18 snippet.
    2. If the user asks about errors/status, provide a pacs.002 snippet.
    3. Use 'get_sepa_reason_codes' to explain any status tags like <StsId> or <Staff>.
    4. Highlight specific tags like <IntrBkSttlmAmt> for SEPA or <Dbtr> for UK.
    """,
    tools=[get_sepa_reason_codes],
    output_key="format_data"
)

# Agent C: The Educator (Final Voice)
jargon_buster_tutor = Agent(
    name="jargon_buster_tutor",
    model=model_name,
    description="Friendly summary for beginners using analogies.",
    instruction="""
    Synthesize RAW_RESEARCH and FORMAT_DATA into a cohesive lesson.
    - Use analogies (e.g., 'BACS is a freight train').
    - Explain 'The Why': why do we use XML instead of simple text?
    - Create a small 'Glossary' at the end for any technical terms used.
    
    RAW_RESEARCH: { raw_research }
    FORMAT_DATA: { format_data }
    """
)

# --- 4. WORKFLOW & ROOT ORCHESTRATION ---

tutor_workflow = SequentialAgent(
    name="tutor_workflow",
    description="Sequential processing: Research -> Format -> Explanation.",
    sub_agents=[payment_researcher, message_format_expert, jargon_buster_tutor]
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="Entry point for the Payments Tutor.",
    instruction="""
    Greet the user as a new BFSI engineering hire. 
    Ask what UK or SEPA payment rail they need to learn about.
    Once they ask, use 'save_user_query' and transfer to 'tutor_workflow'.
    """,
    tools=[save_user_query],
    sub_agents=[tutor_workflow]
)

# --- 5. INTERACTIVE EXECUTION LOOP ---

async def main():
    print("--- 🎓 2026 UK/EU Payments Agent (ADK) ---")
    print("Supports: BACS, FPS, CHAPS, SEPA (SCT & SCT Inst)")
    
    while True:
        user_input = input("\nYou (Type 'exit' to quit): ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break

        print("\n[Agents are collaborating...]\n")
        try:
            # Running the root agent starts the full sequence
            response = await root_agent.run(user_input)
            
            # Print the final output from the last agent in the chain
            if response and response.content.parts:
                print(f"Tutor: {response.content.parts[0].text}")
            else:
                print("Tutor: I've processed that, but I have no text output to show.")
                
        except Exception as e:
            logging.error(f"Execution Error: {e}")
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())