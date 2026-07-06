import asyncio
from anthropic import Anthropic
from google.adk.tools.function_tool import FunctionTool
from google.adk.models.anthropic_llm import function_declaration_to_tool_param
from tools.mcp_tools import get_github_mcp_toolset, search_github_tools, execute_github_tool

client = Anthropic()

async def main():
    # Full, unfiltered GitHub toolset -- real MCPTool objects
    full_toolset = get_github_mcp_toolset()
    all_mcp_tools = await full_toolset.get_tools()
    full_schema = [
        function_declaration_to_tool_param(t._get_declaration())
        for t in all_mcp_tools
    ]

    # Lean dispatcher -- real FunctionTool objects, same wrapping the actual agent uses
    search_tool = FunctionTool(func=search_github_tools)
    execute_tool = FunctionTool(func=execute_github_tool)
    lean_schema = [
        function_declaration_to_tool_param(search_tool._get_declaration()),
        function_declaration_to_tool_param(execute_tool._get_declaration()),
    ]

    full_count = client.messages.count_tokens(
        model="claude-sonnet-5",
        messages=[{"role": "user", "content": "test"}],
        tools=full_schema,
    )
    lean_count = client.messages.count_tokens(
        model="claude-sonnet-5",
        messages=[{"role": "user", "content": "test"}],
        tools=lean_schema,
    )

    print(f"Full toolset ({len(all_mcp_tools)} tools): {full_count.input_tokens} tokens")
    print(f"Lean dispatcher (2 tools): {lean_count.input_tokens} tokens")
    reduction = (full_count.input_tokens - lean_count.input_tokens) / full_count.input_tokens * 100
    print(f"Reduction: {reduction:.1f}%")

asyncio.run(main())