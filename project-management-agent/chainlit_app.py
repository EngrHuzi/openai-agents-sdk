import asyncio
import chainlit as cl
from typing import Optional, List, Dict, Any

from config import model
from agents import Runner
from agents.mcp import MCPServerStreamableHttpParams, MCPServerStreamableHttp
from agent import create_orchestration_agent


# 🧭 1. Define your starter buttons
@cl.set_starters
async def set_starters(user: Optional[cl.User] = None) -> List[cl.Starter]:
    return [
        cl.Starter(
            label="➕ Create a new task",
            message="Create a new task for project 'Project X' titled 'Landing Page' assigned to 'Alex' due tomorrow.",
        ),
        cl.Starter(
            label="📅 Daily summary",
            message="Generate a daily summary for project 'Project X'.",
        ),
        cl.Starter(
            label="⏰ Reschedule meeting",
            message="Reschedule meeting MTG-42 to 3pm tomorrow.",
        ),
        cl.Starter(
            label="✅ Update task status",
            message="Mark the task 'Landing Page' in project 'Project X' as completed.",
        ),
        cl.Starter(
            label="👤 Assign team member",
            message="Assign 'Sarah' to the task 'Landing Page' in project 'Project X'.",
        ),
    ]


# 🧠 2. Initialize backend without sending any message
@cl.on_chat_start
async def on_chat_start():
    # Initialize MCP Server
    params_server = MCPServerStreamableHttpParams(
        url="http://localhost:9000/mcp"
    )
    server = MCPServerStreamableHttp(params_server, cache_tools_list=True)
    await server.__aenter__()
    cl.user_session.set("mcp_server", server)

    # Initialize orchestration agent
    orchestration_agent = create_orchestration_agent(server, model)
    cl.user_session.set("orchestration_agent", orchestration_agent)

    # ✅ No welcome message here (so starters stay visible)
    # If you want, you can delay or show a typing step
    # await asyncio.sleep(2)
    # await cl.Message(content="✅ Project Management Agent ready!").send()


# ♻️ 2b. Restore a previous thread from the sidebar
@cl.on_chat_resume
async def on_chat_resume(thread: Dict[str, Any]):
    # Ensure server and agent are available for resumed threads too
    if not cl.user_session.get("mcp_server"):
        params_server = MCPServerStreamableHttpParams(
            url="http://localhost:9000/mcp"
        )
        server = MCPServerStreamableHttp(params_server, cache_tools_list=True)
        await server.__aenter__()
        cl.user_session.set("mcp_server", server)

    if not cl.user_session.get("orchestration_agent"):
        server: MCPServerStreamableHttp = cl.user_session.get("mcp_server")
        orchestration_agent = create_orchestration_agent(server, model)
        cl.user_session.set("orchestration_agent", orchestration_agent)

    # Extract past steps to seed lightweight memory
    steps = thread.get("steps", []) or []
    memory: List[Dict[str, Any]] = []
    for step in steps:
        role = "assistant" if step.get("author") == "assistant" else "user"
        content = step.get("output", step.get("content", "")) or ""
        if content:
            memory.append({"role": role, "content": content})
    cl.user_session.set("thread_memory", memory)

    # Optional: small notice on resume
    await cl.Message(content="🔁 Resumed previous conversation. Context restored.").send()

# 💬 3. Handle user input or starter clicks
@cl.on_message
async def on_message(message: cl.Message):
    server: MCPServerStreamableHttp = cl.user_session.get("mcp_server")
    orchestration_agent = cl.user_session.get("orchestration_agent")

    if not orchestration_agent:
        await cl.Message(content="⚠️ Agent not initialized.").send()
        return

    # Initialize/append to per-thread memory
    thread_memory: List[Dict[str, Any]] = cl.user_session.get("thread_memory") or []
    thread_memory.append({"role": "user", "content": message.content})
    cl.user_session.set("thread_memory", thread_memory)

    msg = cl.Message(content="")
    await msg.send()

    # If your orchestration supports passing memory/context, do it here
    # Fallback: just pass the latest user message
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

    # Store assistant response in memory
    assistant_text = final_text if final_text else msg.content
    thread_memory = cl.user_session.get("thread_memory") or []
    if assistant_text:
        thread_memory.append({"role": "assistant", "content": assistant_text})
        cl.user_session.set("thread_memory", thread_memory)
