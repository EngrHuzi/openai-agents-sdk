from mcp.server.fastmcp import FastMCP

mcp_app = FastMCP(
    name="MCPServer",
    stateless_http=True,
    json_response=True, # Generally easier for HTTP clients if they don't need full SSE parsing
)

@mcp_app.tool(name="get_weather",description="Get the weather for a given city")
async def get_weather(city:str):
    return f"The weather in {city} is sunny."



mcp_app1=mcp_app.streamable_http_app()


