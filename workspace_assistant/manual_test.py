import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
from agent import create_agent

async def main():
    agent = create_agent()
    runner = InMemoryRunner(agent=agent)
    await runner.session_service.create_session(
        app_name=runner.app_name, user_id="user", session_id="session"
    )
    message = genai_types.Content(role="user", parts=[genai_types.Part(text="List repositories for GitHub user Mike5765")])
    async for event in runner.run_async(user_id="user", session_id="session", new_message=message):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)

asyncio.run(main())