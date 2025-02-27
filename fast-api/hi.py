from fastapi import FastAPI, Path, Query
from typing import Optional, List
from pydantic import BaseModel, validator, Field
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# To run this in a real environment:
# uvicorn main:app --reload

# This will start the FastAPI server and reload the app on code changes.
# You can then access the API at http://127.0.0.1:8000css