AI Assistant with Chainlit and OpenAI Agents sdk

This project implements an interactive AI assistant using Chainlit and the openai-agents framework. The assistant leverages a hierarchical agent structure, enabling it to perform online searches via the Tavily API and provide the current date and time. The application integrates with the Gemini API for natural language processing and is designed to run as a web-based chat interface.
Features

Interactive Chat Interface: Built with Chainlit, offering real-time streaming of responses.
Hierarchical Agents:
search_agent: Handles online searches using the Tavily API.
supervisor_agent_with_datetime: Coordinates responses, using tools to fetch the current time or delegate search tasks.


Tool Integration:
browse_online: Performs web searches.
get_current_datetime: Returns the current date and time.


Environment Variable Support: Securely manages API keys using a .env file.
Real-Time Streaming: Responses are streamed token-by-token for a smooth user experience.

Prerequisites

Python 3.8 or higher
API keys for:
Gemini API (GEMINI_API_KEY)
Tavily API (SEARCH_API_KEY)



Installation

Clone the Repository:
git clone <repository-url>
cd <repository-directory>


Set Up a Virtual Environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



install directly:
pip install chainlit openai-agents tavily-python python-dotenv 


Configure Environment Variables:Create a .env file in the project root with the following content:
GEMINI_API_KEY=your_gemini_api_key
SEARCH_API_KEY=your_tavily_api_key



Usage

Run the Application:
uv run chainlit run chatbot.py     

This starts a local web server, typically at http://localhost:8000.

Access the Chat Interface:Open your browser and navigate to http://localhost:8000. You'll see a welcome message from the AI assistant.

Interact with the Assistant:

Ask questions like "What's the current time?" to use the get_current_datetime tool.
Request information like "Search for the latest AI news" to trigger the search_agent with the browse_online tool.



Project Structure

app.py: Main application script containing the Chainlit setup, agent definitions, and tool implementations.
.env: Environment file for storing API keys (not tracked in version control).
requirements.txt: Lists project dependencies.


Potential Enhancements

Add more tools (e.g., for specific data processing or API integrations).
Enhance prompts for better tool selection and response quality.
Implement session persistence using a database for chat history.
Customize the Chainlit UI with additional features like buttons or forms.

Troubleshooting

API Key Errors: Ensure GEMINI_API_KEY and SEARCH_API_KEY are correctly set in the .env file.
Dependency Issues: Verify all packages are installed using uv list. Reinstall if necessary.
Server Not Starting: Check for port conflicts (default: 8000) or missing dependencies.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Chainlit for the chat interface framework.
Tavily for search capabilities.
Google Gemini API for language model support.
python-dotenv for environment variable management.

