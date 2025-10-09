from agents import AsyncOpenAI, OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure client with text responses
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",

)


model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,


)