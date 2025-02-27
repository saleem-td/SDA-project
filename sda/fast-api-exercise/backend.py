# Cell 1: Imports and Setup
from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel, field_validator
# validator will be deprecated in newer version of FastAPI
# You may see the warning is your Flask version is the latest
# Don't worry if you see the warning
# To avoid the warning you can import the field_validator instead of validator
# which perform the same function
from datetime import datetime

app = FastAPI()


# Cell 2: Task Model
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1
    tags: List[str] = []

    # Validate title
    @field_validator('title')
    def title_must_be_meaningful(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()

    # Validate priority
    @field_validator('priority')
    def priority_must_be_valid(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

    # Validate tags
    @field_validator('tags')
    def clean_tags(cls, v):
        # Convert to lowercase and remove duplicates
        return list(set(tag.lower() for tag in v))
    

# Cell 3: Database Setup
# We'll use a simple dictionary as our database
tasks = {}


# Cell 4: Create Task Endpoint
@app.post("/tasks/")
async def create_task(task: TaskCreate):
    # Generate a new task ID
    task_id = len(tasks) + 1
    # Store the task
    tasks[task_id] = task
    # Return the created task with its ID
    return {
        "task_id": task_id,
        "task": task
    }

# Example task creation
example_task = {
    "title": "Learn FastAPI",
    "description": "Complete the practice exercises",
    "due_date": "2024-12-31T00:00:00",
    "priority": 2,
    "tags": ["python", "api", "learning"]
}

# Cell 5: Get Tasks with Pagination
@app.get("/tasks/")
async def get_tasks(
    skip: int = Query(0, description="Number of tasks to skip"),
    limit: int = Query(10, description="Maximum number of tasks to return")
):
    # Get a slice of tasks based on skip and limit
    task_items = list(tasks.items())[skip:skip + limit]

    return {
        "total_tasks": len(tasks),
        "returned_tasks": len(task_items),
        "tasks": dict(task_items)
    }

# Cell 6: Search Endpoint
@app.get("/tasks/search/")
async def search_tasks(
    title: Optional[str] = Query(None, description="Search by title"),
    priority: Optional[int] = Query(None, description="Filter by priority (1-5)"),
    skip: int = Query(0, description="Number of tasks to skip"),
    limit: int = Query(10, description="Maximum number of tasks to return")
):
# Filter tasks
    filtered_tasks = {}

    for task_id, task in tasks.items():
        # Check if task matches search criteria
        if title and title.lower() not in task.title.lower():
            continue
        if priority and task.priority != priority:
            continue
        filtered_tasks[task_id] = task

    # Apply pagination
    task_items = list(filtered_tasks.items())[skip:skip + limit]

    return {
        "total_matches": len(filtered_tasks),
        "returned_tasks": len(task_items),
        "tasks": dict(task_items)
    }