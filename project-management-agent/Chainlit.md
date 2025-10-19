# Project Management Agent - Chainlit Integration

This project provides a **Team Collaboration and Project Management Agent** with a Chainlit web interface that enables natural language interaction for project management tasks.

## Overview

The Chainlit app provides a conversational interface to a multi-agent system that handles:
- **Project Management**: Create tasks, update statuses, manage deadlines
- **Team Collaboration**: Assign tasks, generate summaries, reschedule meetings
- **User Preferences**: Store and recall team settings and defaults
- **Knowledge Graph**: Analyze task dependencies and relationships
- **Greeting & Orchestration**: Route requests to appropriate specialized agents

## Quick Start

### Prerequisites

1. **Install dependencies** using UV (recommended package manager):
   ```bash
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   # Required: Set your Gemini API key
   setx GEMINI_API_KEY "your_gemini_api_key_here"  # Windows
   # export GEMINI_API_KEY="your_gemini_api_key_here"  # Linux/Mac
   ```

3. **Start the MCP Server** (in a separate terminal):
   ```bash
   uv run python server.py
   ```
   This starts the project management tools server on `http://localhost:9000`

4. **Launch Chainlit** (in another terminal):
   ```bash
   uv run chainlit run chainlit_app.py -w 
   ```
   The app will be available at `http://localhost:8000`

## Features

### 🤖 Multi-Agent Architecture
- **Front-End Orchestration Agent**: Routes requests to specialized agents
- **Project Management Agent**: Handles task creation, updates, and project operations
- **User Preference Agent**: Manages team settings and personalization
- **Knowledge Graph Agent**: Analyzes task dependencies and relationships
- **Greeting Agent**: Handles casual conversation and greetings

### 💬 Conversational Interface
- **Natural Language Processing**: Convert spoken requests into structured actions
- **Streaming Responses**: Real-time response streaming for better UX
- **Chat History**: Persistent conversation threads across sessions
- **Starter Prompts**: Quick action buttons for common tasks

### 🛠️ Project Management Tools
- **Task Management**: Create, update, and track tasks with assignees and deadlines
- **Meeting Coordination**: Reschedule meetings and manage calendars
- **Daily Summaries**: Generate project status reports and team updates
- **Sprint Management**: Track sprint progress and burndown metrics
- **User Task Views**: Get personalized task lists and assignments

### 🔧 Technical Features
- **MCP Integration**: Uses Model Context Protocol for tool calling
- **Guardrails**: Input/output validation for safe operations
- **Human-in-the-Loop**: Draft approvals for major changes
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## Starter Prompts

The interface includes quick-start buttons for common operations:

1. **"Create a new task"** - Create tasks with title, assignee, and due date
2. **"Daily summary"** - Generate project status summaries
3. **"Reschedule meeting"** - Update meeting times and schedules

## Example Interactions

### Task Management
```
User: "Create a new task for project 'Website Redesign' titled 'Update Homepage' assigned to 'Sarah' due tomorrow"
Agent: [Creates task with ID TASK-20250117123456 and confirms details]
```

### Project Summaries
```
User: "Generate a daily summary for project 'Website Redesign'"
Agent: [Provides status breakdown: 3 To Do, 4 In Progress, 10 Done]
```

### Meeting Coordination
```
User: "Reschedule meeting MTG-42 to 3pm tomorrow"
Agent: [Updates meeting time and confirms the change]
```

## Architecture

### Agent Flow
1. **User Input** → Front-End Orchestration Agent
2. **Intent Classification** → Route to appropriate specialist agent
3. **Tool Execution** → MCP server handles project management operations
4. **Response Generation** → Stream results back to user
5. **Approval Loop** → Human confirmation for major changes

### MCP Server Tools
- `create_task`: Create new tasks with full metadata
- `update_task`: Modify task status and due dates
- `generate_daily_summary`: Generate project/team summaries
- `reschedule_meeting`: Update meeting schedules
- `get_user_tasks`: Retrieve user-specific task lists
- `get_sprint_summary`: Get sprint progress and metrics

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for LLM functionality
- Default MCP server URL: `http://localhost:9000/mcp`

### Dependencies
- **Chainlit**: Web UI framework
- **OpenAI Agents SDK**: Multi-agent orchestration
- **MCP**: Model Context Protocol for tool integration
- **FastMCP**: HTTP-based MCP server implementation
- **Pydantic**: Data validation and serialization

## Development

### Project Structure
```
project-management-agent/
├── chainlit_app.py          # Chainlit web interface
├── agent.py                 # Multi-agent orchestration setup
├── server.py                # MCP server with project management tools
├── config.py                # LLM configuration (Gemini)
├── instructions.py          # Agent behavior instructions
├── gaurdrail_check.py       # Input/output validation
└── pyproject.toml           # Project dependencies
```

### Running in Development
1. Start MCP server: `uv run python server.py`
2. Start Chainlit: `uv run chainlit run chainlit_app.py -w `
3. Access at: `http://localhost:8000`

## Notes

- The Chainlit UI uses the same orchestration graph as the standalone `agent.py`
- MCP server runs on port 9000, Chainlit on port 3000 to avoid conflicts
- All project management operations go through the MCP server for consistency
- The system supports both individual and team-based project management workflows

