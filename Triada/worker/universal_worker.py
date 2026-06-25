import asyncio
import httpx
from datetime import datetime
import os
import sys
import yaml

from Triada.common.models import Task, Heartbeat

class UniversalWorker:
    def __init__(self, worker_id, manager_url, skills_dir="Triada/skills/", agents_dir="agents/", llm_provider=None):
        self.worker_id = worker_id
        self.manager_url = manager_url
        self.skills_dir = skills_dir
        self.agents_dir = agents_dir
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

    def load_markdown_resource(self, resource_name, base_dir):
        # Support both resource_name and resource_name.md
        if not resource_name.endswith(".md"):
            resource_path = os.path.join(base_dir, f"{resource_name}.md")
        else:
            resource_path = os.path.join(base_dir, resource_name)

        if not os.path.exists(resource_path):
            # Also check if it's a directory containing SKILL.md (legacy skill structure)
            skill_dir_path = os.path.join(base_dir, resource_name, "SKILL.md")
            if os.path.exists(skill_dir_path):
                resource_path = skill_dir_path
            else:
                return None

        with open(resource_path, 'r') as f:
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
            # 1. Load Resources (Skills and Agent instructions)
            instructions_block = []

            # Load specific skills
            for skill_name in self.current_task.skills:
                skill = self.load_markdown_resource(skill_name, self.skills_dir)
                if skill:
                    instructions_block.append(f"Skill: {skill_name}\nInstructions: {skill['instructions']}")
                else:
                    # Try agents directory too
                    agent = self.load_markdown_resource(skill_name, self.agents_dir)
                    if agent:
                        instructions_block.append(f"Agent Persona: {skill_name}\nInstructions: {agent['instructions']}")

            # 2. Prepare Prompt
            system_prompt = f"You are a Universal Worker. Your task is: {self.current_task.title}\n\n"
            system_prompt += "Resource Instructions:\n" + "\n\n".join(instructions_block)

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
