import uuid
import threading
import time
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from pydantic import BaseModel
from enum import Enum
import traceback

from config import Config
from tempmail.moemail import MoeMail
from tempmail.tempmailhub import TempMailHub
from automation.dreamina import DreaminaRegister

app = FastAPI(title="Dreamina Register API")

import shutil
import glob
import os

@app.on_event("startup")
async def startup_event():
    print("Performing startup cleanup...")
    # Clean up stale user_data directories
    for path in glob.glob(os.path.join(os.getcwd(), "user_data_*")):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Cleaned up stale directory: {path}")
        except Exception as e:
            print(f"Failed to cleanup {path}: {e}")
            
    # Clean up stale proxy plugins
    for path in glob.glob(os.path.join(os.getcwd(), "proxy_auth_plugin_*")):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Cleaned up stale proxy plugin: {path}")
        except Exception as e:
            print(f"Failed to cleanup proxy plugin {path}: {e}")

# --- In-Memory Task Store ---
tasks: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models ---
class MailType(str, Enum):
    moemail = "moemail"
    tempmailhub = "tempmailhub"

class RegisterRequest(BaseModel):
    mail_type: MailType
    channel: Optional[str] = None # For tempmailhub

class BatchRegisterRequest(BaseModel):
    count: int
    mail_type: MailType
    channel: Optional[str] = None # For tempmailhub

class UpdateSessionRequest(BaseModel):
    email: str
    password: str

class TaskResponse(BaseModel):
    task_id: str
    status: str

class RegisteredAccount(BaseModel):
    email: str
    password: str
    session_id: str

class BatchRegisterResult(BaseModel):
    success_count: int
    fail_count: int
    accounts: List[RegisteredAccount]
    errors: List[str]

class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None # Can be RegisteredAccount or BatchRegisterResult
    error: Optional[str] = None

# --- Dependencies ---
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    token = authorization.split(" ")[1]
    # In a real scenario, you might want a specific API KEY for the server
    # For now, let's assume we reuse one of the keys from config or a specific SERVER_API_KEY
    # If no specific key is defined, we might need to add one to Config or .env
    # Let's check if there is an env var for this, if not, maybe use a hardcoded one or one of the existing keys?
    # The requirement says "Authorization: Bearer $API_KEY". 
    # Let's assume there is a SERVER_API_KEY in .env, or we just validate it exists.
    # For simplicity and robust implementation, let's use a configured key.
    # We will look for SERVER_API_KEY in Os.environ, defaulting to a simple check if not set (or fail).
    
    # Since we can't easily add to .env right now without asking user, 
    # let's assume valid if it matches a specific value or just accept any non-empty for now if no config?
    # Better: check against a configured key.
    # Let's add SERVER_API_KEY to Config in a future step or just use a placeholder check here.
    # Implementing a simple check:
    # Implementing a simple check:
    expected_key = Config.SERVER_API_KEY
    if token != expected_key:
         raise HTTPException(status_code=403, detail="Invalid API Key")
    return token

# --- Helper Functions ---
def get_tempmail_service(mail_type: str, channel: Optional[str] = None):
    if mail_type == "moemail":
        if not Config.MOEMAIL_API_KEY:
             raise ValueError("MOEMAIL_API_KEY is not configured")
        return MoeMail(Config.MOEMAIL_API_KEY, Config.MOEMAIL_BASE_URL)
    elif mail_type == "tempmailhub":
        if not Config.TEMPMAILHUB_API_KEY:
            raise ValueError("TEMPMAILHUB_API_KEY is not configured")
        effective_channel = channel if channel else Config.TEMPMAILHUB_CHANNEL
        if not effective_channel:
             raise ValueError("Channel is required for tempmailhub")
        return TempMailHub(Config.TEMPMAILHUB_API_KEY, effective_channel, Config.TEMPMAILHUB_BASE_URL)
    else:
        raise ValueError(f"Unsupported mail type: {mail_type}")

def run_register_task(task_id: str, mail_type: str, channel: Optional[str]):
    try:
        tasks[task_id]["status"] = "processing"
        tempmail_service = get_tempmail_service(mail_type, channel)
        register = DreaminaRegister(tempmail_service, Config.PROXY_URL)
        result = register.register() # Now returns dict
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        traceback.print_exc()

def run_batch_register_task(task_id: str, count: int, mail_type: str, channel: Optional[str]):
    try:
        tasks[task_id]["status"] = "processing"
        tempmail_service = get_tempmail_service(mail_type, channel)
        
        results = []
        errors = []
        
        for i in range(count):
            try:
                print(f"Batch Register Task {task_id}: Processing {i+1}/{count}")
                register = DreaminaRegister(tempmail_service, Config.PROXY_URL)
                res = register.register()
                results.append(res)
            except Exception as e:
                print(f"Batch Register Task {task_id}: Failed {i+1}/{count} - {e}")
                errors.append(f"Index {i+1}: {str(e)}")
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = {
            "success_count": len(results),
            "fail_count": len(errors),
            "accounts": results,
            "errors": errors
        }
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        traceback.print_exc()

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/register", response_model=TaskResponse)
def create_register_task(req: RegisterRequest, background_tasks: BackgroundTasks, token: str = Depends(verify_token)):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "created_at": time.time(),
        "type": "single_register"
    }
    
    # Run in a separate thread because DrissionPage is blocking
    thread = threading.Thread(target=run_register_task, args=(task_id, req.mail_type.value, req.channel))
    thread.daemon = True
    thread.start()
    
    return {"task_id": task_id, "status": "pending"}

@app.post("/register/batch", response_model=TaskResponse)
def create_batch_register_task(req: BatchRegisterRequest, background_tasks: BackgroundTasks, token: str = Depends(verify_token)):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "created_at": time.time(),
        "type": "batch_register"
    }
    
    thread = threading.Thread(target=run_batch_register_task, args=(task_id, req.count, req.mail_type.value, req.channel))
    thread.daemon = True
    thread.start()
    
    return {"task_id": task_id, "status": "pending"}

@app.post("/session/update", response_model=Dict[str, Any])
def update_session(req: UpdateSessionRequest, token: str = Depends(verify_token)):
    # This is synchronous as per plan, but since it involves browser, it might block the server.
    # However, user requested async only for register and batch. 
    # If we want to be safe, we should probably make this async too, but let's stick to plan: synchronous.
    # Warning: calling blocking code in async def or normal def in FastAPI:
    # fastAPI runs normal def in threadpool, so it's okay-ish, but DrissionPage might have thread safety issues if not careful.
    # Since we create a new instance each time, it should be fine.
    
    try:
        # We don't need tempmail service for login, but DreaminaRegister init requires it.
        # We can pass a dummy or change __init__ to optional.
        # Let's look at __init__: `def __init__(self, tempmail_service: TempMailBase, ...)`
        # It expects a TempMailBase. We can pass None if login doesn't use it, but type hint might complain or code might break if it tries to use it.
        # Let's check `login` method: it accesses `self.page`. `__init__` sets `self.tempmail_service`. 
        # `login` does NOT use `tempmail_service`.
        # So we can pass a dummy or Mock.
        # Constructing a dummy might be easier. Or just pick one from config.
        
        # Use moemail as default dummy if config available, else try simple mock
        try:
             tempmail_service = get_tempmail_service("moemail")
        except:
             # If moemail not configured, try tempmailhub, else fail?
             # Actually, let's just create a dummy object
             class DummyTempMail:
                 pass
             tempmail_service = DummyTempMail()

        register = DreaminaRegister(tempmail_service, Config.PROXY_URL)
        result = register.login(req.email, req.password)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResultResponse)
def get_task_status(task_id: str, token: str = Depends(verify_token)):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "result": task.get("result"),
        "error": task.get("error")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
