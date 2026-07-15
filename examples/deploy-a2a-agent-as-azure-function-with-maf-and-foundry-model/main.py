import os

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from agent_framework_a2a import A2AExecutor
from agent_framework_foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv()

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "9999"))
SERVER_URL = os.getenv("SERVER_URL", f"http://{HOST}:{PORT}/")

agent_card = AgentCard(
    name="General Assistant",
    description="A general-purpose AI assistant powered by Azure AI Foundry.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url=SERVER_URL, protocol_binding="JSONRPC"),
    ],
    skills=[],
)

_client = FoundryChatClient(credential=DefaultAzureCredential())
_agent = _client.as_agent(
    name="General Assistant",
    instructions="You are a helpful general-purpose AI assistant.",
)

_request_handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(_agent, stream=True),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(_request_handler, "/"),
    ],
)


def main() -> None:
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
