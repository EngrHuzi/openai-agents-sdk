# Project Management Agent Project

you will create a **Team Collaboration and Project Management Agent**, leveraging multi-agent orchestration, LLM-based tool-calling, and user-centric design to manage tasks, deadlines, and team collaboration efficiently.

---

## Getting Started (Quickstart)

Follow these steps to run the local MCP server and the Chainlit UI.

1. Install uv (if you don't have it yet)
   - Windows (PowerShell): `iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex`
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. Create and activate a virtual env for this project
   - Create: `uv venv`
   - Activate (Windows cmd): `\.venv\\Scripts\\activate`
   - Activate (PowerShell): `.\\.venv\\Scripts\\Activate.ps1`
   - Activate (bash/zsh): `source .venv/bin/activate`

3. Install dependencies with uv
   - `uv sync`

4. Set environment variables
   - Required: `GEMINI_API_KEY`
   - Windows cmd.exe:
     - `setx GEMINI_API_KEY "your_api_key_here" && exit & start cmd`
   - Or create a `.env` file at project root containing:
     - `GEMINI_API_KEY=your_api_key_here`

5. Start the MCP server (port 9000)
   - `python server.py`

6. In a new terminal, start the Chainlit app
   - `uv run chainlit run chainlit_app.py -w`

You should see the Chainlit UI launch in your browser. Use the starter buttons or chat to interact.

---

## Project Overview

1. **Goal**  
   - Build a **Team Collaboration and Project Management Agent** that helps users (and potentially an entire team) organize tasks, track progress, schedule meetings, and receive summaries of project updates.  
   - Use **LLM-based function-calling** to parse natural language commands (e.g., “Create a new sprint backlog item” or “Summarize yesterday’s stand-up meeting”), integrating with existing project management APIs (e.g., Jira, Trello, Asana).  
   - Maintain a **human-in-the-loop** approach for final approvals or major changes (e.g., reprioritizing tasks, shifting deadlines).

2. **Key Components**  
   1. **Front-End Orchestration Agent** (existing)  
      - Continues serving as the single entry point for user interactions.  
   2. **Greeting Agent** (existing)  
      - Handles trivial greetings, small talk.  
   3. **User Preference Agent** (existing)  
      - Stores user-specific or team-specific preferences: default task assignee, sprint lengths, preferred meeting times.  
   4. **Knowledge Graph Agent** (optional)  
      - Could store relationships among tasks, team members, sprints, or dependencies (e.g., “Task A depends on Task B being completed”).  
 
   5. **Project Management Agent** **(New)**  
      - Integrates with popular PM tools (Jira, Trello, Asana) or a mock/standalone task system.  
      - Uses an **LLM** to interpret user commands and call “tools” such as `CreateTask`, `UpdateDeadline`, `GenerateDailySummary`, etc.  
      - Provides a **human-in-the-loop** step for any high-impact changes (e.g., reassigning tasks, adjusting sprint scope).

3. **Value Proposition**  
   - Illustrates how multi-agent systems and LLM-based orchestration streamline everyday team and project management tasks.  
   - Shows how **natural language** can facilitate complex operations in a standard PM tool, coupled with user oversight to maintain team alignment.

---

## 1. Plan the Architecture

1. **Service Layout**  
   - The **Project Management Agent** is a new service/container that:  
     - Communicates with a project management tool or API.  
     - Leverages LLM function-calling to interpret and execute user commands.  
   - Other agents continue to operate as separate services/containers (Front-End, Greeting, Preferences, etc.).

2. **Communication Patterns**  
   - The LLM in the **Project Management Agent** will have tool definitions such as:
     - **CreateTask**(title, description, assignee, due_date)  
     - **UpdateTask**(task_id, new_status, new_due_date)  
     - **GenerateDailySummary**(project_id)  
     - **RescheduleMeeting**(meeting_id, new_time)

3. **Human-in-the-Loop Approval**  
   - For risky or large-scope actions—like completely reorganizing a sprint or removing multiple tasks—the system can return a **draft** requiring user confirmation.  
   - The user can approve or modify these changes through the **Front-End Orchestration Agent**.

---

## 2. Project Management Agent

### 2.1 Responsibilities

1. **Parse Project Commands**  
   - e.g., “Create a new task for the UI redesign, assign it to Alice, deadline next Friday.”  
   - e.g., “Move task #123 to ‘In Progress.’”  
   - The LLM interprets the instruction and calls the correct tool (e.g., `CreateTask`, `UpdateTask`).

2. **Fetch and Summarize Project Data**  
   - e.g., “Show me all tasks assigned to me this week,” or “Give me a status update on Sprint 5.”  
   - The agent calls the PM tool’s APIs to retrieve data, then uses the LLM to generate a concise summary.

3. **Meeting and Calendar Coordination**  
   - If integrated with a calendar (Google Calendar, Outlook), the agent can find meeting slots or reschedule events.  
   - Returns a draft action for user approval if it involves changing multiple people’s schedules.

4. **Daily Stand-up or Weekly Report Generation**  
   - The agent can automatically compile stand-up notes or weekly summaries from task updates and user activity.  
   - Possibly uses the **Mail Processing Agent** to send the summary via email or the **Knowledge Graph Agent** to store cross-project relationships.


## 3. Front-End Orchestration Agent: Extended Logic

1. **Identify Project Management Requests**  
   - If the user’s input relates to tasks, sprints, backlogs, or status updates, route to the **Project Management Agent**.  
   - Other requests (greetings, personal finance, etc.) remain handled by their respective agents.

2. **Draft Confirmation**  
   - If the PM Agent returns a `draft: true`, ask the user whether to finalize or modify.  
   - On approval, the front-end calls `POST /project_management/finalize` or a similar endpoint.

3. **Fallback**  
   - For requests not recognized as project management tasks or if the PM Agent cannot parse the instruction, prompt the user for clarification.

---

## 4. Demonstration Scenario

1. **User**: “Hello!”  
   - **Front-End** → **Greeting Agent** → “Hi there! How can I help you today?”  
2. **User**: “Please create a new task: ‘Design login screen,’ assigned to Sarah, with a deadline next Monday.”  
   - **Front-End** → **Project Management Agent** → The agent calls `CreateTask` with the relevant details.  
   - Returns a draft: “Task ‘Design login screen’ for Sarah, due next Monday. Approve?”  
3. **User**: “Yes, approve.”  
   - **Front-End** → Finalizes with the PM Agent, which updates the project management tool (e.g., Jira or Trello).  
   - The agent confirms: “Task created successfully.”  
4. **User**: “What are Sarah’s tasks for this sprint?”  
   - **Front-End** → **Project Management Agent** → The agent calls a PM API to filter tasks assigned to Sarah in the current sprint.  
   - Summarizes: “Sarah has three tasks: ‘Design login screen,’ ‘Fix header CSS,’ and ‘Update user onboarding flow.’”  
5. **User**: “Move ‘Fix header CSS’ to In Progress.”  
   - **Front-End** → **Project Management Agent** → Calls `UpdateTask(task_id=X, new_status='In Progress')`.  
   - Returns a success message or a draft if needed.

---

## 5. Deployment and Testing

1. **Local or Cloud Setup**  
   - Containerize each agent (Front-End, PM Agent, etc.).  
   - Connect the PM Agent to a **sandbox** or **mock** project management API (or use a real account with test projects).

2. **LLM Function-Calling**  
   - Define clear “tools” for creating/updating tasks, retrieving sprint or backlog data, summarizing stand-up notes.  
   - Verify the LLM can parse user instructions and correctly call these tools with structured parameters.

3. **Integration Points**  
   - Optionally link a calendar system for meeting invites or sprint review scheduling.  
   - Optionally link with the **Mail Processing Agent** to send daily or weekly project summaries.

4. **Observability**  
   - **Project Management Agent**: Log each action (task creation, status updates, meeting scheduling).  
   - **Front-End**: Log the user’s final confirmation or rejections.

5. **Error Handling**  
   - If the PM tool’s API returns an error (e.g., invalid assignee), the agent should produce a friendly message for resolution.

---

## 6. Possible Enhancements

1. **Task Dependency Modeling**  
   - Use the **Knowledge Graph Agent** to store dependencies (Task A depends on Task B).  
   - The system can warn the user if they try to start a task before its prerequisite is finished.

2. **Intelligent Task Prioritization**  
   - Incorporate basic ML to suggest priorities based on deadlines, effort estimates, or historical data.  
   - The user can override or confirm these suggestions.

3. **Advanced Summaries and Reporting**  
   - Let the LLM generate daily or weekly “stand-up” style summaries from multiple tasks and statuses.  
   - Possibly include burn-down charts or velocity metrics if integrating with agile frameworks.

4. **Team Collaboration and Notifications**  
   - The system could post updates to Slack or Microsoft Teams channels automatically, or email stakeholders when major tasks are completed.

5. **Multi-Project Management**  
   - Extend the system to handle multiple projects, each with different teams or boards.  
   - The user can ask cross-project questions (“Show me tasks assigned to me across all active projects.”).

6. **Time Tracking Integration**  
   - Connect with time-tracking tools (e.g., Harvest or Toggl) to automatically log time spent on tasks and generate timesheet reports.

---

## Conclusion

This **project** focuses on creating a **Team Collaboration and Project Management Agent**, demonstrating how **Agentia** can streamline:

- **Project management tasks** (creating, updating, summarizing)  
- **Team communication** (assigning tasks, scheduling sprints, updating statuses)  
- **Human-in-the-loop** workflows (confirming major changes, approvals)  
- **LLM-based orchestration** (interpret natural language commands, call PM tool APIs, generate reports)

By integrating with real or mock project management tools, you illustrate how **multi-agent systems** and **conversational AI** can dramatically improve productivity and clarity for teams operating in fast-paced or agile development environments.

---

## Installation and Dependency Management (uv)

This project uses `uv` for Python package and environment management.

- Create project env: `uv venv`
- Activate env:
  - Windows cmd: `\.venv\\Scripts\\activate`
  - PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
  - bash/zsh: `source .venv/bin/activate`
- Install deps from `pyproject.toml` / `uv.lock`: `uv sync`
- Add a new dependency: `uv add <package-name>`

Python version: `>=3.13` (see `pyproject.toml`).

---

## How to Run

Two processes run locally:

1. MCP server (provides tools over HTTP):
   - `python server.py`
   - Exposes: `http://localhost:9000/mcp`

2. Chainlit UI (front-end chat):
   - `chainlit run chainlit_app.py -w`

The Chainlit app connects to the MCP server at `http://localhost:9000/mcp` on startup.

---

## Environment Variables

- `GEMINI_API_KEY` (required)
  - Used to configure the `OpenAIChatCompletionsModel` pointing to Google Generative Language API compatible endpoint.
  - Errors on startup if missing (see `config.py`).

Optional: use a `.env` file at the project root (auto-loaded via `python-dotenv`).

---

## Project Structure

High-level files/directories:

- `server.py`: FastMCP-based MCP server exposing project management tools on port 9000.
- `agent.py`: Builds the orchestration agent and wires sub-agents and MCP server client.
- `chainlit_app.py`: Chainlit UI app; initializes MCP server client and orchestration agent; handles chat.
- `config.py`: Loads `GEMINI_API_KEY`, configures external client and model.
- `instructions.py`: Agent instruction strings for the various sub-agents.
- `gaurdrail_check.py`: Input/output guardrails for agents.
- `public/`: Static assets for Chainlit UI (theme, images, custom JS/CSS).
- `pyproject.toml`: Project metadata and dependencies; managed with uv.
- `uv.lock`: Locked dependency versions.

---

## Available MCP Tools

Exposed by the MCP server (`server.py`):

- `create_task(task: Task)`
  - Create a task with `title`, `description`, `assignee`, `due_date`.
- `update_task(update: TaskUpdate)`
  - Update task `status` and/or `due_date` by `task_id`.
- `reschedule_meeting(meeting: Meeting)`
  - Set a new time for a meeting.
- `generate_daily_summary(project_id?: str, assignee?: str)`
  - Summarize tasks (counts per status) globally or for an assignee.
- `get_user_tasks(assignee: str)`
  - List tasks assigned to a specific user.
- `get_sprint_summary(sprint_id: str)`
  - Sprint-level progress: total, completed, remaining, percent done.

These tools are automatically discovered and used by the orchestration agent via the MCP HTTP transport.

---

## Usage Examples

- Create a task (natural language via Chainlit):
  - "Create a new task for project 'Project X' titled 'Landing Page' assigned to 'Alex' due tomorrow."
- Generate a summary:
  - "Generate a daily summary for project 'Project X'."
- Reschedule a meeting:
  - "Reschedule meeting MTG-42 to 3pm tomorrow."
- Update status:
  - "Mark the task 'Landing Page' as completed."

---

## Customization

- UI: tweak `public/custom_theme.css` and `public/custom_js.html`.
- Starters: edit the `@cl.set_starters` list in `chainlit_app.py`.
- Agent logic: adjust instructions in `instructions.py` or guardrails in `gaurdrail_check.py`.

---

## Troubleshooting

- Missing API key error on startup
  - Ensure `GEMINI_API_KEY` is set. On Windows cmd.exe:
    - `setx GEMINI_API_KEY "your_api_key_here" && exit & start cmd`
  - Or add it to `.env` and restart the app.

- Chainlit cannot connect to MCP server
  - Confirm `python server.py` is running and listening on `http://localhost:9000/mcp`.
  - Check firewall rules or conflicting ports.

- Port already in use (9000)
  - Stop the conflicting process or change the port in `server.py` and in `chainlit_app.py` MCP URL.

- Dependency issues
  - Recreate env: `deactivate` then `uv venv && uv sync`.

---

## Development Notes

- Python `>=3.13` required.
- Key dependencies (see `pyproject.toml`): `openai-agents`, `chainlit`, `mcp`, `python-dotenv`.
- Use `uv add <package>` to add new dependencies.

---

## Chainlit Configuration

The Chainlit app is configured via `.chainlit/config.toml`.

- UI
  - `name`: "Project Management Agent"
  - `default_theme`: `light` (pairs with `public/custom_theme.css`)
  - `logo_file_url`: `/public/architect.png`
  - `default_avatar_file_url`: `/public/avator.jpg`
  - `custom_css`: `/public/custom_theme.css`
  - `custom_js`: `/public/custom_js.html`
  - Header links configured for Documentation and GitHub

- Features
  - `persistence = true` (threads persist)
  - Spontaneous file uploads enabled
  - MCP transports enabled: `sse`, `streamable-http`, `stdio`

If you change the MCP server URL/port, update it in `chainlit_app.py` where `MCPServerStreamableHttpParams(url=...)` is created.

---

## Agent Instructions and Guardrails

Agent instruction prompts live in `instructions.py`:

- `greeting_agent_instructions`: Brief, friendly greetings only.
- `user_preference_agent_instructions`: Manage and recall user/team preferences.
- `knowledge_graph_agent_instructions`: Reason about dependencies and relationships.
- `project_management_agent_instructions`: Execute project and task operations; approval flow for irreversible actions.
- `orchestration_agent_instructions`: Classify and route requests, manage human-in-the-loop drafts.

Guardrails live in `gaurdrail_check.py` and are attached in `agent.py` for each agent’s input/output. Adjust or extend these to enforce domain boundaries and response quality.

---

## Running the Orchestration via Script

Besides the UI, you can run a quick orchestration test from `agent.py` once the MCP server is running:

1. Start MCP server:
   - `python server.py`
2. In another terminal, run the demo:
   - `python agent.py`

This will construct the orchestration agent graph, send a sample instruction, and print the final output to the console.

---

## Security & Production Considerations

- Do not commit real API keys; use environment variables or secret managers.
- Consider authn/authz for MCP server when exposing beyond localhost.
- Add structured logging and request IDs across UI and MCP server for traceability.
- Replace in-memory stores with persistent data sources (DB/PM APIs) for real usage.

---

## Contributing

1. Create a branch from `main`.
2. Use `uv` for dependency changes (`uv add`), then `uv lock` is auto-managed.
3. Ensure README stays updated when adding features/tools.
4. Open a PR with a concise description and testing notes.