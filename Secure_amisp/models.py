from pydantic import BaseModel, Field, conint, confloat
from typing import Optional, List
from datetime import datetime

# --- Request Schemas (Inputs from the Vendor) ---

class InstallMeterRequest(BaseModel):
    """Schema for registering a new meter."""
    consumer_id: str = Field(..., description="Unique ID of the consumer (VARCHAR/String(50)).")
    meter_id: str = Field(..., description="Unique ID of the new meter (VARCHAR/String(50)).")
    install_date: datetime = Field(..., description="Timestamp of the installation (DateTime).")

class RemoveMeterRequest(BaseModel):
    """Schema for marking a meter as removed/disconnected."""
    meter_id: str = Field(..., description="Unique ID of the meter to remove.")
    removal_date: datetime = Field(..., description="Timestamp of the removal.")

class UploadReadingRequest(BaseModel):
    """Schema for pushing a single meter consumption data point."""
    meter_id: str = Field(..., description="ID of the meter generating the reading.")
    reading_datetime: datetime = Field(..., description="Timestamp of the reading.")
    kwh: confloat(gt=0) = Field(..., description="The consumption reading in kWh (Float).")

# NOTE: A common pattern for bulk upload is to wrap the single reading model
class BulkUploadReadingRequest(BaseModel):
    """Schema for uploading a list of meter consumption data points."""
    vendor_id: int
    readings: List[UploadReadingRequest]


class CommandRequest(BaseModel):
    """Schema for issuing a command to a meter."""
    meter_id: str
    command_type: str = Field(..., description="Type of command (e.g., 'DISCONNECT', 'RECONNECT', 'RATE_CHANGE').")
    vendor_id: int
    # Additional fields could include command_value, scheduled_time, etc.

class RechargeRequest(BaseModel):
    """Schema for processing a consumer payment/recharge."""
    consumer_id: str = Field(..., description="Consumer receiving the recharge.")
    amount: confloat(gt=0) = Field(..., description="The payment amount (Float).")
    transaction_ref: str = Field(..., description="Unique transaction reference (VARCHAR/String(100)).")

class InvoiceSyncRequest(BaseModel):
    """Schema for syncing a monthly invoice (Future/Utility feature)."""
    invoice_id: conint(ge=1)
    consumer_id: str
    billing_month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Billing month in YYYY-MM format.")
    total_units: float
    total_amount: float

# --- Response Schemas (Standardized API Outputs) ---

class ApiStatusResponse(BaseModel):
    """Standard response for status and simple operations."""
    status: str = Field(..., description="Status of the operation ('success' or 'error').")
    message: str = Field(..., description="Human-readable message.")
    data: Optional[dict] = None

class CommandStatusResponse(BaseModel):
    """Response for checking a meter command status."""
    command_id: conint(ge=1)
    meter_id: str
    status: str = Field(..., description="Current status ('PENDING', 'SENT', 'SUCCESS', 'FAILED').")
    response_message: Optional[str] = Field(None, description="Details or error message from the meter/utility.")

class ConsumerInfoResponse(BaseModel):
    """Detailed consumer profile response (Future feature)."""
    consumer_id: str
    name: str
    address: str
    balance: float
    status: str
    meter_id: Optional[str] = None