import asyncio
from qanot import Qanot, Config

async def main():
    config = Config.from_env()
    agent = Qanot(config)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())