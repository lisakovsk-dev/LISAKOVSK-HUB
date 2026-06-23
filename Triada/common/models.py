from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class Task(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    priority: str = "normal"
    model: str
    skills: List[str]
    tools: List[str] = []
    context: Dict = {}
    instructions: List[str]
    expected_output: str
    status: str = "pending" # pending, in_progress, completed, failed
    result: Optional[str] = None
    worker_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class WorkerStatus(BaseModel):
    worker_id: str
    worker_name: str
    status: str = "idle" # idle, working, offline
    profile: str = "universal"
    last_heartbeat: datetime = Field(default_factory=datetime.now)
    current_task_id: Optional[str] = None

class Heartbeat(BaseModel):
    worker_id: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
