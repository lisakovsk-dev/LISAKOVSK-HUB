import httpx
from typing import Any

class NotionAdapter:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    async def query_database(self, database_id: str) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.notion.com/v1/databases/{database_id}/query",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def create_page(self, parent_id: str, properties: dict) -> Any:
        payload = {
            "parent": {"database_id": parent_id},
            "properties": properties
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/pages",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
