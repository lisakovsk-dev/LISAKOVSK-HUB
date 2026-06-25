import asyncio
import os
import sys
from Triada.common.config import Config
from Triada.providers.llm.openrouter import OpenRouterAdapter
from Triada.worker.universal_worker import UniversalWorker

async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "../common/settings.yaml")
    config = Config(config_path)

    worker_id = os.getenv("WORKER_ID", "worker-01")
    manager_url = config.get("manager.url", "http://localhost:8000")

    llm = OpenRouterAdapter(
        api_key=config.get("llm.api_key"),
        model=config.get("llm.model", "openai/gpt-4o")
    )

    # Skills dir relative to repo root
    skills_dir = os.path.join(base_dir, "../skills")

    worker = UniversalWorker(
        worker_id=worker_id,
        manager_url=manager_url,
        skills_dir=skills_dir,
        llm_provider=llm
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
