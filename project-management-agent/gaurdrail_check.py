        
from typing import List
from config import model
from pydantic import BaseModel, Field
from agents import Agent, Runner, TResponseInputItem,input_guardrail, output_guardrail, RunContextWrapper, GuardrailFunctionOutput

class GreetingInputCheckOutput(BaseModel):
                is_complex_request: bool
                reasoning: str

greeting_input_guardrail_agent = Agent(
            name="Greeting Input Guardrail Agent",
            instructions="""
            Determine if the user is asking about technical, project management, or complex work-related topics.
            If the message is just a greeting or small talk, set is_complex_request = False.
            If it contains technical or project-related content, set is_complex_request = True.
            """,
            output_type=GreetingInputCheckOutput,
            model=model,
        )

@input_guardrail
async def greeting_input_guardrail(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | List[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(greeting_input_guardrail_agent, input, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=result.final_output.is_off_topic,
            )

class GreetingOutput(BaseModel):
    response: str = Field(description="The friendly greeting message.")
    is_greeting: bool = Field(description="True if this is a greeting or small talk.")
class GreetingOutputCheck(BaseModel):
    is_off_topic: bool
    reasoning: str
greeting_output_guardrail_agent = Agent(
            name="Greeting Output Guardrail Agent",
            instructions="""
            Check if the agent's response goes beyond greetings and small talk.
            """,
            output_type=GreetingOutputCheck,
            model=model,
        )

@output_guardrail
async def greeting_output_guardrail(
            ctx: RunContextWrapper,
            agent: Agent,
            output: GreetingOutput,
        ) -> GuardrailFunctionOutput:
            # Support being passed either a ProjectManagementOutput object or a raw string
            if isinstance(output, str):
                text = output
            else:
                # If it's a Pydantic model or similar, try to read `.response`, fall back to str()
                text = getattr(output, "response", None) or str(output)

            result = await Runner.run(greeting_output_guardrail_agent, text, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=getattr(result.final_output, "is_off_topic", False),
            )

class PreferenceItem(BaseModel):
            key: str
            value: str

class PreferenceOutput(BaseModel):
            status: str
            preferences: List[PreferenceItem]
            message: str

class PreferenceInputCheckOutput(BaseModel):
            is_off_topic: bool
            reasoning: str

user_preference_input_guardrail_agent = Agent(
            name="User Preference Input Guardrail Agent",
            instructions="Determine if the user message is about preferences/settings.",
            output_type=PreferenceInputCheckOutput,
            model=model,
        )

@input_guardrail
async def user_preference_input_guardrail(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | List[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(user_preference_input_guardrail_agent, input, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=result.final_output.is_off_topic,
            )

class PreferenceOutputCheck(BaseModel):
            is_off_topic: bool
            reasoning: str

user_preference_output_guardrail_agent = Agent(
            name="User Preference Output Guardrail Agent",
            instructions="Check if the response is strictly preference-related.",
            output_type=PreferenceOutputCheck,
            model=model,
        )

@output_guardrail
async def user_preference_output_guardrail(
            ctx: RunContextWrapper,
            agent: Agent,
            output: PreferenceOutput,
        ) -> GuardrailFunctionOutput:
            # Support being passed either a ProjectManagementOutput object or a raw string
            if isinstance(output, str):
                text = output
            else:
                # If it's a Pydantic model or similar, try to read `.response`, fall back to str()
                text = getattr(output, "response", None) or str(output)
                
            result = await Runner.run(user_preference_output_guardrail_agent, text, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=getattr(result.final_output, "is_off_topic", False),
            )

# ---------------------------
        # KNOWLEDGE GRAPH AGENT
        # ---------------------------
class KnowledgeGraphRelationship(BaseModel):
            source_node: str
            target_node: str
            relationship_type: str

class KnowledgeGraphOutput(BaseModel):
            query_topic: str
            relationships: List[KnowledgeGraphRelationship]
            summary: str

class KnowledgeGraphInputCheck(BaseModel):
            is_off_topic: bool
            reasoning: str

knowledge_graph_input_guardrail_agent = Agent(
            name="Knowledge Graph Input Guardrail Agent",
            instructions="Classify whether the query is related to knowledge graph.",
            output_type=KnowledgeGraphInputCheck,
            model=model,
        )

@input_guardrail
async def knowledge_graph_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | List[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(knowledge_graph_input_guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


class KnowledgeGraphOutput(BaseModel):
    summary: str


class KnowledgeGraphOutputCheck(BaseModel):
    is_off_topic: bool
    reasoning: str


knowledge_graph_output_guardrail_agent = Agent(
    name="Knowledge Graph Output Guardrail Agent",
    instructions="Check if response is knowledge graph related.",
    output_type=KnowledgeGraphOutputCheck,
    model=model,
)


@output_guardrail
async def knowledge_graph_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: KnowledgeGraphOutput | str,
) -> GuardrailFunctionOutput:
    # Support being passed either a KnowledgeGraphOutput object or a raw string
    if isinstance(output, str):
        text = output
    else:
        # If it's a Pydantic model or similar, try to read `.summary`, fall back to str()
        text = getattr(output, "summary", None) or str(output)

    result = await Runner.run(knowledge_graph_output_guardrail_agent, text, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=getattr(result.final_output, "is_off_topic", False),
    )


class ProjectManagementInputCheck(BaseModel):
            is_off_topic: bool
            reasoning: str

project_management_input_guardrail_agent = Agent(
            name="Project Management Input Guardrail Agent",
            instructions="Check if the query is project management related.",
            output_type=ProjectManagementInputCheck,
            model=model,
        )

@input_guardrail
async def project_management_input_guardrail(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | List[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(project_management_input_guardrail_agent, input, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=result.final_output.is_off_topic,
            )

class ProjectManagementOutput(BaseModel):
            response: str

class ProjectManagementOutputCheck(BaseModel):
            is_off_topic: bool
            reasoning: str

project_management_output_guardrail_agent = Agent(
            name="Project Management Output Guardrail Agent",
            instructions="Check if response is strictly project management related.",
            output_type=ProjectManagementOutputCheck,
            model=model,
        )

@output_guardrail
async def project_management_output_guardrail(
            ctx: RunContextWrapper,
            agent: Agent,
            output: ProjectManagementOutput | str,
        ) -> GuardrailFunctionOutput:
            # Support being passed either a ProjectManagementOutput object or a raw string
            if isinstance(output, str):
                text = output
            else:
                # If it's a Pydantic model or similar, try to read `.response`, fall back to str()
                text = getattr(output, "response", None) or str(output)

            result = await Runner.run(project_management_output_guardrail_agent, text, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=getattr(result.final_output, "is_off_topic", False),
            )

