# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------
# --- Configuration & Engine Initialization ---
# ---------------------------------------------------------------------

# Retrieve the URL from the environment variable (read from .env file)
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Ensure the URL was loaded successfully
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL not found in environment variables or .env file.")

# 🎯 CRITICAL FIX: FORCE THE USE OF THE ROBUST 'psycopg' DRIVER 
# This handles the scenario where the env variable is set to 'postgresql+psycopg2' or 'postgresql+asyncpg'
if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
    # Strip any existing dialect and force the use of the 'psycopg' dialect
    # Example: 'postgres+psycopg2://...' -> 'postgresql+psycopg://...'
    # Example: 'postgresql://...' -> 'postgresql+psycopg://...'
    
    # Standardize the protocol to 'postgresql' for consistency with SQLAlchemy 2.x conventions
    updated_url = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Remove any existing dialect (+psycopg2, +asyncpg) if present
    if "+" in updated_url:
        base_url = updated_url.split("://", 1)
        # Check if a dialect is specified (e.g., postgresql+psycopg2)
        if base_url[0].count('+') > 0:
            # Reconstruct the URL using only the base protocol and the new dialect
            protocol_prefix = base_url[0].split('+')[0]
            SQLALCHEMY_DATABASE_URL = f"{protocol_prefix}+psycopg://{base_url[1]}"
        else:
            # If it was just 'postgresql://', append the new dialect
            SQLALCHEMY_DATABASE_URL = f"{base_url[0]}+psycopg://{base_url[1]}"
    else:
         # Fallback if no specific protocol (should not happen with Aiven URL)
         SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
            
# SQLAlchemy Engine
# The Aiven SSL requirement (sslmode=require) is handled, and we now use the 'psycopg' driver.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True # Recommended for cloud databases
)

# Base for all models
Base = declarative_base()

# Local Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ---------------------------------------------------------------------


# Dependency to get the DB Session (for Flask/FastAPI)
def get_db():
    db = SessionLocal()
    try:
        # Flask/FastAPI will use this generator
        yield db
    finally:
        db.close()

# --- Utility DB SQLAlchemy Models (PostgreSQL compatible types) ---

class Consumer(Base):
    __tablename__ = "consumers"
    consumer_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    address = Column(String(255))
    balance = Column(Float, default=0.0)
    status = Column(String(20), default="ACTIVE")

class Meter(Base):
    __tablename__ = "meters"
    meter_id = Column(String(50), primary_key=True)
    consumer_id = Column(String(50), ForeignKey("consumers.consumer_id"))
    install_date = Column(DateTime)
    status = Column(String(20), default="PENDING_INSTALL")

class MeterReading(Base):
    __tablename__ = "meter_readings"
    id = Column(Integer, primary_key=True, index=True) 
    meter_id = Column(String(50), ForeignKey("meters.meter_id"))
    reading_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    kwh = Column(Float)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(String(50), ForeignKey("consumers.consumer_id"))
    amount = Column(Float)
    transaction_ref = Column(String(100), unique=True)
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)

class VendorApiKey(Base):
    __tablename__ = "vendor_api_keys"
    vendor_id = Column(String(20), primary_key=True)
    api_key_hash = Column(String(255))
    is_active = Column(Boolean, default=True)

class VendorAuditLog(Base):
    __tablename__ = "vendor_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(20))
    endpoint = Column(String(100))
    request_data = Column(String(2048)) 
    response_status = Column(Integer)
    log_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    
class MeterCommand(Base):
    """
    NEW: Tracks commands issued to meters (e.g., DISCONNECT, RECONNECT).
    Required by the /api/meter-command and /api/command-status endpoints.
    """
    __tablename__ = "meter_commands"
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), ForeignKey("meters.meter_id"))
    command_type = Column(String(50))
    status = Column(String(20), default="PENDING") # PENDING, SENT, SUCCESS, FAILED
    command_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    response_message = Column(String(255), nullable=True)


# --- Table Creation Logic ---
if __name__ == "__main__":
    # This block allows you to run 'python database.py' to initialize the database schema.
    # checkfirst=True ensures that tables are only created if they do not already exist.
    print("Attempting to create/verify database tables...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Database table creation/verification complete.")