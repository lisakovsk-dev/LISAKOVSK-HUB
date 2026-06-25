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
        self.identity = "You are Jules, an extremely skilled software engineer. You are the Triada Orchestrator."

    async def handle_request(self, chat_id: str, text: str):
        state = self.sessions.get(chat_id)

        # 11. Confirmation check
        if state and state.get("awaiting_confirmation"):
            if text.lower() in ["confirm", "yes", "подтверждаю", "да", "a", "b", "c", "а", "б", "в"]:
                # If they just said 'yes', we use the recommended one (usually A or specified in state)
                chosen_variant = text.lower()
                if chosen_variant in ["confirm", "yes", "подтверждаю", "да"]:
                    chosen_variant = state.get("recommended_variant", "a")

                # Logic to map variant to specific task list
                await self.dispatch_tasks(chat_id, state["variants"][chosen_variant]["plan_json"])
                self.sessions[chat_id] = None
            elif text.lower() == "cancel":
                self.sessions[chat_id] = None
                await self.messenger.send_message(chat_id, "Request cancelled.")
            else:
                await self.messenger.send_message(chat_id, "Please confirm the plan (A/B/C or Yes/Confirm) or send 'cancel'.")
            return

        # Mandatory 11-step cycle (logical flow)
        # 1. Understand request, 2. Define goal, 3. Info gathering, 4. Search
        analysis_prompt = f"""You are Jules. Follow the mandatory 11-step cycle.
1. Understand: {text}
2. Define Goal.
3. Check if info is missing.
4. Perform search if needed.

Output ONLY the DEFINED GOAL and a brief analysis.
"""
        goal_analysis = await self.llm.generate(analysis_prompt, system_prompt=self.identity)

        # 5. Decomposition, 6. Skill Audit, 7. Skill Check, 8. Solution Variants, 9. Plan preparation
        planning_prompt = f"""Based on the Goal: {goal_analysis}

Perform steps 5-9:
5. Decomposition.
6. Skill Audit (Available: web_search, report_generation, github_analysis, monetization_scan, architecture_review).
7. Check Skill availability.
8. Formulate 3 variants (A, B, C).
   Variant A: Pros, Cons, Risks, Timeline.
   Variant B: Pros, Cons, Risks, Timeline.
   Variant C: Pros, Cons, Risks, Timeline.
9. Prepare detailed plans for each.

Output the 3 variants for the user in a readable format.
Then, at the end, provide a JSON block containing the task lists for each variant.

Recommended Variant: A

JSON Format:
```json
{{
  "a": [ {{ "title": "...", "model": "...", "skills": [...], "instructions": [...], "expected_output": "..." }} ],
  "b": [ ... ],
  "c": [ ... ]
}}
```
"""
        full_planning_response = await self.llm.generate(planning_prompt, system_prompt=self.identity)

        # 10. Show plan to user
        display_text = f"🎯 Goal: {goal_analysis}\n\n{full_planning_response}\n\nWhich variant do you choose? (A/B/C)"
        await self.messenger.send_message(chat_id, display_text)

        # Parse JSON from response
        try:
            clean_json = full_planning_response.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()

            variants_data = json.loads(clean_json)

            self.sessions[chat_id] = {
                "awaiting_confirmation": True,
                "goal": goal_analysis,
                "variants": {
                    "a": {"plan_json": variants_data.get("a", [])},
                    "b": {"plan_json": variants_data.get("b", [])},
                    "c": {"plan_json": variants_data.get("c", [])},
                    "а": {"plan_json": variants_data.get("a", [])},
                    "б": {"plan_json": variants_data.get("b", [])},
                    "в": {"plan_json": variants_data.get("c", [])}
                },
                "recommended_variant": "a"
            }
        except Exception as e:
            print(f"Error parsing planning JSON: {e}")
            await self.messenger.send_message(chat_id, "⚠️ Error in plan generation. Please try again.")

    async def dispatch_tasks(self, chat_id, tasks_data):
        if not tasks_data:
            await self.messenger.send_message(chat_id, "❌ No tasks to dispatch.")
            return

        await self.messenger.send_message(chat_id, f"🚀 Dispatching {len(tasks_data)} tasks to Worker Pool...")
        try:
            for t_data in tasks_data:
                task = Task(
                    title=t_data["title"],
                    model=t_data.get("model", "deepseek-chat"),
                    skills=t_data.get("skills", []),
                    instructions=t_data.get("instructions", []),
                    expected_output=t_data.get("expected_output", "Markdown")
                )
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.manager_url}/tasks/submit",
                        content=task.model_dump_json(),
                        headers={"Content-Type": "application/json"}
                    )

            await self.messenger.send_message(chat_id, f"✅ Tasks queued successfully.")
        except Exception as e:
            await self.messenger.send_message(chat_id, f"❌ Error dispatching tasks: {e}")
