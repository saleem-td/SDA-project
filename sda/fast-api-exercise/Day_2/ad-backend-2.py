# Basic imports needed for our application
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
# Import libraries for SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import httpx

# Initialize FastAPI app
app = FastAPI()

# Basic Task model
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost/taskdb"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define SQLAlchemy model
class TaskDB(Base):
    """Database model for tasks"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
def create_task(task: Task, db: Session = Depends(get_db)):
    """Create a new task"""
    # Convert Pydantic model to SQLAlchemy model
    db_task = TaskDB(**task.dict())

    try:
        # Add and commit to database
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )

@app.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Retrieve a single task"""
    # Query the database
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    # Handle task not found
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    """Update a task with error handling"""
    # Find the task
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    # 404 Error - Task not found
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # 400 Error - Invalid data
    # potential issue: due_date parameter have time zone characters, which is not supported by datetime
    # solution: remove time zone characters
    if task.due_date and task.due_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date cannot be in the past"
        )

    try:
        # Update task attributes
        for key, value in task.dict().items():
            setattr(db_task, key, value)
        db.commit()
        return {"message": "Task updated successfully"}
    except Exception as e:
        # 500 Error - Server error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )
    



@app.get("/tasks/{task_id}/with-joke")
async def get_task_with_joke(task_id: int, db: Session = Depends(get_db)):
    """Async endpoint example fetching task and a random joke"""
    # Get task from database
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Fetch a random joke asynchronously from a free API
    async with httpx.AsyncClient() as client:
        response = await client.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()

    # Combine and return data
    return {
        "task": task,
        "joke": {
            "setup": joke["setup"],
            "punchline": joke["punchline"]
        }
    }


