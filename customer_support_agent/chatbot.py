import os
from typing import List, Dict, Optional
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

# Define maximum chat history length to manage memory
MAX_HISTORY_LENGTH = 10

# Define specialist agents
BILLING_AGENT = Agent(
    name="Billing Agent",
    instructions="""You are a billing specialist assisting customers with payment-related inquiries,
      such as billing disputes, subscription modifications, and refund requests. For inquiries about
      technical issues or account settings, politely clarify that your expertise is limited to billing
      and payment matters and offer to transfer to the appropriate specialist.""",
)

TECHNICAL_AGENT = Agent(
    name="Technical Agent",
    instructions="""You are a technical support specialist assisting with product-related issues,
      including troubleshooting, error messages, and how-to queries. Focus exclusively on resolving 
      technical problems. For billing or payment inquiries, politely clarify that your expertise is 
      limited to technical matters and offer to transfer to the appropriate specialist.""",
)

TRIAGE_AGENT = Agent(
    name="Customer Service",
    instructions="""You are the initial customer service representative responsible for routing inquiries. 
    Direct billing or payment-related questions to the Billing Agent and technical or how-to questions 
    to the Technical Agent. Answer general product inquiries directly, including questions about your 
    role or purpose. When handing off, confirm with the user and ensure a courteous and seamless transition.""",
    handoffs=[BILLING_AGENT, handoff(TECHNICAL_AGENT)],
)

@cl.on_chat_start
async def initialize_session():
    """Initialize the session with the Gemini API client and default agent settings."""
    try:
        # Initialize external client for Gemini API
        # Note: Verify that the Gemini API endpoint is compatible with AsyncOpenAI client
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
        logger.info("Session initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize session: {str(e)}")
        raise RuntimeError(f"Failed to initialize session: {str(e)}")

@cl.on_message
async def process_message(message: cl.Message):
    """Handle incoming user messages, route to appropriate agents, and stream responses."""
    response_message = cl.Message(content="")
    await response_message.send()

    # Retrieve session data
    current_agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    chat_history: List[Dict[str, str]] = cl.user_session.get("chat_history", [])
    awaiting_handoff: Optional[str] = cl.user_session.get("awaiting_handoff")
    inquiry_type: Optional[str] = cl.user_session.get("inquiry_type")

    # Append user message to chat history and limit length
    chat_history.append({"role": "user", "content": message.content})
    chat_history = chat_history[-MAX_HISTORY_LENGTH:]  # Keep only the last 10 messages

    # Log current session state for debugging
    logger.debug(f"Processing message: {message.content}, Current agent: {current_agent.name}, Awaiting handoff: {awaiting_handoff}")

    # Handle handoff confirmation
    if awaiting_handoff:
        if message.content.strip().lower() in ["yes", "proceed", "okay", "confirm"]:
            target_agent = BILLING_AGENT if awaiting_handoff == "billing" else TECHNICAL_AGENT
            cl.user_session.set("agent", target_agent)
            cl.user_session.set("awaiting_handoff", None)
            cl.user_session.set("inquiry_type", awaiting_handoff)
            cl.user_session.set("chat_history", chat_history)  # Preserve history
            response_content = (
                f"Thank you. You have been transferred to our {target_agent.name}. "
                "How may they assist you?"
            )
            await response_message.stream_token(response_content)
            await response_message.update()
            logger.info(f"User transferred to {target_agent.name}")
            return
        else:
            cl.user_session.set("awaiting_handoff", None)
            cl.user_session.set("inquiry_type", None)
            response_content = "Understood. How may I assist you further?"
            await response_message.stream_token(response_content)
            await response_message.update()
            logger.info("Handoff cancelled by user")
            return

    # Detect inquiry type for routing
    message_lower = message.content.lower()

    # Handle specialist agent logic
    if current_agent.name == "Billing Agent" and any(
        keyword in message_lower for keyword in ["technical", "error", "bug", "problem", "crash"]
    ):
        logger.debug(f"Current agent: {current_agent.name}, redirecting technical inquiry")
        cl.user_session.set("awaiting_handoff", "technical")
        response_content = (
            "I’m sorry, this appears to be a technical issue. As a billing specialist, "
            "I’ll transfer you to our Technical Agent. Please confirm with 'yes' or 'proceed'."
        )
        await response_message.stream_token(response_content)
        await response_message.update()
        logger.info("Billing Agent redirecting technical inquiry")
        return
    elif current_agent.name == "Technical Agent" and any(
        keyword in message_lower for keyword in ["billing", "charge", "payment", "refund", "subscription"]
    ):
        logger.debug(f"Current agent: {current_agent.name}, redirecting billing inquiry")
        cl.user_session.set("awaiting_handoff", "billing")
        response_content = (
            "I’m sorry, this appears to be a billing issue. As a technical specialist, "
            "I’ll transfer you to our Billing Agent. Please confirm with 'yes' or 'proceed'."
        )
        await response_message.stream_token(response_content)
        await response_message.update()
        logger.info("Technical Agent redirecting billing inquiry")
        return

    # Triage logic for Customer Service agent
    if current_agent.name == "Customer Service":
        if any(keyword in message_lower for keyword in ["yourself", "about you", "who are you", "what are you"]):
            response_content = (
                "I am a Customer Service representative here to assist with general inquiries, "
                "billing, or technical issues. How may I help you today?"
            )
            for token in response_content.split():
                await response_message.stream_token(token + " ")
            await response_message.update()
            chat_history.append({"role": "assistant", "content": response_content})
            cl.user_session.set("chat_history", chat_history)
            logger.info("Customer Service responded to self-inquiry")
            return
        elif any(keyword in message_lower for keyword in ["billing", "charge", "payment", "refund", "subscription"]):
            cl.user_session.set("awaiting_handoff", "billing")
            response_content = (
                "Thank you for your inquiry. To assist with your billing concern, may I connect you "
                "with our Billing Agent? Please confirm with 'yes' or 'proceed'."
            )
            await response_message.stream_token(response_content)
            await response_message.update()
            logger.info("Customer Service routing billing inquiry")
            return
        elif any(keyword in message_lower for keyword in ["technical", "error", "bug", "problem", "crash"]):
            cl.user_session.set("awaiting_handoff", "technical")
            response_content = (
                "Thank you for your inquiry. To assist with your technical issue, may I connect you "
                "with our Technical Agent? Please confirm with 'yes' or 'proceed'."
            )
            await response_message.stream_token(response_content)
            await response_message.update()
            logger.info("Customer Service routing technical inquiry")
            return

    try:
        # Execute agent with context and stream response
        logger.debug(f"Executing {current_agent.name} with input: {chat_history}")
        result = Runner.run_sync(
            starting_agent=current_agent, input=chat_history, run_config=config
        )
        response_content = result.final_output

        # Stream response tokens
        for token in response_content.split():
            await response_message.stream_token(token + " ")
        await response_message.update()

        # Update chat history
        chat_history.append({"role": "assistant", "content": response_content})
        chat_history = chat_history[-MAX_HISTORY_LENGTH:]  # Limit history length
        cl.user_session.set("chat_history", chat_history)

        # Log interaction
        logger.info(f"Agent: {current_agent.name} | User Input: {message.content}")
        logger.info(f"Assistant Response: {response_content}")
    except OpenAIError as e:
        error_message = "Failed to process request due to an API error. Please try again later."
        await response_message.stream_token(error_message)
        await response_message.update()
        logger.error(f"API Error in {current_agent.name}: {str(e)}")
    except ClientError as e:
        error_message = "Network issue occurred. Please check your connection and try again."
        await response_message.stream_token(error_message)
        await response_message.update()
        logger.error(f"Network Error in {current_agent.name}: {str(e)}")
    except Exception as e:
        error_message = "An unexpected error occurred. Please try again or contact support."
        await response_message.stream_token(error_message)
        await response_message.update()
        logger.error(f"Unexpected Error in {current_agent.name}: {str(e)}")