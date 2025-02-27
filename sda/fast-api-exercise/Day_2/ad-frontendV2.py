import streamlit as st
import requests
from datetime import date, datetime

# Base URL of your FastAPI back-end
BASE_URL = "http://localhost:8000"  # Adjust if your backend is hosted elsewhere

st.title("Task Manager Front-End")

# Create separate tabs for each functionality
tab_create, tab_read, tab_update, tab_joke = st.tabs([
    "Create Task", "Read Task", "Update Task", "Task with Joke"
])

# ----- Create Task Tab -----
with tab_create:
    st.header("Create a New Task")
    title = st.text_input("Title")
    description = st.text_area("Description")
    due_date = st.date_input("Due Date", value=date.today())
    priority = st.number_input("Priority (1-5)", min_value=1, max_value=5, value=1)
    
    if st.button("Create Task"):
        # Build payload; due_date is converted to ISO format
        task_payload = {
            "title": title,
            "description": description,
            "due_date": datetime.combine(due_date, datetime.min.time()).isoformat(),
            "priority": priority
        }
        response = requests.post(f"{BASE_URL}/tasks/", json=task_payload)
        if response.status_code == 201:
            st.success("Task created successfully!")
            st.json(response.json())
        else:
            st.error("Error creating task")
            st.write(response.text)

# ----- Read Task Tab -----
with tab_read:
    st.header("Read a Task")
    task_id = st.number_input("Enter Task ID", min_value=1, step=1, key="read_task_id")
    if st.button("Get Task"):
        response = requests.get(f"{BASE_URL}/tasks/{int(task_id)}")
        if response.status_code == 200:
            st.success("Task fetched successfully!")
            st.json(response.json())
        else:
            st.error("Error fetching task")
            st.write(response.text)

# ----- Update Task Tab -----
with tab_update:
    st.header("Update a Task")
    task_id_update = st.number_input("Enter Task ID to update", min_value=1, step=1, key="update_task_id")
    new_title = st.text_input("New Title", key="new_title")
    new_description = st.text_area("New Description", key="new_description")
    new_due_date = st.date_input("New Due Date", value=date.today(), key="new_due_date")
    new_priority = st.number_input("New Priority (1-5)", min_value=1, max_value=5, value=1, key="new_priority")
    
    if st.button("Update Task"):
        update_payload = {
            "title": new_title,
            "description": new_description,
            "due_date": datetime.combine(new_due_date, datetime.min.time()).isoformat(),
            "priority": new_priority
        }
        response = requests.put(f"{BASE_URL}/tasks/{int(task_id_update)}", json=update_payload)
        if response.status_code == 200:
            st.success("Task updated successfully!")
            st.write(response.json())
        else:
            st.error("Error updating task")
            st.write(response.text)

# ----- Task with Joke Tab -----
with tab_joke:
    st.header("Get Task with a Random Joke")
    task_id_joke = st.number_input("Enter Task ID for Joke", min_value=1, step=1, key="joke_task_id")
    if st.button("Fetch Task with Joke"):
        response = requests.get(f"{BASE_URL}/tasks/{int(task_id_joke)}/with-joke")
        if response.status_code == 200:
            data = response.json()
            st.success("Fetched task and joke successfully!")
            st.write("Task:")
            st.json(data.get("task"))
            st.write("Joke:")
            st.write(f"Setup: {data.get('joke', {}).get('setup')}")
            st.write(f"Punchline: {data.get('joke', {}).get('punchline')}")
        else:
            st.error("Error fetching task with joke")
            st.write(response.text)
