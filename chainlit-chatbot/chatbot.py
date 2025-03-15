import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel  # type: ignore
from agents.run import RunConfig  # type: ignore

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    # Initialize external client for streaming with Gemini API
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Set up the chat session when a user connects
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    agent: Agent = Agent(name="Assistant", instructions="You are a helpful assistant your name is Alexa", model=model)
    cl.user_session.set("agent", agent)

    # Send a welcome message
    await cl.Message(content="Welcome to the  AI  Assistant! How can I help you today?").send()

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
        print(f"Assistant: {response_content}")
    except Exception as e:
        await msg.stream_token(f"\nError: {str(e)}")
        await msg.update()
        print(f"Error: {str(e)}")




