import asyncio
import os
import sys
import json
import httpx

from Triada.common.models import Task

class Orchestrator:
    def __init__(self, llm_provider, messenger_provider, manager_url):
        self.llm = llm_provider
        self.messenger = messenger_provider
        self.manager_url = manager_url
        self.sessions = {} # chat_id -> state

    async def handle_request(self, chat_id: str, text: str):
        state = self.sessions.get(chat_id)

        if state and state.get("awaiting_confirmation"):
            if text.lower() in ["confirm", "yes", "подтверждаю", "да"]:
                await self.dispatch_tasks(chat_id, state["pending_tasks_json"])
                self.sessions[chat_id] = None
            elif text.lower() == "cancel":
                self.sessions[chat_id] = None
                await self.messenger.send_message(chat_id, "Request cancelled.")
            else:
                await self.messenger.send_message(chat_id, "Please confirm the plan (Yes/Confirm) or send 'cancel'.")
            return

        # 1-4: Analysis
        goal_prompt = f"Analyze request and define goal: {text}"
        goal = await self.llm.generate(goal_prompt, system_prompt="You are the AI Office Orchestrator.")

        # 5-10: Planning with 3 variants
        planning_prompt = f"""Decompose the goal into 3 solution variants (A, B, C) as per requirements.
Goal: {goal}

Each variant must include: Pros, Cons, Risks, Timeline.
Also, provide the DETAILED PLAN for the recommended variant in JSON format at the end.

Available Skills: web_search, report_generation, github_analysis, monetization_scan, architecture_review.

JSON Format for the plan:
[
  {{
    "title": "Task Title",
    "model": "deepseek-chat",
    "skills": ["web_search"],
    "instructions": ["Step 1", "Step 2"],
    "expected_output": "Markdown report"
  }}
]
"""
        full_response = await self.llm.generate(planning_prompt, system_prompt="You are the AI Office Planner.")

        # Present variants and JSON to user
        await self.messenger.send_message(chat_id, f"Goal: {goal}\n\n{full_response}\n\nDo you confirm the recommended plan? (Yes/No)")

        self.sessions[chat_id] = {
            "awaiting_confirmation": True,
            "goal": goal,
            "pending_tasks_json": full_response
        }

    async def dispatch_tasks(self, chat_id, full_text):
        await self.messenger.send_message(chat_id, "🚀 Dispatching tasks to Worker Pool...")
        try:
            # Extract JSON from the full response
            clean_json = full_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                parts = clean_json.split("```")
                for part in reversed(parts):
                    if part.strip().startswith("[") or part.strip().startswith("{"):
                        clean_json = part.strip()
                        break

            tasks_data = json.loads(clean_json)

            for t_data in tasks_data:
                task = Task(
                    title=t_data["title"],
                    model=t_data["model"],
                    skills=t_data["skills"],
                    instructions=t_data["instructions"],
                    expected_output=t_data["expected_output"]
                )
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.manager_url}/tasks/submit",
                        content=task.model_dump_json(),
                        headers={"Content-Type": "application/json"}
                    )

            await self.messenger.send_message(chat_id, f"✅ {len(tasks_data)} tasks queued successfully.")
        except Exception as e:
            await self.messenger.send_message(chat_id, f"❌ Error dispatching tasks: {e}")
