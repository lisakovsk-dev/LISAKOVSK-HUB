from Triada.providers.base import MessengerProvider
import asyncio
from aiogram import Bot, Dispatcher, types

class TelegramAdapter(MessengerProvider):
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

    async def send_message(self, chat_id: str, text: str, **kwargs):
        await self.bot.send_message(chat_id, text, **kwargs)

    async def start(self, message_handler):
        @self.dp.message()
        async def handle(message: types.Message):
            await message_handler(str(message.chat.id), message.text)

        print("Starting Telegram polling...")
        await self.dp.start_polling(self.bot)
