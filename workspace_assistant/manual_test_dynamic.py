import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
from agent import create_agent_with_tool_search


async def run_query(runner, query: str):
    print(f"\n{'='*60}\nQUERY: {query}\n{'='*60}")
    message = genai_types.Content(role="user", parts=[genai_types.Part(text=query)])
    async for event in runner.run_async(user_id="user", session_id="session", new_message=message):
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.function_call:
                print(f"  [TOOL CALL] {part.function_call.name}({dict(part.function_call.args)})")
            elif part.function_response:
                print(f"  [TOOL RESULT] {part.function_response.name} -> {str(part.function_response.response)[:200]}")
            elif part.text:
                print(f"  [MODEL TEXT] {part.text}")


async def main():
    agent = create_agent_with_tool_search()
    runner = InMemoryRunner(agent=agent)
    await runner.session_service.create_session(
        app_name=runner.app_name, user_id="user", session_id="session"
    )

    test_queries = [
        "List repositories for GitHub user Mike5765",
        "Show open issues in Mike5765/agents-assignment-2",
        "What are my Google tasks?",
    ]

    for query in test_queries:
        await run_query(runner, query)


asyncio.run(main())