import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff,set_tracing_disabled,input_guardrail,output_guardrail,GuardrailFunctionOutput,RunContextWrapper,TResponseInputItem,OutputGuardrailTripwireTriggered
from agents.tool import function_tool
from tavily import TavilyClient
from pydantic import BaseModel
from instructions import plan_trip_instructions,budget_created_instructions,set_reminder_instructions,weather_instructions,smart_supervisor_instructions
import chainlit as cl

set_tracing_disabled(True)


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


set_tracing_disabled(True)


class TravelSafetyCheckOutput(BaseModel):
    is_unethical_or_illegal_request: bool
    reasoning: str

travel_guardrail_agent = Agent(
    name="Travel Guardrail",
    instructions=(
        "Determine if the user request involves illegal travel activity, such as crossing borders illegally, "
        "faking documents, or bypassing visa restrictions. Respond with reasoning."
    ),
    output_type=TravelSafetyCheckOutput,
    model=model # Ensure the model is used here as well
)

@input_guardrail
async def travel_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(travel_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_unethical_or_illegal_request,
    )

class TripOutput(BaseModel):
    response: str

class TripSafetyCheck(BaseModel):
    reasoning: str
    contains_illegal_or_unrealistic: bool

trip_guardrail_agent = Agent(
    name="Trip Output Guardrail",
    instructions="Check if the travel plan contains illegal, unsafe, or unrealistic recommendations. Provide reasoning.",
    output_type=TripSafetyCheck,
    model=model
)

@output_guardrail
async def trip_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: TripOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(trip_guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_illegal_or_unrealistic,
    )



from pydantic import BaseModel

class TripPlanOutput(BaseModel):
    response: str

plan_trip_agent=Agent(
    name="plan_trip_agent",
    instructions=plan_trip_instructions,
    model=model,
    input_guardrails=[travel_guardrail],
    output_guardrails=[trip_output_guardrail],
    output_type=TripPlanOutput
)


class FinanceSafetyCheckOutput(BaseModel):
    is_unethical_or_illegal_request: bool
    reasoning: str

finance_guardrail_agent = Agent(
    name="Finance Guardrail",
    instructions=(
        "Determine whether the user's request contains unethical or illegal financial content, such as tax fraud, "
        "loan evasion, or unrealistic get-rich-quick schemes. Provide a reasoned judgment."
    ),
    output_type=FinanceSafetyCheckOutput,
    model=model
)

@input_guardrail
async def finance_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(finance_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_unethical_or_illegal_request,
    )



class BudgetOutput(BaseModel):
    response: str

class BudgetSafetyCheck(BaseModel):
    reasoning: str
    contains_unethical_finance: bool

budget_guardrail_agent = Agent(
    name="Budget Output Guardrail",
    instructions="Check if the budget advice includes unethical, unsafe, or illegal financial strategies. Provide reasoning.",
    output_type=BudgetSafetyCheck,
    model=model
)

@output_guardrail
async def budget_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: BudgetOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(budget_guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_unethical_finance,
    )

budget_created_agent=Agent(
    name="budget_created_agent",
    instructions=budget_created_instructions,
    model=model,
    input_guardrails=[finance_guardrail],
    output_guardrails=[budget_output_guardrail],
    output_type=BudgetOutput
)


class ReminderCheckOutput(BaseModel):
    reasoning: str
    # is_malicious_or_concerning: bool # This was the old name, now using contains_harmful_reminder

reminder_guardrail_agent = Agent(
    name="Reminder Guardrail",
    instructions=(
        "Check if the reminder request is potentially harmful, threatening, or abusive — such as reminders for violent acts "
        "or unethical actions. Explain your reasoning."
    ),
    output_type=ReminderCheckOutput,
    model=model
)

@input_guardrail
async def reminder_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(reminder_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_harmful_reminder,
    )



class ReminderOutput(BaseModel):
    response: str

class ReminderSafetyCheck(BaseModel):
    reasoning: str
    contains_harmful_reminder: bool

reminder_guardrail_agent = Agent(
    name="Reminder Output Guardrail",
    instructions="Check if the reminder includes anything harmful, suspicious, or unethical. Provide reasoning.",
    output_type=ReminderSafetyCheck,
    model=model
)

@output_guardrail
async def reminder_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ReminderOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(reminder_guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_harmful_reminder,
    )

set_reminder_agent=Agent(
    name="set_reminder_agent",
    instructions=set_reminder_instructions,
    model=model,
    input_guardrails=[reminder_guardrail],
    output_guardrails=[reminder_output_guardrail],
    output_type=ReminderOutput
)

@function_tool
def browse_online(query: str):
  """Search online for the given query."""
  tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
  response = tavily_client.search(query)
  return response

weather_agent=Agent(
    name="weather_agent",
    instructions=weather_instructions,
    model=model,
    tools=[browse_online]
)



smart_supervisor_agent=Agent(
    name="smart_supervisor_agent",
    instructions=smart_supervisor_instructions,
    model=model,
    tools=[
        weather_agent.as_tool(
            tool_name="weather_agent",
            tool_description="Search online for the given query."
        )
    ],
    handoffs=[plan_trip_agent,set_reminder_agent,budget_created_agent]
)

# Chainlit handlers
@cl.on_chat_start
async def start():
    # Set up the chat session
    cl.user_session.set("chat_history", [])
    cl.user_session.set("agent", smart_supervisor_agent)
    # Send welcome message
    await cl.Message(content="Welcome to the Personal Finance & Travel Advisor! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # Send an empty message to initiate streaming
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
