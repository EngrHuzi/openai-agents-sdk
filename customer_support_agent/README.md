# Multi-Agent Customer Support Bot with Chainlit and Gemini API

This project implements a customer support chatbot using [Chainlit](https://docs.chainlit.io/) and the Gemini API. It features a triage agent that intelligently routes customer messages to specialized agents for billing and technical support, ensuring faster and more accurate resolutions.

## 🚀 Features

- 🤖 **Triage Agent**: Determines the nature of customer queries and hands them off to the appropriate specialist.
- 💳 **Billing Agent**: Handles subscription, payment, and refund inquiries.
- 🛠 **Technical Agent**: Assists with troubleshooting and technical issues.
- 🌐 **Streaming Responses**: Simulates real-time message streaming for better user experience.
- 🔐 **Environment Configuration**: API keys are managed securely via `.env` file.

## 🧰 Technologies Used

- **Python**
- **Chainlit**
- **Gemini API (OpenAI-compatible)**
- **dotenv** for managing environment variables

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

