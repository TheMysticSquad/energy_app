from fastapi import FastAPI, BackgroundTasks
import requests, time, os
from security.hmac_utils import verify_payload

app = FastAPI(title="Mock AMISP")
NSC_CALLBACK_URL = "http://nsc:8000/nsc/callback"

@app.post("/amisp/disconnect")
def process_request(data: dict, background_tasks: BackgroundTasks):
    if not verify_payload(data):
        return {"error": "Invalid signature"}

    background_tasks.add_task(execute_action, data)
    return {"message": "Request received"}

def execute_action(payload):
    time.sleep(3)
    callback = {
        "request_id": payload.get("request_id"),
        "status": "SUCCESS",
        "message": "Action completed"
    }
    try:
        requests.post(NSC_CALLBACK_URL, json=callback, timeout=5)
    except Exception as e:
        print("Callback failed:", e)
