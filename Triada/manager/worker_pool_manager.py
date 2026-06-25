from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import asyncio
import os
import sys
from contextlib import asynccontextmanager

from Triada.common.models import WorkerStatus, Heartbeat, Task

# In-memory storage
workers = {} # worker_id -> WorkerStatus
task_queue = [] # List of Tasks
in_progress_tasks = {} # task_id -> Task
results = {} # task_id -> dict (report)

async def monitor_offline_workers():
    while True:
        # Trigger the worker list update which handles requeueing
        now = datetime.now()
        for w_id, w in list(workers.items()):
            if now - w.last_heartbeat > timedelta(seconds=30):
                w.status = "offline"
                # If worker had a task, requeue it
                if w.current_task_id:
                    task_id = w.current_task_id
                    if task_id in in_progress_tasks:
                        task = in_progress_tasks.pop(task_id)
                        task.status = "pending"
                        task.worker_id = None
                        task_queue.insert(0, task)
                        print(f"Requeued task {task_id} from offline worker {w_id}")
                    w.current_task_id = None
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    monitor_task = asyncio.create_task(monitor_offline_workers())
    yield
    # Shutdown logic
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.post("/heartbeat")
async def receive_heartbeat(heartbeat: Heartbeat):
    if heartbeat.worker_id not in workers:
        workers[heartbeat.worker_id] = WorkerStatus(
            worker_id=heartbeat.worker_id,
            worker_name=f"Worker {heartbeat.worker_id}",
            status=heartbeat.status
        )
    else:
        workers[heartbeat.worker_id].status = heartbeat.status
        workers[heartbeat.worker_id].last_heartbeat = heartbeat.timestamp

    return {"status": "ok"}

@app.get("/workers")
async def list_workers():
    return list(workers.values())

@app.get("/tasks/next")
async def get_next_task(worker_id: str):
    if not task_queue:
        return None

    # Simple FIFO for now
    task = task_queue.pop(0)
    task.status = "in_progress"
    task.worker_id = worker_id

    in_progress_tasks[task.id] = task

    if worker_id in workers:
        workers[worker_id].status = "working"
        workers[worker_id].current_task_id = task.id

    return task

@app.post("/tasks/report")
async def receive_report(report: dict):
    task_id = report.get("task_id")
    results[task_id] = report

    if task_id in in_progress_tasks:
        in_progress_tasks.pop(task_id)

    worker_id = report.get("worker_id")
    if worker_id in workers:
        workers[worker_id].status = "idle"
        workers[worker_id].current_task_id = None

    return {"status": "ok"}

@app.post("/tasks/submit")
async def submit_task(task: Task):
    task_queue.append(task)
    return {"status": "queued", "task_id": task.id}

@app.get("/tasks/result/{task_id}")
async def get_task_result(task_id: str):
    return results.get(task_id)
