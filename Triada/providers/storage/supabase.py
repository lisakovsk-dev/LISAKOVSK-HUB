import os
import httpx
from typing import Any, Optional

class SupabaseAdapter:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def insert(self, table: str, data: dict) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/rest/v1/{table}",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def select(self, table: str, query_params: Optional[dict] = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/{table}",
                params=query_params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def update(self, table: str, data: dict, filters: dict) -> Any:
        # Simplistic filter implementation for MVP
        filter_str = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.url}/rest/v1/{table}?{filter_str}",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
