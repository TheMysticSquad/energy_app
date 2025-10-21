# database.py - Updated for MySQL Connection
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------
# --- Configuration & Engine Initialization for MySQL ---
# ---------------------------------------------------------------------

# Retrieve the URL from the environment variable (now named 'DB' for MySQL)
DB_URL = os.getenv("DB")

# Ensure the URL was loaded successfully
if not DB_URL:
    raise ValueError("DB URL (environment variable 'DB') not found.")

# 🎯 CRITICAL FIX: Ensure the URL uses the correct MySQL dialect.
# We will use the 'mysql+mysqlconnector' dialect, which requires the
# 'mysql-connector-python' package.

if DB_URL.startswith("mysql://") and not DB_URL.startswith("mysql+mysqlconnector://"):
    # Replace generic 'mysql://' with the specific driver dialect
    DB_URL = DB_URL.replace("mysql://", "mysql+mysqlconnector://", 1)
    
# SQLAlchemy Engine
# The URL must be formatted as: mysql+mysqlconnector://user:password@host:port/dbname
engine = create_engine(
    DB_URL,
    pool_pre_ping=True, # Recommended for cloud databases
    # Optional: Set encoding for consistent character handling in MySQL
    # encoding='utf8' 
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

# --- Utility DB SQLAlchemy Models (Standard definitions for compatibility) ---
# NOTE: MySQL does not enforce column size restrictions as strictly as Postgres, 
# but these definitions are compatible.

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
    # Using String for ForeignKey reference, as MySQL treats it as VARCHAR
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
    Tracks commands issued to meters (e.g., DISCONNECT, RECONNECT).
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
    print("Attempting to create/verify MySQL database tables...")
    # NOTE: Be sure your database ('defaultdb' or whatever you're using) exists first.
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Database table creation/verification complete.")