## Grade: 100 / 100

**Assignment:** Google Workspace Assistant + GitHub MCP (ADK)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-11  ·  Commit `4a1d963`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| tool_design | 18 | 18 | Option B chosen. 5 plain-function tools (list/create/complete/update/delete_task) with action-verb names, full Args/Returns docstrings, typed params (str/bool/int/Optional), all collected into the tasks_tools list (tasks_tools.py:166). Exceeds the 3-tool minimum. (`workspace_assistant/tools/tasks_tools.py:18`) |
| agent_instructions | 14 | 14 | System instruction is clear and scoped: names all five tools, sets default list behavior (active only, by due date), and mandates confirm-before-change for create/update/delete plus confirm-before-complete when inferred. Safe behavior well covered. (`workspace_assistant/agent.py:25`) |
| error_handling | 14 | 14 | Every tool wraps its API call in try/except returning a consistent {status, message} dict (e.g. tasks_tools.py:43-44). update_task adds an explicit edge-case guard returning an error when no fields are supplied (tasks_tools.py:135-136). (`workspace_assistant/tools/tasks_tools.py:135`) |
| functionality | 14 | 14 | Static read: correct Google Tasks API usage via get_tasks_service — tasks().list/insert/patch/delete. complete_task patches status='completed' (tasks_tools.py:91-99); create/update build request bodies conditionally. Operations match intent. (`workspace_assistant/tools/tasks_tools.py:91`) |
| code_quality | 10 | 10 | Readable, organized, well-documented. Tools wired into an LlmAgent via create_agent() (agent.py:54-59). DRY _base_instruction() helper shared by both agent factories avoids instruction duplication. (`workspace_assistant/agent.py:37`) |
| mcp_configured | 10 | 10 | get_github_mcp_toolset() builds an McpToolset over StdioConnectionParams/StdioServerParameters running the GitHub MCP server via npx (mcp_tools.py:48-62), and it is attached to the agent through tasks_tools + mcp_tools (agent.py:58). (`workspace_assistant/tools/mcp_tools.py:48`) |
| github_queries | 15 | 15 | Static read: the full McpToolset is added to the agent's tools (agent.py:58; mcp_tools.py:257), exposing all GitHub queries (repos, issues, PRs). Instruction directs listing repos, showing issues, and creating issues with confirmation (agent.py:46). Correctly wired through the toolset. (`workspace_assistant/agent.py:58`) |
| mcp_error_handling | 5 | 5 | Missing GITHUB_PERSONAL_ACCESS_TOKEN raises a clear ValueError (mcp_tools.py:50-52). The bonus search/execute wrappers also try/except MCP failures and execute_github_tool validates the tool name before calling (mcp_tools.py:241-245). (`workspace_assistant/tools/mcp_tools.py:50`) |
| _bonus_ | +25 | +15 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- Complete Option B implementation: all 5 task tools as plain functions with action-verb names, full Args/Returns docstrings, and correctly typed parameters, collected into tasks_tools (tasks_tools.py:18-172).
- Consistent, thoughtful error handling — uniform {status, message} contract on every tool plus an explicit no-op guard in update_task (tasks_tools.py:135-136) and a tool-name existence check in execute_github_tool (mcp_tools.py:241-245).
- Clean, DRY agent design: a shared _base_instruction() helper feeds both create_agent() and the bonus tool-search agent, and the system instruction gives precise confirm-before-change safety rules (agent.py:22-48).
- Strong, honest reflection: verifies library behavior against source, explains why defer_loading=True was unavailable, and measures an 87.4% tool-token reduction using ADK's real declaration pipeline (reflection_template.md:28-30, 68-80).

### What to improve (actionable)
- The defer_loading=True bonus (10 pts) is not earned because the flag is never set in code. Since google-adk 2.3.0 lacks the parameter, a brief in-code comment at the toolset construction pointing to the manual search/execute deferral would make the equivalence obvious to a grader reading only mcp_tools.py.
- search_github_tools uses literal word-overlap scoring; queries like 'PR' or 'commit history' will miss list_pull_requests / list_commits. Add synonym or fuzzy matching (the student already notes this in the reflection).
- execute_github_tool passes tool_args straight through; validating them against the target tool's input schema before the call would surface malformed-argument errors more clearly.
- calendar_tools.py is left as the original stub — harmless since Option B was chosen, but removing or clearly marking the unused option file would reduce clutter.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1596 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `4a1d963` · delivered 2026-07-11T18:01:07Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
