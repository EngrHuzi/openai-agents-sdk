# Mental Health Support Assistant

Welcome to the Mental Health Support Assistant – an AI‑powered platform designed to support your mental well-being. This project harnesses multiple AI agents with built‑in safety guardrails to provide a secure, empathetic, and interactive experience for users managing stress, tracking their mood, engaging in reflective journaling, performing meditation exercises, and even detecting crisis situations.

## Overview

The Mental Health Support Assistant is built to:

- **Mood Tracking:** Identify key emotions and events in your day to help you understand your mood trends.
- **Journaling Guidance:** Assist in recording and reflecting on your thoughts with supportive suggestions and structured outputs.
- **Meditation Support:** Guide you through short, soothing meditation exercises tailored to your current state.
- **Crisis Detection:** Monitor user inputs for signs of distress and alert you or offer resources when needed.
- **Supervisor Guidance:** Enable professional oversight when critical situations are detected.

Built on a flexible and extensible architecture, the project leverages the:

- **Chainlit UI:** Provides a responsive, conversational frontend.
- **Gemini API:** Integrates advanced language models to understand and generate supportive responses.
- **Python & FastAPI:** Manage backend processes and API communications.
- **Multilingual Support:** Offers translations and localized messages via a dedicated `.chainlit/translations` directory.

## Features

- **Secure & Supportive Interactions:** All outputs are validated through safety guardrails.
- **Reflective Journaling:** Capture and organize your daily thoughts with a focus on growth and self-compassion.
- **Guided Meditation:** Follow simple, calming exercises to alleviate stress.
- **User-Friendly Interface:** Powered by Chainlit, ensuring an intuitive chat-based experience.
- **Extensible Architecture:** Easily expand the project with new modules or enhanced AI agent capabilities.

## Getting Started

### Prerequisites

- **Python 3.13 or later** – Ensure your environment meets the required Python version.
- **Pipenv/Virtual Environment:** It is recommended to use a virtual environment for project dependencies.
- **Environment Variables:** Create a `.env` file and set the required keys such as `GEMINI_API_KEY` for the Gemini API.

### Installation

1. **Clone the Repository:**

   ```sh
   git clone https://github.com/yourusername/mental-health-support-agent.git
   cd mental-health-support-agent
   ```

2. **Install Dependencies:**

   ```sh
   pip install -r requirements.txt
   # or if using pyproject.toml with a build tool like Poetry:
   poetry install
   ```

3. **Set Up Environment Variables:**

   Ensure you have your `.env` file properly configured with your API keys and other settings. See [`.env.example`](.env.example) for reference.

### Running the Application

To start the backend and open the Chainlit interface:

```sh
chainlit run agent.py
```

Once running, open your browser to the local URL provided (usually http://localhost:8000) and start interacting with the assistant.

## Technologies Used

- **Chainlit:** For building interactive, chat-based UIs. See the [Chainlit documentation](https://chainlit.io) for more details.
- **Gemini API:** Integrates an advanced AI model for language understanding and response generation.
- **FastAPI:** A high-performance backend framework.
- **Python:** The core programming language used in the project.
- **Additional Libraries:** Managed via [pyproject.toml](pyproject.toml)

## Project Structure

The main files and directories include:

- **agent.py:** Contains the core logic for initializing agents and defining conversation flows.
- **instructions.py:** Holds detailed guidance for each agent (mood tracking, journaling, meditation, crisis detection).
- **chainlit.md:** Provides additional documentation about Chainlit usage and project details.
- **pyproject.toml & uv.lock:** Manage project dependencies and build configurations.
- **.chainlit/translations/:** Directory for localization files supporting multiple languages.
- **README.md:** This file, outlining project overview, setup, and usage.

## Contributing

Contributions are welcome! If you have ideas or improvements, please open an issue or submit a pull request. When contributing, please ensure your changes adhere to the project’s safety and quality standards.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- Special thanks to the developers behind Chainlit and the Gemini API for providing the backbone technology for this project.
- Inspired by the need to support mental well-being and foster healthy conversations in digital environments.

Enjoy your experience with the Mental Health Support Assistant, and remember, taking care of your