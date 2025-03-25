from fastapi import FastAPI, HTTPException, Query
import requests
from datetime import datetime
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware 
from typing import Optional
from pydantic import BaseModel
import logging


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






# Configure logging
logging.basicConfig(level=logging.INFO)

class Task(BaseModel):
    task_id: str
    student_id: int
    educator_employee_id:int
    description: str
    due_date: str
    status: str
    feedback: str
    program_id: int
    title: str
    priority: str
    category: str
    stage: str

@app.post("/tasks")
def insert_task(task: Task):
    payload = task.dict()
    payload["created_at"] = datetime.utcnow().isoformat()
    
    logging.info(f"Payload being sent: {payload}")
    
    response = requests.post(f"{url}/goals_tasks", headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return {"message": "Task inserted successfully"}
    
    logging.error(f"Error response: {response.status_code} - {response.text}")
    raise HTTPException(status_code=response.status_code, detail=response.text)



class TaskUpdate(BaseModel):
    due_date: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

@app.patch("/tasks")
def update_task(
    task_id: str = Query(...),  # Extracting task_id from query parameters
    update_data: TaskUpdate = None  # Accepting the update data as a Pydantic model
):
    # Log received parameters for debugging
    print(f"Received task_id: {task_id}")
    print(f"Received update data: {update_data}")

    json_data = update_data.dict(exclude_unset=True)  # Convert to dict and exclude unset values

    if not json_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    
    print(f"JSON data to send: {json_data}")
    # Correct Supabase API filtering
    f_url = f"{url}/goals_tasks?task_id=eq.{task_id}"
    response = requests.patch(f_url, headers=headers, json=json_data)

    if response.status_code in [200, 204]:
        return {"message": "Task updated successfully"}

    raise HTTPException(status_code=response.status_code, detail=response.text)

# Example of how to call the endpoint
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
