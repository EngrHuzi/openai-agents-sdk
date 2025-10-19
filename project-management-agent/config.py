from agents import AsyncOpenAI, OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv, find_dotenv

# Load environment from .env if present
_ = load_dotenv(find_dotenv())
load_dotenv()

# Primary expected variable used by this project: GEMINI_API_KEY
gemini_api_key = os.getenv("GEMINI_API_KEY") 

if not gemini_api_key:
    raise RuntimeError(
        "Missing API key: set GEMINI_API_KEY (preferred)\n"
        "On Windows cmd.exe: setx GEMINI_API_KEY \"your_api_key_here\" && restart your shell\n"
        "Or add it to a .env file in the project root:\n"
        "GEMINI_API_KEY=your_api_key_here"
    )

# Configure client with text responses
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)