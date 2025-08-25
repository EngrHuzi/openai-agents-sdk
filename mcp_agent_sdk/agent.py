import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStreamableHttpParams,MCPServerStreamableHttp,create_static_tool_filter,ToolFilterContext
import asyncio
_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

#dynamcic tool filter
def tool_filter(context:ToolFilterContext,tool):
    return tool.name.startswith("get_weather")

async def main():
    params_server=MCPServerStreamableHttpParams(url="http://localhost:8000/mcp")
    tool_filter=create_static_tool_filter(allowed_tool_names="get_weather",blocked_tool_names="")
    async with MCPServerStreamableHttp(params_server,tool_filter=tool_filter,tool_filter=tool_filter,cache_tools_list=True) as server:

        agent=Agent(
            name="Weather_agent",
            instructions="You are a weather agent that can answer questions about the weather.",
            model=llm_model,
            mcp_servers=[server]
        )

        res= await  Runner.run(agent,input="What is weather in lahore?")
        print(res)

if __name__=="__main__":
    asyncio.run(main())
