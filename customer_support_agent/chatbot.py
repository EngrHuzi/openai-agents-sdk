import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff,set_tracing_disabled
from agents.tool import function_tool
from tavily import TavilyClient
from instructions import search_agent_prompt,billing_instruction,technical_instruction,supervisor_instruction

set_tracing_disabled(True)
# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate API keys
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in the .env file.")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set. Please ensure it is defined in the .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

@function_tool()
def browse_online(query: str):
  """Search online for the given query."""
  tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
  response = tavily_client.search(query)
  return response

search_agent = Agent(
    name="Search Agent",
    instructions=search_agent_prompt,
    tools=[browse_online],
    model=model
)


BILLING_AGENT = Agent(
    name="Billing Agent",
    instructions=billing_instruction,
    model=model
)

TECHNICAL_AGENT = Agent(
    name="Technical Agent",
    instructions=technical_instruction,
    model=model,
)

SUPERVISOR_AGENT=Agent(
    name="Supervisor Agent",
    instructions=supervisor_instruction,
    model=model,
    tools=[
        search_agent.as_tool(tool_name="search_agent",
                             tool_description="Specialized in Searching and Browsing on the Book"
                             )
     ],
    handoffs=[BILLING_AGENT, TECHNICAL_AGENT],
)

user_query=input("Enter your query: ")
response = Runner.run_sync(SUPERVISOR_AGENT, user_query)
print(f"**{response.last_agent.name}**:\n\n {response.final_output}")
response.to_input_list()


