"""
Part 2: GitHub MCP Integration

Configure McpToolset to connect to the GitHub MCP server.

Required: Direct configuration in Python code
Optional: File-based configuration from config/mcp_servers.json
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

# Path to MCP server configuration (for Option B)
MCP_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mcp_servers.json"


# =============================================================================
# REQUIRED: Direct Configuration
# =============================================================================
# TODO: Implement get_github_mcp_toolset()
# Configure the GitHub MCP server directly in Python code.
#
# Example structure:
#
# def get_github_mcp_toolset() -> McpToolset:
#     token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
#     if not token:
#         raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in .env")
#
#     server_params = StdioServerParameters(
#         command="npx",
#         args=["-y", "@modelcontextprotocol/server-github"],
#         env={"GITHUB_PERSONAL_ACCESS_TOKEN": token}
#     )
#
#     return McpToolset(
#         connection_params=StdioConnectionParams(server_params=server_params)
#     )


def get_github_mcp_toolset() -> McpToolset:
    """Create a McpToolset connected to the GitHub MCP server."""
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in .env")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params)
    )


# =============================================================================
# OPTIONAL: File-based Configuration
# =============================================================================
def load_mcp_config() -> dict:
    """Load MCP server configuration from JSON file."""
    if not MCP_CONFIG_PATH.exists():
        raise FileNotFoundError(f"MCP config not found: {MCP_CONFIG_PATH}")

    with open(MCP_CONFIG_PATH) as f:
        config = json.load(f)

    # Replace environment variable placeholders
    github_config = config.get("mcpServers", {}).get("github", {})
    env = github_config.get("env", {})
    for key, value in env.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env[key] = os.getenv(env_var, "")

    return config


# TODO: Implement get_github_mcp_toolset_from_config()
# Load configuration from config/mcp_servers.json
#
# Example structure:
#
# def get_github_mcp_toolset_from_config() -> McpToolset:
#     config = load_mcp_config()
#     github = config["mcpServers"]["github"]
#
#     token = github["env"].get("GITHUB_PERSONAL_ACCESS_TOKEN")
#     if not token:
#         raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in .env")
#
#     server_params = StdioServerParameters(
#         command=github["command"],
#         args=github["args"],
#         env=github["env"]
#     )
#
#     return McpToolset(
#         connection_params=StdioConnectionParams(server_params=server_params)
#     )


# =============================================================================
# BONUS (+25 points) - Tool Search Pattern
# =============================================================================
# Implement defer_loading to reduce token usage by ~80%
#
# Why: GitHub MCP has 15+ tools (~8K tokens). Loading all upfront is wasteful.
# With defer_loading, tools are discovered on-demand (~1.5K tokens).
#
# Points breakdown:
# - search_github_tools function (10 pts)
# - defer_loading=True configured (10 pts)
# - create_agent_with_tool_search works (5 pts)
#
# Steps:
# 1. Create a search_github_tools tool that searches available MCP tools
# 2. Configure McpToolset with defer_loading=True
# 3. Keep only 1-2 frequently-used tools always loaded
#
# REQUIRED: In your reflection, compare context/token usage:
# - Run WITHOUT defer_loading, note context size (~8K tokens for 15+ tools)
# - Run WITH defer_loading, note context size (~1.5K tokens)
# - Calculate and report the % reduction
#
# Example structure:
#
# from google.adk.tools import FunctionTool
#
# def search_github_tools(query: str) -> dict:
#     """Search for available GitHub tools by keyword.
#
#     Args:
#         query: Search term (e.g., "issues", "repository", "pull request")
#
#     Returns:
#         dict with matching tool names and descriptions
#     """
#     # TODO: Implement tool search logic
#     pass
#
#
# def get_github_mcp_toolset_deferred() -> McpToolset:
#     """Create McpToolset with defer_loading for on-demand tool discovery."""
#     token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
#     if not token:
#         raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set")
#
#     server_params = StdioServerParameters(
#         command="npx",
#         args=["-y", "@modelcontextprotocol/server-github"],
#         env={"GITHUB_PERSONAL_ACCESS_TOKEN": token}
#     )
#
#     return McpToolset(
#         connection_params=StdioConnectionParams(server_params=server_params),
#         defer_loading=True  # Key: tools loaded on-demand
#     )


from google.adk.tools import ToolContext

_full_toolset_cache = None


def _get_full_toolset() -> McpToolset:
    """Return a cached, unfiltered McpToolset connected to GitHub.

    Cached at module level so repeated searches/calls don't respawn the
    GitHub MCP server process each time.
    """
    global _full_toolset_cache
    if _full_toolset_cache is None:
        _full_toolset_cache = get_github_mcp_toolset()
    return _full_toolset_cache


async def search_github_tools(query: str) -> dict:
    """Search GitHub tools by keyword before calling execute_github_tool.

    Args:
        query: Capability keywords (e.g. "repositories", "issues").

    Returns:
        dict with 'matched_tools' (name + description per match).
    """
    try:
        toolset = _get_full_toolset()
        all_tools = await toolset.get_tools()

        stopwords = {"the", "a", "an", "for", "of", "in", "on", "to", "and", "my"}
        query_words = [
            w for w in query.lower().split() if len(w) > 2 and w not in stopwords
        ]

        scored = []
        for t in all_tools:
            haystack = f"{t.name} {t.description or ''}".lower()
            score = sum(1 for word in query_words if word in haystack)
            if score > 0:
                scored.append((score, t))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        matches = [
            {"name": t.name, "description": t.description} for _, t in scored[:10]
        ]

        return {"status": "success", "matched_tools": matches, "count": len(matches)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def execute_github_tool(
    tool_name: str, tool_args: dict, tool_context: ToolContext
) -> dict:
    """Execute a specific GitHub tool by name, found via search_github_tools.

    Args:
        tool_name: The exact name of the tool to run, as returned by
            search_github_tools.
        tool_args: Dictionary of arguments to pass to that tool, matching
            its expected parameters.
        tool_context: Injected automatically by the agent framework.

    Returns:
        dict with 'status' and 'result' (the tool's raw output), or an
        error if the tool name wasn't found among the discovered tools.
    """
    try:
        toolset = _get_full_toolset()
        all_tools = await toolset.get_tools()
        target = next((t for t in all_tools if t.name == tool_name), None)
        if target is None:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found. Use search_github_tools first.",
            }

        result = await target.run_async(args=tool_args, tool_context=tool_context)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


mcp_tools = [
    # Add your McpToolset here after implementing one of the options above
    # Example: get_github_mcp_toolset()
    # Example: get_github_mcp_toolset_from_config(),
    get_github_mcp_toolset(),
]