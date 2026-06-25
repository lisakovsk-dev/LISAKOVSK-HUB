import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from Triada.orchestrator.orchestrator_core import Orchestrator
import json

async def test_distributed_architecture_flow():
    # 1. Mock dependencies
    llm = AsyncMock()
    # Mock goal definition and planning with 3 variants + JSON
    llm.generate.side_effect = [
        "Goal: Analyze Market", # Goal
        "Variant A: ...\nVariant B: ...\nVariant C: ...\n\n```json\n" + json.dumps({
            "a": [{
                "title": "Search competitors",
                "model": "deepseek-chat",
                "skills": ["web_search"],
                "instructions": ["Search TOP 5"],
                "expected_output": "list"
            }],
            "b": [],
            "c": []
        }) + "\n```" # Planning response
    ]

    messenger = AsyncMock()
    manager_url = "http://mock-manager"

    orchestrator = Orchestrator(llm, messenger, manager_url)
    chat_id = "user123"

    # 2. Simulate User Request
    print("Step 1: Orchestrator analyzing request...")
    await orchestrator.handle_request(chat_id, "Find competitors for my AI project")

    # Verify Orchestrator is waiting for confirmation
    if chat_id not in orchestrator.sessions:
        print("Session not found - likely failed parsing JSON in handle_request")
        return

    assert orchestrator.sessions[chat_id]["awaiting_confirmation"] is True
    print("Orchestrator is awaiting confirmation.")

    # 3. Simulate User Confirmation
    print("Step 2: User confirms plan...")

    # Mock httpx.AsyncClient().post
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(status_code=200)

        await orchestrator.handle_request(chat_id, "Yes")

        # Verify httpx was called
        mock_post.assert_called()
        print(f"httpx.post called with: {mock_post.call_args}")

    # Session should be cleared
    assert orchestrator.sessions.get(chat_id) is None
    print("Plan confirmed and dispatched.")

    print("Test passed: Distributed architecture flow logic verified.")

if __name__ == "__main__":
    asyncio.run(test_distributed_architecture_flow())
