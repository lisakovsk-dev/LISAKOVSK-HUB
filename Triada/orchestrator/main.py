import asyncio
import os
import sys
from Triada.common.config import Config
from Triada.providers.llm.openrouter import OpenRouterAdapter
from Triada.providers.messenger.telegram import TelegramAdapter
from Triada.orchestrator.orchestrator_core import Orchestrator

async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "../common/settings.yaml")
    config = Config(config_path)

    llm = OpenRouterAdapter(
        api_key=config.get("llm.api_key"),
        model=config.get("llm.model", "openai/gpt-4o")
    )

    messenger = TelegramAdapter(token=config.get("telegram.token"))
    manager_url = config.get("manager.url", "http://localhost:8000")

    orchestrator = Orchestrator(
        llm_provider=llm,
        messenger_provider=messenger,
        manager_url=manager_url
    )

    print("Orchestrator starting...")
    await messenger.start(orchestrator.handle_request)

if __name__ == "__main__":
    asyncio.run(main())
