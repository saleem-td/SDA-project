# 📌 Import Required Libraries
from fastapi import FastAPI, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, select
from datetime import datetime

# 📌 Initialize FastAPI App
app = FastAPI()

# 📌 Database Configuration
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@172.21.153.18:5432/books"

# Create Async Engine & Session
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# 📌 Define Database Table (Task Model)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=False, default=1)
    tags = Column(ARRAY(String), nullable=True)

# 📌 Initialize Database (Create Tables)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 📌 Define Pydantic Model for Task Creation
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1
    tags: List[str] = []

    @field_validator('title')
    def title_must_be_meaningful(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()

    @field_validator('priority')
    def priority_must_be_valid(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

    @field_validator('tags')
    def clean_tags(cls, v):
        return list(set(tag.lower() for tag in v))

# 📌 Dependency to Get DB Session
async def get_db():
    async with async_session_maker() as session:
        yield session

# 📌 Create Task API
@app.post("/tasks/")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        tags=task.tags
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return {"task_id": new_task.id, "task": new_task}

# 📌 Get Tasks with Pagination
@app.get("/tasks/")
async def get_tasks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).offset(skip).limit(limit))
    tasks = result.scalars().all()

    return {"total_tasks": len(tasks), "tasks": tasks}

# 📌 Search Tasks by Title or Priority
@app.get("/tasks/search/")
async def search_tasks(
    title: Optional[str] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    query = select(Task)
    
    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))
    if priority:
        query = query.filter(Task.priority == priority)

    result = await db.execute(query.offset(skip).limit(limit))
    tasks = result.scalars().all()

    return {"total_matches": len(tasks), "tasks": tasks}
