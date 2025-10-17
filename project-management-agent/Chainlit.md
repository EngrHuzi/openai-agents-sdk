### Chainlit Integration

This project includes a Chainlit UI with streaming, chat history, starter prompts, and a custom dark/light theme.

#### Run

```bash
# Run Chainlit on 3000 to avoid MCP (8000) conflict
uv run chainlit run chainlit_app.py -w -p 3000
```

If `uv` is not on PATH, run from project root with your chosen Python env.

#### Features

- **Streaming**: Responses stream live.
- **Chat history**: Sessions persist in Chainlit; users can switch between threads.
- **Starter prompts**: Quick actions shown on chat start.
- **Dark/Light**: Default dark; toggle in UI. Custom palette in `public/theme.json`.

#### Configuration

- `/.chainlit/config.toml` sets app entrypoint and default theme.
- `/public/theme.json` customizes fonts, colors, and surfaces for both themes.

Example config snippet:

```toml
[UI]
default_theme = "dark"
theme = "public/theme.json"
```

#### Environment

Set an API key compatible with `config.py` and configure MCP URL if needed:

```bash
setx GEMINI_API_KEY "your_api_key"  # Windows
# Optional: if MCP is not at default localhost:8000
setx MCP_SERVER_URL "http://localhost:8001/mcp"
```

#### Notes

- The UI uses the same orchestration graph as `agent.py` via `create_orchestration_agent`.
- The MCP server is managed per-session inside Chainlit.

