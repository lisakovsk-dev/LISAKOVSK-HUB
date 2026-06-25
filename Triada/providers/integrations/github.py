import httpx
from typing import Any, Optional

class GitHubAdapter:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_file_content(self, path: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/contents/{path}",
                headers=self.headers
            )
            if response.status_code == 200:
                import base64
                data = response.json()
                return base64.b64decode(data['content']).decode('utf-8')
            return None

    async def list_files(self, path: str = "") -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/contents/{path}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
