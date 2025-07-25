from mcp.server.fastmcp import FastMCP

mcp=FastMCP(name="hello mcp",stateless_http=True)

@mcp.tool()
def search(query:str):
    return {"result": f"Searching for {query}"}

@mcp.tool()
def weather(city:str):
    return {"result": f"The weather in {city} is sunny."}


mcp_app=mcp.streamable_http_app()





