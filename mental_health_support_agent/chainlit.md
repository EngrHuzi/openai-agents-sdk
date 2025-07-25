# Mental Health Support Assistant

Welcome to the Mental Health Support Assistant, an AI-powered platform designed to support your mental well-being. This project integrates several modules to help you track your mood, guide your journaling, provide meditation support, and detect potential crisis situations.

## Overview

This project harnesses multiple AI agents with built-in safety guardrails to ensure a supportive and safe user experience:

- **Mood Tracking:** Receive insights and support for managing your emotions with secure input and output validations.
- **Journaling Guidance:** Engage in reflective journaling under gentle guidance.
- **Meditation Support:** Access personalized meditation exercises to help reduce stress.
- **Crisis Detection:** Built-in crisis detection mechanisms to provide help when needed.

## How to Use

1. **Setup:** Ensure that the environment variable `GEMINI_API_KEY` is set to your Gemini API key.
2. **Start the Application:** Run the project and access the Chainlit interface.
3. **Interaction:** Begin by sending a message. The assistant, powered by multiple AI agents and safety guardrails, will respond to your inputs.

## Technologies

- **Chainlit:** This application uses Chainlit as its frontend UI to facilitate interactive conversations.
- **Gemini API:** The project leverages the Gemini-2.0-flash model through the Gemini API for advanced language understanding.
- **Python & UV:** The backend is built using Python, managing dependencies with UV for streamlined package management.

## Project Structure

- `agent.py`: Contains the logic for initializing agents and defining interaction flows with various guardrails.
- `instructions.py`: Provides the instructions for mood tracking, journaling, meditation, crisis detection, and supervisor guidance.
- `chainlit.md`: Documentation file you are currently reading, updated to reflect the purpose of this project.
- Other configuration files such as `pyproject.toml` and `uv.lock` handle project dependencies.

Enjoy your experience, and remember that taking care of your mental health is a priority. If you need crisis support, please reach out to local professionals immediately.
