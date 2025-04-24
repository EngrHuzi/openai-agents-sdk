# Chainlit Chatbot Application

This project integrates Chainlit with Agents to provide a chatbot experience that streams responses token-by-token using a Gemini API.

## Setup

1. Create a `.env` file in the project root and set the following environment variable:
   - `GEMINI_API_KEY`: Your Gemini API key.

2. Install the required dependencies using uv package manager:

   ```bash
   uv add package-name
   ```

3. Run the Chainlit server:

   ```bash
   uv run chainlit run chatbot.py
   ```

## Project Structure

- `chatbot.py`: The main chatbot implementation. It initializes agents, config, and handles incoming messages. The responses are streamed token-by-token to simulate live typing.
- `chainlit.md`: This documentation file.

## Features

- **Multiple Agents**: The chatbot defines specialist agents for billing and technical support, coordinated via a triage agent.
- **Session Management**: Conversation history and required configurations are stored in the Chainlit user session.
- **Streaming Responses**: The chatbot simulates streaming by splitting the response into tokens and sending them sequentially with a short delay.

## Customization

- You can adjust the agents' instructions and handoffs in `chatbot.py` to fit your requirements.
- Modify the streaming logic or delays in the `@cl.on_message` handler as needed.

## Troubleshooting

- Ensure that the `GEMINI_API_KEY` is correctly set in your `.env` file.
- Check the console logs for errors if the chatbot does not behave as expected.
- Verify that all required dependencies are installed.
