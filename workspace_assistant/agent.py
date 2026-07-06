"""
Google Workspace Assistant - Main Agent Definition

Part 1: Implement tools and system instruction for Calendar OR Tasks
Part 2: Add McpToolset for GitHub integration
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.models.anthropic_llm import AnthropicLlm
from tools.mcp_tools import search_github_tools, execute_github_tool

from config.settings import Settings

# TODO: Import your chosen tool set
# from tools.calendar_tools import calendar_tools
from tools.tasks_tools import tasks_tools

# TODO Part 2: Import MCP tools
from tools.mcp_tools import mcp_tools


def _base_instruction() -> str:
    """Shared Tasks-related instruction text, reused by both create_agent()
    and create_agent_with_tool_search() so the rules only live in one place."""
    return """You are a Tasks Manager assistant that helps users organize and track their to-do items using Google Tasks.

You have access to five tools: list_tasks, create_task, complete_task, update_task, and delete_task.

Follow these rules:
- When listing tasks, show only active (incomplete) tasks by default, ordered by due date. Do not show completed or past tasks unless the user explicitly asks to see them.
- Before creating a new task, confirm the title, notes, and due date with the user to make sure the details are correct.
- If the user explicitly says a task is done or asks you to mark it complete, complete it directly. If you infer from conversation that a task might be finished but the user hasn't said so directly, confirm with the user before marking it complete.
- Before updating a task's title, notes, or due date, confirm the specific changes with the user first.
- Before deleting a task, always confirm with the user first, since deletion is permanent and cannot be undone."""


def create_agent() -> LlmAgent:
    """Create the Workspace Assistant agent."""
    settings = Settings()

    # TODO Part 1: Write your system instruction
    instruction = _base_instruction() + """

You also have access to GitHub tools for managing repositories and issues. You can list the user's repositories, show open issues in a repository, and create new issues when asked. Always confirm the repository name and issue details before creating a new issue.

Be clear and concise in your responses, and always tell the user what action you took or are about to take."""

    # TODO Part 2: Create McpToolset for GitHub

    # TODO: Create and return your LlmAgent
    return LlmAgent(
        name="workspace_assistant",
        model=AnthropicLlm(model=settings.model_name),
        instruction=instruction,
        tools=tasks_tools + mcp_tools,
    )

    # raise NotImplementedError("Implement create_agent")


def create_agent_with_tool_search() -> LlmAgent:
    """BONUS: Create agent with defer_loading for tool search."""
    settings = Settings()

    instruction = _base_instruction() + """

You also have access to GitHub capabilities, but the specific tools are not loaded by default to save context. When the user asks for something GitHub-related, first call search_github_tools with a keyword describing what you need (e.g. "repositories", "issues", "create issue") to discover the exact tool name and its parameters, then call execute_github_tool with that tool name and the correct arguments to actually perform the action.

Be clear and concise in your responses, and always tell the user what action you took or are about to take."""

    return LlmAgent(
        name="workspace_assistant_tool_search",
        model=AnthropicLlm(model=settings.model_name),
        instruction=instruction,
        tools=tasks_tools + [search_github_tools, execute_github_tool],
    )