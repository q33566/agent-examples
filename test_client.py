"""Manual test script — run with the server already started on port 9999."""

import asyncio

from agent_framework import AgentSession
from agent_framework_a2a import A2AAgent


async def main() -> None:
    server_url = "http://localhost:9999/"

    async with A2AAgent(url=server_url, name="General Assistant") as agent:
        session = AgentSession()

        # First turn
        print("--- Turn 1 ---")
        response = await agent.run("What is the capital of France?", session=session)
        for msg in response.messages:
            for content in msg.contents:
                if content.type == "text":
                    print(f"Agent: {content.text}")

        # Second turn (same session — tests context continuity)
        print("\n--- Turn 2 ---")
        response = await agent.run("And what is its most famous landmark?", session=session)
        for msg in response.messages:
            for content in msg.contents:
                if content.type == "text":
                    print(f"Agent: {content.text}")


if __name__ == "__main__":
    asyncio.run(main())
