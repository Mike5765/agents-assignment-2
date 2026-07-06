# Assignment 2 Reflection

**Name:** Michael Kelley   
**Option:** B - task tools
**Date:** 7/5/26

---

## Tool Design Decisions

### Tools Implemented
1. **list_tasks**: Retrieves tasks from a Google Tasks list, showing active tasks by default
2. **create_task**: Adds a new task with a title, optional notes, and optional due date
3. **complete_task**: Marks an existing task as done
4. **update_task**: Modifies the title, notes, or due date of an existing task
5. **delete_task**: Permanently removes a task

### Why These Tools?
The assignment required a minimum of 3 tools, but I chose to implement all 5 suggested tools instead of stopping at the minimum. A task manager that can only list and create tasks, but not update or delete them, felt incomplete for real use. Users need the full cycle of a task (create it, track it, change it, finish it, or remove it if it's no longer relevant) to actually replace a real to-do app. Building the full set also gave me more to reason about for tool design consistency, since update_task and delete_task both needed to handle edge cases the simpler tools didn't (e.g., what happens if no fields are provided to update_task).

### Description Strategy
I named each function with a clear action verb matching how a user would naturally phrase a request (e.g., "show my tasks" maps to list_tasks, "add a task" maps to create_task). Each docstring's first sentence explains specifically when the LLM should reach for that tool, for example, complete_task's docstring distinguishes between the user explicitly saying a task is done versus the model inferring it from context, since those two cases needed different behavior per my system instruction. I also documented the exact shape of each tool's return dict (e.g., "dict with 'status' and 'tasks'") so the model would know which fields to reference when generating its response back to the user, rather than guessing at the structure.

---

## Challenges Encountered

### Challenge 1: defer_loading Parameter Didn't Exist
- **Problem:** The bonus section instructions told me to configure McpToolset with `defer_loading=True` to implement the Tool Search pattern. When I checked the actual constructor signature of McpToolset in my installed google-adk version (2.3.0), that parameter didn't exist at all, it would have thrown a TypeError immediately.
- **Solution:** Instead of guessing at a workaround, I inspected the real McpToolset API and found two things that did exist: a `tool_filter` parameter, and an async `get_tools()` method that returns every tool a server exposes. Rather than hardcoding a static subset of "commonly used" tools with `tool_filter` (which I realized would defeat the actual point of the assignment, the LLM is supposed to dynamically decide which tools it needs, not have that decision made for it in advance), I built two generic functions instead: `search_github_tools`, which calls `get_tools()` and returns matching tool names/descriptions for a keyword, and `execute_github_tool`, which looks up and calls any tool by the exact name the search returned. This meant the agent's context only ever holds these 2 generic tool definitions instead of the GitHub server's full 26, while the LLM genuinely discovers and picks a different tool name depending on what's actually being asked — I verified this by running different queries (repos vs. issues) and confirming two different tool names got resolved dynamically each time, not a fixed hardcoded pair.

### Challenge 2: main.py Session Bug
- **Problem:** Running `python main.py --interactive` (the provided CLI entry point I wasn't allowed to edit) threw a `SessionNotFoundError` on the very first message. 
- **Solution:** I traced this by reading the actual `Runner._get_or_create_session` source code directly, which showed sessions only auto-create if `auto_create_session=True` is passed to the Runner — and that parameter defaults to `False`. `main.py` never sets it, and `InMemoryRunner` (which `main.py` uses) doesn't even expose that parameter to be set. I checked across every google-adk version from 1.0.0 through the current 2.3.0 and found that no version has ever auto-created a session, meaning this wasn't a version-drift issue, but a genuine bug in the provided scaffolding (it's missing an explicit `session_service.create_session()` call before `runner.run()`). Since main.py is a "do not edit" file, I couldn't fix it directly. I wrote a small standalone test script (not part of any graded file) that explicitly creates the session first, which let me verify my actual agent implementation works correctly end-to-end. I also flagged this to my instructor, since it's a bug outside my control that could affect anyone grading by running main.py directly.

---

## Error Handling Approach

Every tool I wrote follows the same pattern: a try/except block wraps the actual API call, and both the success and error paths return the same dict shape — `{"status": "success", ...}` or `{"status": "error", "message": "..."}`. I anticipated the main failure modes being network issues, invalid IDs (e.g., trying to update or delete a task that doesn't exist), and expired or missing OAuth credentials. By always returning a consistent structure regardless of success or failure, the agent can reliably check `status` and decide how to respond to the user, rather than the whole program crashing on an unexpected exception mid-conversation.

For update_task specifically, I added an extra guard clause that checks whether any fields were actually provided before making an API call — if someone calls update_task with no title, notes, or due date changes, it returns an error immediately ("No fields provided to update.") instead of sending a pointless empty request to Google's API.

For the GitHub bonus tools, execute_github_tool also checks whether the requested tool_name actually exists among the discovered tools before trying to call it, returning a clear error message directing the model back to search_github_tools if the name doesn't match anything, rather than failing with a confusing internal error.

---

## Ideas for Improvement

If you had more time, what would you add or change?

1. Fix the main.py session bug properly, since I now understand exactly what's wrong (missing an explicit session_service.create_session() call before runner.run()) but wasn't able to edit that file for this assignment.
2. Improve search_github_tools with semantic/fuzzy matching instead of literal word matching, so queries like "PR" or "commit history" correctly find tools like list_pull_requests or list_commits without requiring exact keyword overlap.
3. Validate tool_args against the target tool's actual input schema inside execute_github_tool before making the real API call, so malformed arguments produce a clear, actionable error immediately instead of surfacing whatever error message the MCP server happens to return.

---

## Key Learnings

This assignment made concrete something I'd only understood theoretically before: LLMs are excellent at reasoning and language, but genuinely unreliable at precise, mechanical tasks like exact math or knowing real-time information, which is exactly why tool use exists. Giving the model a calculator or an API call instead of asking it to compute or recall something directly is one of the most important ideas in making LLMs actually useful in production, rather than just impressive in a demo.

But implementing tools isn't free, it comes with its own scaling problem. Building the GitHub MCP bonus made this very real for me: connecting to a single MCP server exposed 26 tools, and loading every one of their full schemas into context by default cost over 6,700 tokens before the conversation even started. This is exactly the problem Anthropic's Tool Search and lazy-loading pattern was built to solve, and building my own small version of it (search_github_tools + execute_github_tool) rather than just reading about the concept made the "why" behind it click in a way it hadn't before, I measured an 87% reduction in tool-definition tokens using the exact same conversion pipeline the real agent uses, which is a genuinely large, real cost that scales badly the more tools an agent has access to.

The biggest takeaway is that tool use turns an LLM from something that talks about the world into something that can actually act in it, and the design space for what that unlocks is enormous. But this assignment also taught me that the tooling ecosystem around agents (ADK, MCP, the various SDKs) is still young and changes fast, I hit real discrepancies between what the course scaffolding assumed and what the actual installed libraries supported multiple times, which meant I had to learn to verify library behavior directly against source code rather than trust documentation or assignment instructions at face value. That's probably the most transferable skill from this whole project, beyond the specific ADK/MCP mechanics themselves.

---

## Comparison: Token/Context Bloat

To measure this accurately, I used ADK's actual internal tool-declaration pipeline (`FunctionTool._get_declaration()` / `MCPTool._get_declaration()` converted via `function_declaration_to_tool_param()`) rather than approximating the schemas by hand, then counted tokens using Anthropic's real `count_tokens()` API against the model actually powering the agent (claude-sonnet-5). This ensures the numbers reflect exactly what gets sent to the model in a real request, not an estimate.

| Mode | Tools Loaded | Tokens |
|---|---|---|
| Without tool search (create_agent) | 26 GitHub MCP tools, full schemas | 6,737 |
| With tool search (create_agent_with_tool_search) | 2 tools (search_github_tools + execute_github_tool) | 850 |
| **Savings** | | **87.4%** |

My first attempt at this measurement used hand-built approximate schemas rather than the real ones ADK generates, which significantly undercounted the "before" number (1,884 tokens instead of the real 6,737) — real MCP tool schemas include nested JSON schema detail (types, enums, nested properties) that a simplified approximation misses. Correcting the methodology to use ADK's actual internal conversion functions produced a result that is both more accurate and, notably, higher than the assignment's own ~80% example figure.

The measurement script is available at `workspace_assistant/measure_tokens.py` in the project root for reproducibility.