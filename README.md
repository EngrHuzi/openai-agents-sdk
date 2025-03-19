# OpenAI Agents SDK

The **OpenAI Agents SDK** enables you to build **agentic AI applications** with a lightweight and easy-to-use package. It is a **production-ready** upgrade from OpenAI's previous agent experimentation, Swarm. This SDK provides a minimal set of powerful primitives that make it easy to develop and deploy **real-world AI agents**.

## Key Features

- **Agents**: LLMs equipped with instructions and tools to perform tasks.
- **Handoffs**: Agents can delegate specific tasks to other agents.
- **Guardrails**: Validate and check agent inputs before processing.
- **Tracing**: Built-in debugging, monitoring, and evaluation tools.
- **Function Tools**: Convert any Python function into a tool with automatic schema generation and validation.

## Why Use OpenAI Agents SDK?

The SDK is designed with two core principles:

1. **Minimal yet powerful**: Enough features to be useful, yet simple enough to learn quickly.
2. **Out-of-the-box functionality with full customizability**: Works well by default but allows fine-tuning and custom behaviors.

## Features Overview

### 1. Agent Loop
A built-in loop that handles calling tools, sending results to the LLM, and iterating until completion.

### 2. Python-First
Orchestrate and chain agents using native Python features without learning additional abstractions.

### 3. Handoffs
Agents can delegate tasks to specialized agents for better task execution.

### 4. Guardrails
Input validation and parallel checks to ensure robust agent behavior.

### 5. Function Tools
Easily turn Python functions into AI tools with **Pydantic-powered validation**.

### 6. Tracing and Monitoring
Visualize, debug, and optimize agent workflows using OpenAI’s built-in evaluation and fine-tuning tools.


## Quickstart Example

## Installation

To install the OpenAI Agents SDK, run:

```sh
uv add  openai-agents  python-dotenv
```

Here's how to create a simple agent using the SDK:

```python
from openai_agents import Agent, Tool

def greet(name: str) -> str:
    return f"Hello, {name}!"

greet_tool = Tool(function=greet)

agent = Agent(tools=[greet_tool], instructions="You are a helpful assistant.")

response = agent.run("Greet Alice")
print(response)
```

## Contributing
We welcome contributions! Feel free to submit **issues**, **feature requests**, or **pull requests** to help improve the SDK.

## License
This project is licensed under the [MIT License](LICENSE).

## Learn More
For full documentation and advanced usage, visit the [OpenAI Agents SDK documentation](https://platform.openai.com/docs/).
