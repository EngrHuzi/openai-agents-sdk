from dotenv import load_dotenv
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, GuardrailFunctionOutput,set_tracing_disabled,input_guardrail,output_guardrail, TResponseInputItem,Runner, RunContextWrapper
from instructions import mood_tracking_instructions,meditation_instructions,journaling_instructions,crisis_detection_instructions,supervisor_instructions
from pydantic import BaseModel
from typing import List
import chainlit as cl


set_tracing_disabled(True)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)


# Input guardrail for Mood Tracking
class MoodSafetyCheckOutput(BaseModel):
    is_inappropriate_request: bool
    reasoning: str

mood_input_guardrail_agent = Agent(
    name="Mood Input Guardrail",
    instructions=(
        "Check if the user's input is appropriate for mood tracking. "
        "If the input is violent, abusive, or irrelevant (e.g., spam), flag it. "
        "Otherwise, allow it."
    ),
    output_type=MoodSafetyCheckOutput,
    model=model
)

@input_guardrail
async def mood_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(mood_input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate_request
    )

# Output guardrail for Mood Tracking
class MoodOutputValidation(BaseModel):
    is_harmful_response: bool
    reasoning: str

mood_output_guardrail_agent = Agent(
    name="Mood Output Guardrail",
    instructions=(
        "Analyze the agent's response for harmful, unsafe, or unethical advice. "
        "For example, advice that encourages self-harm is harmful. "
        "Return a boolean and reasoning."
    ),
    output_type=MoodOutputValidation,
    model=model
)

@output_guardrail
async def mood_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(mood_output_guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_harmful_response
        )



mood_tracking_agent = Agent(
    name="mood_tracking_agent",
    instructions=mood_tracking_instructions,
    model=model,
    input_guardrails=[mood_input_guardrail],
    output_guardrails=[mood_output_guardrail]

)



# Input guardrail for Journaling
class JournalSafetyCheckOutput(BaseModel):
    is_inappropriate_request: bool
    reasoning: str

journal_input_guardrail_agent = Agent(
    name="Journal Input Guardrail",
    instructions=(
        "Check if the user's input is appropriate for journaling. "
        "If the input is violent, abusive, or irrelevant (e.g., spam), flag it. "
        "Otherwise, allow it."
    ),
    output_type=JournalSafetyCheckOutput,
    model=model
)

@input_guardrail
async def journal_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(journal_input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate_request
    )

# Output guardrail for Journaling
class JournalOutputValidation(BaseModel):
    is_harmful_response: bool
    reasoning: str

journal_output_guardrail_agent = Agent(
    name="Journal Output Guardrail",
    instructions=(
        "Analyze the agent's response for harmful, unsafe, or unethical advice. "
        "For example, advice that encourages self-harm is harmful. "
        "Return a boolean and reasoning."
    ),
    output_type=JournalOutputValidation,
    model=model
)

@output_guardrail
async def journal_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(journal_output_guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_harmful_response
        )

journal_agent = Agent(
    name="journal_agent",
    instructions=journaling_instructions ,
    model=model,
    input_guardrails=[journal_input_guardrail],
    output_guardrails=[journal_output_guardrail]
)



# Input guardrail for Meditation
class MeditationSafetyCheckOutput(BaseModel):
    is_inappropriate_request: bool
    reasoning: str

meditation_input_guardrail_agent = Agent(
    name="Meditation Input Guardrail",
    instructions=(
        "Check if the user's input is appropriate for meditation guidance. "
        "If the input is violent, abusive, or irrelevant (e.g., spam), flag it. "
        "Otherwise, allow it."
    ),
    output_type=MeditationSafetyCheckOutput,
    model=model
)

@input_guardrail
async def meditation_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(meditation_input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate_request
    )


# Output guardrail for Meditation
class MeditationOutputValidation(BaseModel):
    is_harmful_response: bool
    reasoning: str

meditation_output_guardrail_agent = Agent(
    name="Meditation Output Guardrail",
    instructions=(
        "Analyze the agent's response for harmful, unsafe, or unethical advice. "
        "For example, advice that encourages self-harm is harmful. "
        "Return a boolean and reasoning."
    ),
    output_type=MeditationOutputValidation,
    model=model
)

@output_guardrail
async def meditation_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(meditation_output_guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_harmful_response
        )

meditation_agent = Agent(
    name="meditation_agent",
    instructions=meditation_instructions,
    model=model,
    input_guardrails=[meditation_input_guardrail],
    output_guardrails=[meditation_output_guardrail]
)



# Input guardrail for Crisis Detection
class CrisisSafetyCheckOutput(BaseModel):
    is_inappropriate_request: bool
    reasoning: str

crisis_input_guardrail_agent = Agent(
    name="Crisis Input Guardrail",
    instructions=(
        "Check if the user's input is appropriate for crisis detection. "
        "If the input is violent, abusive, or irrelevant (e.g., spam), flag it. "
        "Otherwise, allow it."
    ),
    output_type=CrisisSafetyCheckOutput,
    model=model
)

@input_guardrail
async def crisis_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(crisis_input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate_request
    )

# Output guardrail for Crisis Detection
class CrisisOutputValidation(BaseModel):
    is_harmful_response: bool
    reasoning: str

crisis_output_guardrail_agent = Agent(
    name="Crisis Output Guardrail",
    instructions=(
        "Analyze the agent's response for harmful, unsafe, or unethical advice. "
        "For example, advice that encourages self-harm is harmful. "
        "Return a boolean and reasoning."
    ),
    output_type=CrisisOutputValidation,
    model=model
)

@output_guardrail
async def crisis_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(crisis_output_guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_harmful_response
        )

crisis_agent = Agent(
    name="crisis_agent",
    instructions=crisis_detection_instructions ,
    model=model,
    input_guardrails=[crisis_input_guardrail],
    output_guardrails=[crisis_output_guardrail]
)



# Input guardrail for Supervisor Agent
class SupervisorSafetyCheckOutput(BaseModel):
    is_inappropriate_request: bool
    reasoning: str

supervisor_input_guardrail_agent = Agent(
    name="Supervisor Input Guardrail",
    instructions=(
        "Check if the user's input is appropriate for the supervisor agent. "
        "If the input is violent, abusive, or irrelevant (e.g., spam), flag it. "
        "Otherwise, allow it."
    ),
    output_type=SupervisorSafetyCheckOutput,
    model=model
)

@input_guardrail
async def supervisor_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(supervisor_input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate_request
    )

# Output guardrail for Supervisor Agent
class SupervisorOutputValidation(BaseModel):
    is_harmful_response: bool
    reasoning: str

supervisor_output_guardrail_agent = Agent(
    name="Supervisor Output Guardrail",
    instructions=(
        "Analyze the agent's response for harmful, unsafe, or unethical advice. "
        "For example, advice that encourages self-harm is harmful. "
        "Return a boolean and reasoning."
    ),
    output_type=SupervisorOutputValidation,
    model=model
)

@output_guardrail
async def supervisor_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(supervisor_output_guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_harmful_response
        )

supervisor_agent = Agent(
    name="Supervisor Agent",
    instructions=supervisor_instructions,
    model=model,
    handoffs=[mood_tracking_agent, journal_agent, meditation_agent, crisis_agent],
    input_guardrails=[supervisor_input_guardrail],
    output_guardrails=[supervisor_output_guardrail]

)


@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    cl.user_session.set("agent", supervisor_agent)
    await cl.Message(content="Welcome to the Mental Health Support Assistant! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    agent = cl.user_session.get("agent")
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        # Call the agent synchronously with the full history
        result = Runner.run_sync(starting_agent=agent, input=history)
        # Extract the response string from the output model
        response_content = getattr(result.final_output, 'response', str(result.final_output))

        # Simulate streaming by sending tokens one by one
        for token in response_content.split():
            await msg.stream_token(token + " ")
        await msg.update()

        # Update the chat history with the assistant's response
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)
    except Exception as e:
        await msg.stream_token(f"\nError: {str(e)}")
        await msg.update()