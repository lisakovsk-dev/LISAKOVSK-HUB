import asyncio
import httpx
from datetime import datetime
import os
import sys
import yaml

from Triada.common.models import Task, Heartbeat

class UniversalWorker:
    def __init__(self, worker_id, manager_url, skills_dir="Triada/skills/", llm_provider=None):
        self.worker_id = worker_id
        self.manager_url = manager_url
        self.skills_dir = skills_dir
        self.llm = llm_provider
        self.status = "idle"
        self.current_task = None
        self.stop_event = asyncio.Event()

    async def send_heartbeat(self):
        while not self.stop_event.is_set():
            heartbeat = {
                "worker_id": self.worker_id,
                "status": self.status,
                "timestamp": datetime.now().isoformat()
            }
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{self.manager_url}/heartbeat", json=heartbeat)
            except Exception as e:
                print(f"Failed to send heartbeat: {e}")
            await asyncio.sleep(10)

    async def fetch_task(self):
        while not self.stop_event.is_set():
            if self.status == "idle":
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{self.manager_url}/tasks/next?worker_id={self.worker_id}")
                        if response.status_code == 200:
                            task_data = response.json()
                            if task_data:
                                self.current_task = Task(**task_data)
                                await self.process_task()
                except Exception as e:
                    print(f"Failed to fetch task: {e}")
            await asyncio.sleep(5)

    def load_skill(self, skill_name):
        skill_path = os.path.join(self.skills_dir, skill_name, "SKILL.md")
        if not os.path.exists(skill_path):
            return None

        with open(skill_path, 'r') as f:
            content = f.read()

        if content.startswith('---'):
            parts = content.split('---')
            if len(parts) >= 3:
                meta = parts[1]
                instructions = "---".join(parts[2:])
                return {
                    "metadata": yaml.safe_load(meta),
                    "instructions": instructions.strip()
                }
        return {"metadata": {}, "instructions": content.strip()}

    async def process_task(self):
        self.status = "working"
        print(f"Worker {self.worker_id} processing task {self.current_task.id}")

        try:
            # 1. Load Skills
            skill_instructions = []
            for skill_name in self.current_task.skills:
                skill = self.load_skill(skill_name)
                if skill:
                    skill_instructions.append(f"Skill: {skill_name}\nInstructions: {skill['instructions']}")

            # 2. Prepare Prompt
            system_prompt = f"You are a Universal Worker. Your task is: {self.current_task.title}\n\n"
            system_prompt += "Skills Instructions:\n" + "\n\n".join(skill_instructions)

            prompt = f"Context: {self.current_task.context}\n"
            prompt += f"Instructions: {self.current_task.instructions}\n"
            prompt += f"Expected Output: {self.current_task.expected_output}"

            # 3. Execute via LLM
            if self.llm:
                result = await self.llm.generate(prompt, system_prompt=system_prompt, model=self.current_task.model)
            else:
                result = "LLM Provider not configured"

            # 4. Return Report
            report = {
                "task_id": self.current_task.id,
                "status": "completed",
                "result": result,
                "worker_id": self.worker_id,
                "timestamp": datetime.now().isoformat()
            }

            async with httpx.AsyncClient() as client:
                await client.post(f"{self.manager_url}/tasks/report", json=report)

        except Exception as e:
            print(f"Task failed: {e}")
            error_report = {
                "task_id": self.current_task.id,
                "status": "failed",
                "error": str(e),
                "worker_id": self.worker_id
            }
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.manager_url}/tasks/report", json=error_report)

        self.status = "idle"
        self.current_task = None

    async def run(self):
        print(f"Worker {self.worker_id} started.")
        await asyncio.gather(
            self.send_heartbeat(),
            self.fetch_task()
        )
