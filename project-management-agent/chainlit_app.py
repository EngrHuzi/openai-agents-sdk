import asyncio
import chainlit as cl
from typing import AsyncIterator, List

from config import model
from agents import Runner
from agents.mcp import MCPServerStreamableHttpParams, MCPServerStreamableHttp
from agent import create_orchestration_agent

@cl.on_chat_start
async def on_chat_start():
    starters = [
        cl.Starter(
            label="Create a new task",
            message="Create a new task for project 'Project X' titled 'Landing Page' assigned to 'Alex' due tomorrow."
        ),
        cl.Starter(
            label="Daily summary",
            message="Generate a daily summary for project 'Project X'."
        ),
        cl.Starter(
            label="Reschedule meeting",
            message="Reschedule meeting MTG-42 to 3pm tomorrow."
        ),
    ]
    await cl.set_starters(starters)

    # ✅ Connect to MCP Server on port 9000
    params_server = MCPServerStreamableHttpParams(url="http://localhost:9000/mcp")
    server = MCPServerStreamableHttp(params_server, cache_tools_list=True)
    await server.__aenter__()
    cl.user_session.set("mcp_server", server)

    orchestration_agent = create_orchestration_agent(server, model)
    cl.user_session.set("orchestration_agent", orchestration_agent)

    await cl.Message(content="Hi! I'm ready to help with project management.").send()

@cl.on_message
async def on_message(message: cl.Message):
    server: MCPServerStreamableHttp = cl.user_session.get("mcp_server")
    orchestration_agent = cl.user_session.get("orchestration_agent")

    if not orchestration_agent:
        await cl.Message(content="Agent not initialized.").send()
        return

    msg = cl.Message(content="")
    await msg.send()

    result = await Runner.run(orchestration_agent, message.content)
    final_text = getattr(result, "final_output", None)

    if final_text:
        for i in range(0, len(final_text), 120):
            await msg.stream_token(final_text[i:i+120])
            await asyncio.sleep(0)
        await msg.update()
    else:
        msg.content = str(result)
        await msg.update()

