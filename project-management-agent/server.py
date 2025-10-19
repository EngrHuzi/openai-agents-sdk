from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
import uuid


class Task(BaseModel):
    title: str
    description: str
    assignee: str
    due_date: str  # ISO or friendly format
    status: Optional[str] = Field(default="To Do")
    task_id: Optional[str] = None

class TaskUpdate(BaseModel):
    task_id: str
    new_status: Optional[str] = None
    new_due_date: Optional[str] = None

class Meeting(BaseModel):
    meeting_id: str
    new_time: str

class DailySummaryResponse(BaseModel):
    status: str
    summary: str
    details: Dict[str, int]
    generated_at: str

# =================================
# 🧠 Fake In-Memory DB
# =================================
TASK_DB: Dict[str, Task] = {}
MEETING_DB: Dict[str, str] = {}

# =================================
# 🚀 MCP App
# =================================
mcp = FastMCP(
    name="ProjectManagementAgent",
    stateless_http=True,
)

# =================================
# 🛠️ Helper Functions
# =================================
def parse_due_date(date_str: str) -> str:
    """Parses various date formats into ISO string"""
    try:
        # Try direct ISO
        dt = datetime.fromisoformat(date_str)
    except ValueError:
        # Try friendly formats like 'tomorrow' or 'today'
        lower = date_str.lower().strip()
        now = datetime.now(timezone.utc)
        if lower == "today":
            dt = now
        elif lower == "tomorrow":
            dt = now + timedelta(days=1)
        else:
            # fallback: current time + 1 day
            dt = now + timedelta(days=1)
    return dt.isoformat()

# =================================
# 🧰 MCP Tools
# =================================

@mcp.tool(name="create_task", description="Create a new task with title, description, assignee and due date")
def create_task(task: Task) -> dict:
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    task.task_id = task_id
    task.due_date = parse_due_date(task.due_date)
    TASK_DB[task_id] = task

    return {
        "status": "success",
        "message": f"✅ Task '{task.title}' created and assigned to {task.assignee}.",
        "task": task.model_dump()
    }

@mcp.tool(name="update_task", description="Update task status or due date")
def update_task(update: TaskUpdate) -> dict:
    if update.task_id not in TASK_DB:
        return {"status": "error", "message": f"Task {update.task_id} not found."}

    task = TASK_DB[update.task_id]
    if update.new_status:
        task.status = update.new_status
    if update.new_due_date:
        task.due_date = parse_due_date(update.new_due_date)

    TASK_DB[update.task_id] = task
    return {
        "status": "success",
        "message": f"📝 Task {task.task_id} updated.",
        "task": task.model_dump()
    }

@mcp.tool(name="reschedule_meeting", description="Reschedule a meeting to a new time")
def reschedule_meeting(meeting: Meeting) -> dict:
    MEETING_DB[meeting.meeting_id] = meeting.new_time
    return {
        "status": "success",
        "message": f"📅 Meeting {meeting.meeting_id} rescheduled to {meeting.new_time}."
    }

@mcp.tool(name="generate_daily_summary", description="Generate daily summary of all tasks")
def generate_daily_summary(project_id: Optional[str] = None, assignee: Optional[str] = None) -> dict:
    filtered_tasks = [
        t for t in TASK_DB.values()
        if (not assignee or t.assignee == assignee)
    ]

    counts = {"To Do": 0, "In Progress": 0, "Done": 0}
    for t in filtered_tasks:
        counts[t.status] = counts.get(t.status, 0) + 1

    summary_text = f"📊 Daily summary for {assignee or 'project'}:\n"
    summary_text += "\n".join([f"• {status}: {count}" for status, count in counts.items()])

    return DailySummaryResponse(
        status="success",
        summary=summary_text,
        details=counts,
        generated_at=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    ).model_dump()

@mcp.tool(name="get_user_tasks", description="List all tasks assigned to a user")
def get_user_tasks(assignee: str) -> dict:
    tasks = [t.model_dump() for t in TASK_DB.values() if t.assignee.lower() == assignee.lower()]
    return {
        "status": "success",
        "assignee": assignee,
        "task_count": len(tasks),
        "tasks": tasks
    }

@mcp.tool(name="get_sprint_summary", description="Get sprint summary with progress")
def get_sprint_summary(sprint_id: str) -> dict:
    total = len(TASK_DB)
    done = sum(1 for t in TASK_DB.values() if t.status.lower() == "done")
    progress = f"{int((done / total) * 100)}%" if total else "0%"

    return {
        "status": "success",
        "sprint_id": sprint_id,
        "progress": progress,
        "total_tasks": total,
        "completed_tasks": done,
        "remaining_tasks": total - done
    }

# =================================
# 🌐 Launch MCP Server
# =================================
mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=9000)
