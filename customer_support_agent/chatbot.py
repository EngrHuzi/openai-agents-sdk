import os
from typing import List, Dict, cast
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff
from agents.run import RunConfig

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate API key
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please ensure it is defined in the .env file."
    )

# Define specialist agents
BILLING_AGENT = Agent(
    name="Billing Agent",
    instructions="""You are a billing specialist assisting customers with payment-related inquiries.
    Handle issues such as billing disputes, subscription modifications, and refund requests.
    For inquiries about technical issues or account settings, clarify that your expertise is limited to billing and payment matters and offer to transfer to the appropriate specialist.""",
)

TECHNICAL_AGENT = Agent(
    name="Technical Agent",
    instructions="""You are a technical support specialist assisting with product-related issues.
    Provide solutions for troubleshooting, error messages, and how-to queries.
    Focus exclusively on resolving technical problems. For billing or payment inquiries, clarify that your expertise is limited to technical matters and offer to transfer to the appropriate specialist.""",
)

# Define triage agent for routing customer inquiries
TRIAGE_AGENT = Agent(
    name="Customer Service",
    instructions="""You are the initial customer service representative responsible for routing inquiries.
    Direct billing or payment-related questions to the Billing Agent.
    Direct technical or how-to questions to the Technical Agent.
    Answer general product inquiries directly, including questions about your role or purpose.
    When handing off, confirm with the user and ensure a courteous and seamless transition.""",
    handoffs=[BILLING_AGENT, handoff(TECHNICAL_AGENT)],
)

@cl.on_chat_start
async def initialize_session():
    """Initialize the session with the Gemini API client and default agent settings."""
    try:
        # Initialize external client for Gemini API
        external_client = AsyncOpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        # Configure the model
        model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash", openai_client=external_client
        )

        # Set run configuration
        config = RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True,
        )

        # Initialize session variables
        cl.user_session.set("agent", TRIAGE_AGENT)
        cl.user_session.set("config", config)
        cl.user_session.set("chat_history", [])
        cl.user_session.set("awaiting_handoff", None)  # Track handoff state
        cl.user_session.set("inquiry_type", None)  # Track inquiry type
    except Exception as e:
        raise RuntimeError(f"Failed to initialize session: {str(e)}")

@cl.on_message
async def process_message(message: cl.Message):
    """Handle incoming user messages, route to appropriate agents, and stream responses."""
    # Initialize streaming response
    response_message = cl.Message(content="")
    await response_message.send()

    # Retrieve session data
    current_agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    chat_history: List[Dict[str, str]] = cl.user_session.get("chat_history", [])
    awaiting_handoff: str | None = cl.user_session.get("awaiting_handoff")
    inquiry_type: str | None = cl.user_session.get("inquiry_type")

    # Append user message to chat history
    chat_history.append({"role": "user", "content": message.content})

    # Handle handoff confirmation
    if awaiting_handoff:
        if message.content.strip().lower() in ["yes", "proceed", "okay"]:
            # Confirm handoff to the appropriate agent
            target_agent = BILLING_AGENT if awaiting_handoff == "billing" else TECHNICAL_AGENT
            chat_history = chat_history[:-2] if len(chat_history) >= 2 else chat_history
            cl.user_session.set("agent", target_agent)
            cl.user_session.set("chat_history", chat_history)
            cl.user_session.set("awaiting_handoff", None)
            cl.user_session.set("inquiry_type", awaiting_handoff)  # Set inquiry type
            await response_message.stream_token(
                f"You have been transferred to our {target_agent.name}. They will assist you shortly."
            )
            await response_message.update()
            return
        else:
            # User declines handoff
            cl.user_session.set("awaiting_handoff", None)
            cl.user_session.set("inquiry_type", None)
            await response_message.stream_token(
                "Alright, how else may I assist you?"
            )
            await response_message.update()
            return

    # Detect inquiry type for routing
    message_lower = message.content.lower()

    # Handle inquiries when a specialist is active
    if current_agent.name == "Billing Agent":
        # Check if the message aligns with the billing context or contains explicit technical keywords
        if inquiry_type == "billing" and not any(
            keyword in message_lower for keyword in ["technical", "error", "bug", "problem", "crash"]
        ):
            # Treat as a continuation of the billing inquiry
            pass
        elif any(keyword in message_lower for keyword in ["technical", "error", "bug", "problem", "crash"]):
            # Redirect technical inquiry to Triage Agent
            cl.user_session.set("agent", TRIAGE_AGENT)
            cl.user_session.set("awaiting_handoff", "technical")
            cl.user_session.set("inquiry_type", None)
            await response_message.stream_token(
                "This sounds like a technical issue. I specialize in billing matters, so I’ll transfer you to our Customer Service team to connect you with a Technical Agent. Please confirm with 'yes' or 'proceed'."
            )
            await response_message.update()
            return
    elif current_agent.name == "Technical Agent":
        # Check if the message aligns with the technical context or contains explicit billing keywords
        if inquiry_type == "technical" and not any(
            keyword in message_lower for keyword in ["billing", "charge", "payment", "refund", "subscription"]
        ):
            # Treat as a continuation of the technical inquiry
            pass
        elif any(keyword in message_lower for keyword in ["billing", "charge", "payment", "refund", "subscription"]):
            # Redirect billing inquiry to Triage Agent
            cl.user_session.set("agent", TRIAGE_AGENT)
            cl.user_session.set("awaiting_handoff", "billing")
            cl.user_session.set("inquiry_type", None)
            await response_message.stream_token(
                "This sounds like a billing issue. I specialize in technical matters, so I’ll transfer you to our Customer Service team to connect you with a Billing Agent. Please confirm with 'yes' or 'proceed'."
            )
            await response_message.update()
            return

    # Triage logic for Customer Service agent
    if current_agent.name == "Customer Service":
        # Handle "about yourself" inquiries explicitly
        if any(keyword in message_lower for keyword in ["yourself", "about you", "who are you", "what are you"]):
            response_content = "I am a customer support agent to handle technical, billing, or general queries."
            for token in response_content.split():
                await response_message.stream_token(token + " ")
            await response_message.update()
            chat_history.append({"role": "assistant", "content": response_content})
            cl.user_session.set("chat_history", chat_history)
            print(f"User Input: {message.content}")
            print(f"Assistant Response: {response_content}")
            return

        # Route billing or technical inquiries
        if any(keyword in message_lower for keyword in ["billing", "charge", "payment", "refund", "subscription"]):
            # Prompt for handoff to Billing Agent
            cl.user_session.set("awaiting_handoff", "billing")
            await response_message.stream_token(
                "I’m sorry to hear about your billing issue. Would you like me to connect you with our Billing Agent to resolve this? (Please reply 'yes' or 'proceed')"
            )
            await response_message.update()
            return
        elif any(keyword in message_lower for keyword in ["technical", "error", "bug", "problem", "crash"]):
            # Prompt for handoff to Technical Agent
            cl.user_session.set("awaiting_handoff", "technical")
            await response_message.stream_token(
                "It sounds like a technical issue. Would you like me to connect you with our Technical Agent to assist? (Please reply 'yes' or 'proceed')"
            )
            await response_message.update()
            return

    try:
        # Execute agent with context and stream response
        result = Runner.run_sync(
            starting_agent=current_agent, input=chat_history, run_config=config
        )
        response_content = result.final_output

        # Stream response tokens
        for token in response_content.split():
            await response_message.stream_token(token + " ")
        await response_message.update()

        # Update chat history with assistant response
        chat_history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", chat_history)

        # Log interaction for debugging
        print(f"User Input: {message.content}")
        print(f"Assistant Response: {response_content}")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await response_message.stream_token(error_message)
        await response_message.update()
        print(f"Error: {error_message}")