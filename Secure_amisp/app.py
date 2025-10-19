# app.py (Unified Flask Application for AMISP Vendor Simulator)
from flask import Flask, request, jsonify, render_template, abort
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import hashlib
import os

# Import modules from your project
from database import get_db, Consumer, Meter, MeterReading, Payment, VendorApiKey, VendorAuditLog, MeterCommand
from models import (
    InstallMeterRequest, RemoveMeterRequest, UploadReadingRequest, RechargeRequest, CommandRequest, 
    ApiStatusResponse, CommandStatusResponse # Pydantic models for validation and response
)

# --- Configuration & Initialization ---
app = Flask(__name__)

# --- Pydantic Validation Helper ---
def validate_payload(model):
    """Decorator to validate the request JSON payload against a Pydantic model."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                kwargs['payload'] = model(**data)
            except ValidationError as e:
                abort(400, description=f"Invalid Request Data: {e.errors()}")
            except Exception:
                abort(400, description="Invalid JSON payload.")
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__ # Retain function name for routing
        return wrapper
    return decorator


# --- Authentication Dependency (SECURITY FIX IMPLEMENTED HERE) ---
def get_current_vendor_id(func):
    """
    Decorator to verify Vendor ID sent via X-Vendor-ID header, 
    securely retrieving vendor data from the DB, and logging audit information.
    """
    def wrapper(*args, **kwargs):
        # SECURITY FIX: Read the non-sensitive Vendor ID instead of the API Key
        vendor_id_header = request.headers.get('X-Vendor-ID')
        if not vendor_id_header:
            abort(401, description="Missing X-Vendor-ID header")
        
        # Use database session to verify the Vendor ID
        with next(get_db()) as db:
            # 1. Look up the Vendor based on the ID provided in the header
            stmt = select(VendorApiKey).where(
                # We check the vendor_id directly (no hashing needed here)
                VendorApiKey.vendor_id == vendor_id_header,
                VendorApiKey.is_active == True
            )
            vendor_key_record = db.execute(stmt).scalars().first()
            
            if not vendor_key_record:
                # Log attempt with invalid Vendor ID
                log_audit(db, vendor_id_header, request.path, request.get_json(silent=True), 401)
                abort(401, description=f"Invalid or inactive Vendor ID '{vendor_id_header}'.")
            
            # The Vendor ID is now verified and safe to use
            kwargs['vendor_id'] = vendor_key_record.vendor_id # Pass verified vendor_id to the route
            kwargs['db'] = db # Pass active session to the route
            
            # Execute the actual endpoint logic
            response = func(*args, **kwargs)
            
            # Log successful audit (status code assumed 200/201 from successful response)
            log_audit(db, kwargs['vendor_id'], request.path, request.get_json(silent=True), response.status_code if hasattr(response, 'status_code') else 200)
            return response
    
    wrapper.__name__ = func.__name__ # Retain original function name
    return wrapper

# --- Logging Helper (Modified for Flask) ---
def log_audit(db: Session, vendor_id: str, endpoint: str, request_data: dict, response_status: int):
    """Inserts an audit log record into the vendor_audit_logs table."""
    log_entry = VendorAuditLog(
        vendor_id=vendor_id,
        endpoint=endpoint,
        request_data=str(request_data),
        response_status=response_status
    )
    db.add(log_entry)
    # NOTE: db.commit() is essential here, but we must ensure it doesn't fail
    # if the database session is already in a failed state from the main route.
    try:
        db.commit()
    except Exception:
        # If commit fails (e.g., due to a prior rollback in the main function),
        # try to roll back again and ignore the log entry.
        db.rollback()


# --------------------------------------------------
# 1. FRONTEND ROUTE
# --------------------------------------------------
@app.route("/")
def index():
    """Serves the main HTML page for the frontend simulator."""
    # Flask looks for index.html in the 'templates' folder
    return render_template("index.html")


# --------------------------------------------------
# 2. AMISP API ENDPOINTS (Vendor Simulation)
# --------------------------------------------------

@app.route("/api/install-meter", methods=['POST'])
@get_current_vendor_id
@validate_payload(InstallMeterRequest)
def install_meter(db: Session, vendor_id: str, payload: InstallMeterRequest):
    """Registers a new meter and links it to a consumer."""
    
    consumer = db.get(Consumer, payload.consumer_id)
    if not consumer:
        abort(404, description=f"Consumer ID '{payload.consumer_id}' not found.")

    new_meter = Meter(
        meter_id=payload.meter_id,
        consumer_id=payload.consumer_id,
        install_date=payload.install_date,
        status="INSTALLED"
    )
    
    try:
        db.add(new_meter)
        db.commit()
        # Note: Audit log is handled by the decorator wrapper
        return jsonify(ApiStatusResponse(
            status="success", 
            message=f"Meter {new_meter.meter_id} installed successfully."
        ).model_dump()), 201
    except Exception as e:
        db.rollback()
        abort(500, description=f"DB Error: Meter installation failed. {e}")


@app.route("/api/upload-reading", methods=['POST'])
@get_current_vendor_id
@validate_payload(UploadReadingRequest)
def upload_reading(db: Session, vendor_id: str, payload: UploadReadingRequest):
    """Inserts a new meter reading."""
    
    meter = db.get(Meter, payload.meter_id)
    if not meter or meter.status != 'INSTALLED':
        abort(404, description="Meter not found or not installed.")

    new_reading = MeterReading(
        meter_id=payload.meter_id,
        reading_datetime=payload.reading_datetime,
        kwh=payload.kwh
    )
    
    try:
        db.add(new_reading)
        db.commit()
        return jsonify(ApiStatusResponse(
            status="success", 
            message=f"Reading {payload.kwh} kWh accepted for processing."
        ).model_dump()), 202
    except Exception as e:
        db.rollback()
        abort(500, description=f"DB Error: Reading upload failed. {e}")


@app.route("/api/recharge", methods=['POST'])
@get_current_vendor_id
@validate_payload(RechargeRequest)
def process_recharge(db: Session, vendor_id: str, payload: RechargeRequest):
    """Processes a payment, records it, and updates consumer balance."""
    
    consumer = db.get(Consumer, payload.consumer_id)
    if not consumer:
        abort(404, description="Consumer not found.")

    # 1. Record the Payment
    new_payment = Payment(
        consumer_id=payload.consumer_id,
        amount=payload.amount,
        transaction_ref=payload.transaction_ref
    )

    # 2. Update Consumer Balance
    consumer.balance += payload.amount
    
    try:
        db.add(new_payment)
        db.commit()
        return jsonify(ApiStatusResponse(
            status="success", 
            message=f"Recharge of {payload.amount} processed.",
            data={"new_balance": consumer.balance}
        ).model_dump()), 200
    except Exception as e:
        db.rollback()
        # Simple check for unique constraint violation (transaction_ref)
        if "unique constraint" in str(e).lower():
            abort(409, description="Transaction reference already exists.")
            
        abort(500, description=f"DB Error: Recharge failed. {e}")


@app.route("/api/meter-command", methods=['POST'])
@get_current_vendor_id
@validate_payload(CommandRequest)
def issue_command(db: Session, vendor_id: str, payload: CommandRequest):
    """Issues a command to a meter (e.g., disconnection, rate change)."""
    
    meter = db.get(Meter, payload.meter_id)
    if not meter:
        abort(404, description="Meter not found.")

    new_command = MeterCommand(
        meter_id=payload.meter_id,
        command_type=payload.command_type,
        status="PENDING",
        command_datetime=datetime.utcnow()
    )

    try:
        db.add(new_command)
        db.commit()
        db.refresh(new_command)
        return jsonify(ApiStatusResponse(
            status="success",
            message=f"Command '{payload.command_type}' issued successfully.",
            data={"command_id": new_command.id}
        ).model_dump()), 201
    except Exception as e:
        db.rollback()
        abort(500, description=f"DB Error: Command issuance failed. {e}")


@app.route("/api/command-status/<int:command_id>", methods=['GET'])
@get_current_vendor_id
def get_command_status(db: Session, vendor_id: str, command_id: int):
    """Checks the status of a previously issued meter command."""
    
    command = db.get(MeterCommand, command_id)
    if not command:
        abort(404, description="Command ID not found.")

    return jsonify(CommandStatusResponse(
        command_id=command.id,
        meter_id=command.meter_id,
        status=command.status,
        response_message=command.response_message
    ).model_dump()), 200

# --------------------------------------------------
# 3. Error Handler (To ensure audit logs are saved)
# --------------------------------------------------
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(400)
@app.errorhandler(409)
@app.errorhandler(500)
def handle_http_exception(e):
    # This block is essential for logging failures that happen BEFORE the main route logic
    # It catches exceptions raised by abort()
    try:
        # Try to extract vendor_id from the new header
        vendor_id = request.headers.get('X-Vendor-ID', 'UNKNOWN')
        with next(get_db()) as db:
            log_audit(db, vendor_id, request.path, request.get_json(silent=True), e.code)
    except Exception:
        pass # Ignore logging errors to ensure the HTTP response is sent

    # Return a JSON response for the API clients
    response = jsonify({'status': 'error', 'message': e.description, 'code': e.code})
    response.status_code = e.code
    return response

# --------------------------------------------------
# 4. Run Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
