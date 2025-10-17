from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# ======================
# Data Models
# ======================
class Task(BaseModel):
    title: str
    description: str
    assignee: str
    due_date: str
    status: Optional[str] = "To Do"
    task_id: Optional[str] = None

class Meeting(BaseModel):
    meeting_id: str
    new_time: str

class TaskUpdate(BaseModel):
    task_id: str
    new_status: Optional[str] = None
    new_due_date: Optional[str] = None

class DailySummaryResponse(BaseModel):
    status: str
    project_id: Optional[str] = None
    assignee: Optional[str] = None
    summary: str
    details: Optional[dict] = None
    generated_at: str

# ======================
# Initialize MCP App
# ======================
mcp = FastMCP(
    name="ProjectManagementAgent",
    stateless_http=True,
)

# ======================
# MCP Tools
# ======================
@mcp.tool(
    name="create_task",
    description="Create a new task with specified title, description, assignee and due date"
)
def create_task(task: Task) -> dict:
    task.task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "status": "success",
        "message": f"Task '{task.title}' created successfully",
        "task": task.model_dump()
    }

@mcp.tool(
    name="update_task",
    description="Update an existing task's status or due date"
)
def update_task(update: TaskUpdate) -> dict:
    return {
        "status": "success",
        "message": f"Task {update.task_id} updated successfully",
        "updates": update.model_dump()
    }

@mcp.tool(
    name="generate_daily_summary",
    description="Generate a summary of all tasks and their current status for a project"
)
def generate_daily_summary(project_id: Optional[str] = None, assignee: Optional[str] = None) -> dict:
    if not project_id and not assignee:
        return {
            "status": "error",
            "message": "Either `project_id` or `assignee` must be provided"
        }

    details = {"to_do": 3, "in_progress": 4, "done": 10}
    generated_at = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    resp = DailySummaryResponse(
        status="success",
        project_id=project_id,
        assignee=assignee,
        summary=(f"Daily summary for project {project_id}" if project_id else f"Daily summary for assignee {assignee}"),
        details=details,
        generated_at=generated_at,
    )
    return resp.model_dump()

@mcp.tool(
    name="reschedule_meeting",
    description="Reschedule an existing meeting to a new time"
)
def reschedule_meeting(meeting: Meeting) -> dict:
    return {
        "status": "success",
        "message": f"Meeting {meeting.meeting_id} rescheduled successfully",
        "new_time": meeting.new_time
    }

@mcp.tool(
    name="get_user_tasks",
    description="Get all tasks assigned to a specific user for the current sprint"
)
def get_user_tasks(assignee: str, sprint_id: Optional[str] = None) -> dict:
    return {
        "status": "success",
        "assignee": assignee,
        "sprint_id": sprint_id,
        "tasks": []  # would be populated from PM tool's API
    }

@mcp.tool(
    name="get_sprint_summary",
    description="Get a summary of the current sprint including progress and burndown"
)
def get_sprint_summary(sprint_id: str) -> dict:
    return {
        "status": "success",
        "sprint_id": sprint_id,
        "progress": "75%",
        "remaining_days": 5,
        "completed_tasks": 15,
        "in_progress": 5,
        "to_do": 3
    }

# ======================
# Launch Server
# ======================
mcp_app = mcp.streamable_http_app()

