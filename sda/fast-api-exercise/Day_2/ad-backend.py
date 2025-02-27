# Basic imports needed for our application
from fastapi import FastAPI, Path, Query, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
# import psycopg2 related libraries
import psycopg2
from psycopg2.extras import RealDictCursor


# Initialize FastAPI app
app = FastAPI()

# Basic Task model
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1


# Connection Function to db
def get_db_connection():
    """Create a database connection using psycopg2"""
    try:
        conn = psycopg2.connect(
            dbname="taskdb",
            user="postgres",
            password="postgres",
            host="localhost",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.get("/tasks/raw/{task_id}")
def get_task_raw(task_id: int):
    """Retrieve a task using raw SQL"""
    # Get database connection
    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

    try:
        # Create cursor and execute query
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM tasks WHERE id = %s",
            (task_id,)
        )
        task = cur.fetchone()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return dict(task)
    finally:
        # Always close cursor and connection
        cur.close()
        conn.close()