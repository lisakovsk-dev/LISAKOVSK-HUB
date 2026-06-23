from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        pass

class MessengerProvider(ABC):
    @abstractmethod
    async def send_message(self, chat_id: str, text: str, **kwargs):
        pass

    @abstractmethod
    async def start(self, message_handler):
        pass

class StorageProvider(ABC):
    @abstractmethod
    async def save(self, collection: str, data: dict):
        pass

    @abstractmethod
    async def find(self, collection: str, query: dict):
        pass

class IntegrationProvider(ABC):
    @abstractmethod
    async def execute(self, action: str, **kwargs):
        pass
