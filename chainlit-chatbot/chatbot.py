import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.tool import function_tool
from tavily import TavilyClient
from datetime import datetime
from instructions import search_agent_prompt,supervisor_prompt


load_dotenv()

# Initialize API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
search_api_key = os.getenv("SEARCH_API_KEY")
if not gemini_api_key or not search_api_key:
    raise ValueError("API keys are not set. Please ensure they are defined in your .env file.")

# Initialize external client and model
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Define browse_online tool
@function_tool
def browse_online(query: str):
    """Search online for the given query."""
    tavily_client = TavilyClient(api_key=search_api_key)
    response = tavily_client.search(query)
    return response

# Define get_current_datetime tool
@function_tool
def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Create search_agent
search_agent = Agent(
    name="Search Agent",
    instructions=search_agent_prompt,
    tools=[browse_online],
    model=model
)
# Create supervisor_agent_with_datetime
supervisor_agent_with_datetime = Agent(
    name="Supervisor Agent with Datetime",
    instructions=supervisor_prompt,
    model=model,
    tools=[
        get_current_datetime,
        search_agent.as_tool(tool_name="search_agent", tool_description="Specialized in Searching and Browsing")
    ]
)

# Define RunConfig
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Chainlit handlers
@cl.on_chat_start
async def start():
    # Set up the chat session
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("agent", supervisor_agent_with_datetime)
    # Send welcome message
    await cl.Message(content="Welcome to the Alexa AI Assistant! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # Send an empty message to initiate streaming
    msg = cl.Message(content="")
    await msg.send()
    
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})
    
    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(starting_agent=agent, input=history, run_config=config)
        response_content = result.final_output
        
        # Simulate streaming by sending tokens one by one
        for token in response_content.split():
            await msg.stream_token(token + " ")
        await msg.update()
        
        # Update the chat history with the assistant's response
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)
        
        # Log the interaction
        print(f"User: {message.content}")
        print(f"{response_content}")
    except Exception as e:
        await msg.stream_token(f"\nError: {str(e)}")
        await msg.update()
        print(f"Error: {str(e)}")