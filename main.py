from fastapi import FastAPI, HTTPException
import requests
from datetime import datetime
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend domain(s) for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


url = "https://nizvcdssajfpjtncbojx.supabase.co/rest/v1"
headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

@app.get("/student_ids")
def get_student_ids():
    params = {'select': 'student_id'}
    response = requests.get(f"{url}/students", params=params, headers=headers)
    if response.status_code == 200:
        return [item["student_id"] for item in response.json()]
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/program_ids")
def get_program_ids():
    params = {'select': 'program_id'}
    response = requests.get(f"{url}/programs", params=params, headers=headers)
    if response.status_code == 200:
        return [item["program_id"] for item in response.json()]
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/tasks")
def get_all_tasks():
    response = requests.get(f"{url}/goals_tasks", headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/tasks/status/{status}")
def get_tasks_by_status(status: str):
    params = {'status': f"eq.{status}"}
    response = requests.get(f"{url}/goals_tasks", params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/tasks/student/{student_id}")
def get_tasks_by_student(student_id: int):
    params = {'student_id': f"eq.{student_id}"}
    response = requests.get(f"{url}/goals_tasks", params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/tasks")
def insert_task(task_id: str, student_id: int, assigned_by: int, description: str, 
                due_date: str, status: str, feedback: str, program_id: int, 
                title: str, priority: str, category: str, stage: str):
    payload = {
        "task_id": task_id,
        "student_id": student_id,
        "assigned_by": assigned_by,
        "description": description,
        "due_date": due_date,
        "status": status,
        "created_at": datetime.utcnow().isoformat(),
        "feedback": feedback,
        "program_id": program_id,
        "title": title,
        "priority": priority,
        "category": category,
        "stage": stage,
    }
    response = requests.post(f"{url}/goals_tasks", headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return {"message": "Task inserted successfully"}
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.patch("/tasks")
def update_task(
    task_id: str,
    due_date: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
):
    json_data = {}

    if due_date:
        json_data["due_date"] = due_date
    if category:
        json_data["category"] = category
    if priority:
        json_data["priority"] = priority
    if description:
        json_data["description"] = description
    if status:
        json_data["status"] = status

    if not json_data:
        raise HTTPException(status_code=400, detail="No update fields provided")

    # Supabase API expects filtering via `eq` inside the request body or URL
    f_url = f"{url}/goals_tasks?id=eq.{task_id}"

    response = requests.patch(f_url, headers=headers, json=json_data)

    if response.status_code in [200, 204]:
        return {"message": "Task updated successfully"}

    raise HTTPException(status_code=response.status_code, detail=response.text)
