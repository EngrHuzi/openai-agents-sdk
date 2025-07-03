# Personal Finance & Travel Advisor Agent

An all-in-one AI assistant for personal finance, travel planning, reminders, and weather updates, powered by Chainlit and advanced LLM agents.

## 🚀 Features
- **Travel Planning:** Generate detailed, realistic itineraries for any destination, duration, and interest.
- **Budget Creation:** Personalized monthly budget plans based on your income, expenses, and savings goals.
- **Reminders:** Set up clear, actionable reminders for any task or event.
- **Weather Information:** Instantly check current or forecasted weather for any location and date.
- **Smart Supervision:** The agent intelligently routes your requests to the right specialist agent.
- **Guardrails:** All requests and responses are checked for safety, legality, and realism.
- **Streaming Responses:** Enjoy real-time, token-by-token answers for a smooth chat experience.
- **Session Memory:** The assistant remembers your conversation for context-aware help.

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
 git clone <repo-url>
 cd Personal-finance-advisor-agent
```

### 2. Install Dependencies (using [uv](https://github.com/astral-sh/uv))
```bash
uv venv
uv sync  # use `uv sync` if you have a lockfile
```

Or, to add dependencies individually:
```bash
uv add chainlit python-dotenv pydantic openai-agents tavily-python
```

### 3. Environment Variables
Create a `.env` file in the project root with the following:
```
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run the App
```bash
uv run chainlit run chatbot.py
```
Open the provided local URL in your browser to start chatting!

## 💡 Usage
- Type your request in the chat (e.g., "Plan a 5-day trip to Paris with a focus on art and food").
- Ask for multiple things at once (e.g., "Can I move to the USA for 30 days and also tell the weather in NY city on March 3, 2025?").
- Set reminders (e.g., "Remind me to pay my credit card bill on the 15th of every month").
- Check the weather (e.g., "What's the weather in Tokyo next Friday?").

## ⚙️ Configuration
- All configuration for Chainlit is in `.chainlit/config.toml`.
- The welcome screen is in `chainlit.md`.
- Agent instructions are in `instructions.py`.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## 📄 License
[MIT](LICENSE)

## 📚 Resources
- [Chainlit Documentation](https://docs.chainlit.io)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents)
- [Tavily Python](https://pypi.org/project/tavily-python/)

---

*Built with ❤️ using Chainlit, OpenAI Agents, and modern Python tools.*
