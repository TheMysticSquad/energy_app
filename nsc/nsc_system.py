from fastapi import FastAPI, BackgroundTasks
import requests, os, time
from security.hmac_utils import sign_payload
from utils.retry import retry
from prometheus_client import Counter, start_http_server

app = FastAPI(title="NSC System")

AMISP_URL = os.getenv("AMISP_URL", "http://localhost:8001")
METRIC_REQUESTS = Counter("nsc_requests_total", "Total NSC requests")
TICKET_DB = {}  # simple in-memory store

@app.post("/nsc/disconnect")
@retry
def initiate_disconnect(data: dict, background_tasks: BackgroundTasks):
    METRIC_REQUESTS.inc()
    ticket_id = data.get("request_id")
    TICKET_DB[ticket_id] = {"status": "PENDING", "data": data}

    # sign and send to AMISP
    signed_data = sign_payload(data)
    background_tasks.add_task(send_to_amisp, signed_data)
    return {"message": "Disconnection request sent", "ticket": ticket_id}

def send_to_amisp(payload):
    try:
        res = requests.post(f"{AMISP_URL}/amisp/disconnect", json=payload, timeout=5)
        res.raise_for_status()
    except Exception as e:
        print("Error sending to AMISP:", e)

@app.post("/nsc/callback")
def callback(data: dict):
    ticket_id = data.get("request_id")
    if ticket_id in TICKET_DB:
        TICKET_DB[ticket_id]["status"] = data.get("status")
        return {"message": "Callback processed"}
    return {"error": "Unknown ticket"}

if __name__ == "__main__":
    start_http_server(9100)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
