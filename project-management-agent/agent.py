import asyncio

from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    handoff,

)
from agents.model_settings import ModelSettings
from config import model
from gaurdrail_check import (
    greeting_input_guardrail,
    greeting_output_guardrail,
    user_preference_input_guardrail,
    user_preference_output_guardrail,
    knowledge_graph_input_guardrail,
    knowledge_graph_output_guardrail,
    project_management_input_guardrail,
    project_management_output_guardrail,

)

# MCP Server
from agents.mcp import MCPServerStreamableHttpParams, MCPServerStreamableHttp
# Instructions
from instructions import (
    greeting_agent_instructions,
    user_preference_agent_instructions,
    knowledge_graph_agent_instructions,
    project_management_agent_instructions,
    orchestration_agent_instructions,
)

set_tracing_disabled(True)



# =========================================
# MAIN ENTRY POINT
# =========================================
async def main():
    # Configure MCP server with response transformation
    params_server = MCPServerStreamableHttpParams(
        url="http://localhost:8000/mcp"
    )
    async with MCPServerStreamableHttp(params_server,cache_tools_list=True) as server:


        greeting_agent = Agent(
            name="Greeting Agent",
            instructions=greeting_agent_instructions,
            model=model,
            input_guardrails=[greeting_input_guardrail],
            output_guardrails=[greeting_output_guardrail],
        )
        

        user_preference_agent = Agent(
            name="User Preference Agent",
            instructions=user_preference_agent_instructions,
            model=model,
            input_guardrails=[user_preference_input_guardrail],
            output_guardrails=[user_preference_output_guardrail],
        )

        

        knowledge_graph_agent = Agent(
            name="Knowledge Graph Agent",
            instructions=knowledge_graph_agent_instructions,
            model=model,
            input_guardrails=[knowledge_graph_input_guardrail],
            output_guardrails=[knowledge_graph_output_guardrail],
        )

        

        project_management_agent = Agent(
            name="Project Management Agent",
            instructions=project_management_agent_instructions,
            model=model,
            input_guardrails=[project_management_input_guardrail],
            output_guardrails=[project_management_output_guardrail],
            mcp_servers=[server],   # ✅ Included MCP server
            model_settings=ModelSettings(tool_choice="auto"),
        )

        # ---------------------------
        # ORCHESTRATION AGENT
        # ---------------------------
        orchestration_agent = Agent(
            name="Front-End Orchestration Agent",
            instructions=orchestration_agent_instructions,
            handoffs=[
                greeting_agent,
                user_preference_agent,
                project_management_agent,
                knowledge_graph_agent,
            ],
            model=model,
        )
        

        orchestration_res = await Runner.run(
            orchestration_agent,
            "create a new task for the project 'Project X' with the title 'Task Y' and the description 'Task Z' and the assignee 'John Doe' and the due date '2025-10-17'"  
        )
        print("Orchestration Agent:", orchestration_res.to_input_list())
        print(orchestration_res.final_output)


# =========================================
# RUN SCRIPT
# =========================================
if __name__=="__main__":
    asyncio.run(main())
