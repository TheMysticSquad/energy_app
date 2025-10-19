# utility_api_server.py
from fastapi import FastAPI, HTTPException, Header, Depends, APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uvicorn
from database_manager import DatabaseManager  # Your existing DB manager

router = APIRouter(tags=["API Operations"])

db = DatabaseManager()

# -----------------------------
# Pydantic Models
# -----------------------------
class MeterReading(BaseModel):
    meter_id: str
    reading_datetime: datetime
    kwh: float

class PushMeterReadingRequest(BaseModel):
    vendor_id: int
    readings: List[MeterReading]

class MeterCommandRequest(BaseModel):
    meter_id: str
    command_type: str  # DISCONNECT / RECONNECT / PING / SYNC
    vendor_id: int

class DailyBillingRequest(BaseModel):
    billing_date: Optional[date] = date.today()

class RechargeRequest(BaseModel):
    consumer_id: str
    amount: float
    payment_mode: str
    transaction_ref: Optional[str]

# -----------------------------
# Helper: API Key Auth
# -----------------------------
def verify_vendor_api_key(x_api_key: str = Header(...)):
    vendor = db.get_vendor_by_api_key(x_api_key)
    if not vendor:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return vendor

# -----------------------------
# Consumer Info Endpoint
# -----------------------------
@router.get("/consumer/{consumer_id}")
def get_consumer_info(consumer_id: str, vendor=Depends(verify_vendor_api_key)):
    consumer = db.get_consumer_by_id(consumer_id)
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")
    return {
        "consumer_id": consumer.consumer_id,
        "name": consumer.name,
        "balance": consumer.balance,
        "status": consumer.status
    }

# -----------------------------
# Push Meter Reading Endpoint
# -----------------------------
@router.post("/push-meter-reading")
def push_meter_reading(payload: PushMeterReadingRequest, vendor=Depends(verify_vendor_api_key)):
    for reading in payload.readings:
        db.insert_meter_reading(reading.meter_id, reading.reading_datetime, reading.kwh)
    return {"status": "success", "message": f"{len(payload.readings)} readings recorded."}

# -----------------------------
# Issue Meter Command Endpoint
# -----------------------------
@router.post("/issue-meter-command")
def issue_meter_command(payload: MeterCommandRequest, vendor=Depends(verify_vendor_api_key)):
    command_id = db.insert_meter_command(payload.meter_id, payload.command_type)
    # Optional: trigger actual vendor API call asynchronously
    return {"status": "pending", "command_id": command_id}

# -----------------------------
# Get Meter Command Status
# -----------------------------
@router.get("/meter-command/{command_id}")
def get_meter_command_status(command_id: int, vendor=Depends(verify_vendor_api_key)):
    command = db.get_meter_command(command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return {
        "command_id": command_id,
        "status": command.status,
        "response": command.response_message
    }

# -----------------------------
# Process Recharge Endpoint
# -----------------------------
@router.post("/process-recharge")
def process_recharge(payload: RechargeRequest, vendor=Depends(verify_vendor_api_key)):
    consumer = db.get_consumer_by_id(payload.consumer_id)
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")
    db.add_recharge(payload.consumer_id, payload.amount, payload.payment_mode, payload.transaction_ref)
    db.update_consumer_balance(payload.consumer_id, consumer.balance + payload.amount)
    return {"status": "success", "new_balance": consumer.balance + payload.amount}

# -----------------------------
# Daily Billing Job
# -----------------------------
@router.post("/daily-billing-job")
def run_daily_billing(payload: DailyBillingRequest, vendor=Depends(verify_vendor_api_key)):
    total, success, failed = db.run_daily_billing(payload.billing_date)
    return {
        "status": "completed",
        "billing_date": str(payload.billing_date),
        "total_processed": total,
        "success_count": success,
        "failed_count": failed
    }

# -----------------------------
# Monthly Invoice Generation
# -----------------------------
@router.post("/generate-invoice")
def generate_invoice(month: str, vendor=Depends(verify_vendor_api_key)):
    invoices = db.generate_monthly_invoices(month)
    return {"status": "success", "total_invoices": len(invoices)}

# -----------------------------
# Alerts
# -----------------------------
@router.get("/alerts")
def get_alerts(vendor=Depends(verify_vendor_api_key)):
    alerts = db.get_low_balance_alerts()
    return {"alerts": alerts}

# -----------------------------
# System Status
# -----------------------------
@router.get("/status")
def system_status():
    return {
        "uptime": "Operational",
        "vendors_synced": db.get_active_vendors_count(),
        "last_daily_billing": db.get_last_daily_billing_date()
    }

