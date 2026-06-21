import asyncio
from qanot import QanotAgent

async def main():
    # Создаем агента
    agent = QanotAgent()
    # Запускаем бота
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())